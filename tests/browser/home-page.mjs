import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const externalRequests = [];
const pageErrors = [];
const browser = await chromium.launch({ headless: true });
const isSpecimenPhoto = (url) => new URL(url).pathname.includes("/images/home/hero-specimen-");

// The background easter egg: a faint photo that a pointer-following light
// reveals, without blocking the Hero actions.
const assertSpecimenLight = async (page, specimenRequests) => {
  const layer = page.locator(".hero-specimen");
  const lights = page.locator(".hero-specimen__light");
  assert.equal(await lights.count(), 1);
  assert.equal(await layer.getAttribute("aria-hidden"), "true");
  assert.deepEqual(
    await layer.evaluate((element) => {
      const style = getComputedStyle(element);
      return [style.display, style.pointerEvents];
    }),
    ["block", "none"],
  );
  assert.ok(specimenRequests.length > 0, "Desktop Hero must load the specimen photo.");
  const opacities = () =>
    lights.evaluateAll((elements) => elements.map((element) => getComputedStyle(element).opacity));
  assert.deepEqual(await opacities(), ["0"], "The light must be off until the pointer enters.");

  const figure = await page.locator(".hero-specimen__figure--dim").boundingBox();
  const hero = await page.locator(".home-hero").boundingBox();
  const pointer = { x: figure.x + figure.width * 0.57, y: figure.y + figure.height * 0.43 };
  await page.mouse.move(pointer.x, pointer.y);
  await page.waitForFunction(
    () =>
      [...document.querySelectorAll(".hero-specimen__light")].every(
        (element) => getComputedStyle(element).opacity === "1",
      ),
  );
  const position = await page.locator(".home-hero").evaluate((element) => [
    element.style.getPropertyValue("--light-x"),
    element.style.getPropertyValue("--light-y"),
  ]);
  assert.deepEqual(
    position.map((value) => Math.round(Number.parseFloat(value))),
    [Math.round(pointer.x - hero.x), Math.round(pointer.y - hero.y)],
    "The light must follow the pointer.",
  );

  const blocked = await page.locator(".home-hero__actions a").evaluateAll((links) =>
    links
      .filter((link) => {
        const box = link.getBoundingClientRect();
        const hit = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
        return !link.contains(hit);
      })
      .map((link) => link.textContent.trim()),
  );
  assert.deepEqual(blocked, [], "The specimen layer must not block the Hero actions.");

  await page.mouse.move(hero.x + hero.width / 2, hero.y + hero.height + 40);
  await page.waitForFunction(
    () =>
      [...document.querySelectorAll(".hero-specimen__light")].every(
        (element) => getComputedStyle(element).opacity === "0",
      ),
  );
};

const assertHomeLayout = async (page, label) => {
  const logo = page.locator(".home-hero__logo");
  await logo.waitFor();
  const logoState = await logo.evaluate((image) => ({
    complete: image.complete,
    naturalWidth: image.naturalWidth,
    naturalHeight: image.naturalHeight,
    renderedWidth: image.getBoundingClientRect().width,
    renderedHeight: image.getBoundingClientRect().height,
  }));
  assert.equal(logoState.complete, true, `${label} logo must finish loading.`);
  assert.ok(logoState.naturalWidth > 0, `${label} logo must load successfully.`);
  assert.equal(
    logoState.naturalWidth / logoState.naturalHeight,
    1,
    `${label} logo source must remain square.`,
  );
  assert.ok(
    Math.abs(logoState.renderedWidth / logoState.renderedHeight - 1) < 0.01,
    `${label} logo must not be distorted.`,
  );

  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    `${label} Home must not overflow horizontally.`,
  );

  const clippedElements = await page.locator("main :is(h1, h2, h3, .button)").evaluateAll(
    (elements) =>
      elements
        .filter((element) => {
          const rectangle = element.getBoundingClientRect();
          return (
            rectangle.width <= 0 ||
            rectangle.height <= 0 ||
            rectangle.left < -1 ||
            rectangle.right > innerWidth + 1
          );
        })
        .map((element) => element.textContent.trim()),
  );
  assert.deepEqual(clippedElements, [], `${label} text and actions must remain visible.`);

  const cardHeadingSizes = await page
    .locator("#new-to-armwrestling .feature-card h3")
    .evaluateAll((headings) =>
      headings.map((heading) => Number.parseFloat(getComputedStyle(heading).fontSize)),
    );
  assert.equal(cardHeadingSizes.length, 4);
  assert.equal(
    cardHeadingSizes.every((size) => size === 22),
    true,
    `${label} feature card titles must use the approved 1.375rem size.`,
  );
};

try {
  for (const [label, viewport] of [
    ["Desktop", { width: 1920, height: 1080 }],
    ["Mobile", { width: 390, height: 844 }],
  ]) {
    const context = await createLocalContext(
      browser,
      baseUrl,
      { viewport },
      externalRequests,
    );
    const page = await context.newPage();
    const specimenRequests = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("request", (request) => {
      if (isSpecimenPhoto(request.url())) specimenRequests.push(request.url());
    });
    await page.goto(baseUrl, { waitUntil: "networkidle" });

    await page
      .getByRole("heading", {
        level: 1,
        name: "Nonlinear Upper Limb Dynamics Laboratory",
      })
      .waitFor();
    await page.getByRole("heading", { level: 2, name: "Upcoming Events" }).waitFor();
    await assertHomeLayout(page, label);

    const primaryAction = page.locator("[data-home-primary]");
    const actions = page.locator(".home-hero__actions a");
    assert.deepEqual(await actions.allTextContents(), [
      "Join the Club",
      "Join on USU",
      "New to Armwrestling?",
    ]);
    assert.equal(
      await actions.nth(1).getAttribute("href"),
      "https://usu.edu.au/clubs/armwrestling/",
    );
    const [signup, usu, beginners] = await actions.evaluateAll((links) =>
      links.map((link) => link.getBoundingClientRect().toJSON()),
    );
    assert.equal(signup.top, usu.top);
    assert.ok(signup.right < usu.left);
    const hero = await page.evaluate(() => {
      const box = (element) => element.getBoundingClientRect().toJSON();
      return {
        content: box(document.querySelector(".home-hero__content")),
        logo: box(document.querySelector(".home-hero__logo")),
        lines: [...document.querySelectorAll(".home-hero__title-line")].map(box),
        titleBlock: document.querySelector(".drawing-block").checkVisibility(),
      };
    });
    assert.equal(hero.titleBlock, true, `${label} Hero must show the drawing title block.`);
    if (label === "Mobile") {
      assert.ok(beginners.top > signup.bottom);
      assert.equal(beginners.left, signup.left);
      assert.ok(hero.logo.top >= hero.content.bottom, "Mobile logo must sit below the title.");
      assert.equal(await page.locator(".hero-specimen").isVisible(), false);
      assert.deepEqual(specimenRequests, [], "Mobile must not download the specimen photo.");
    } else {
      assert.equal(beginners.top, signup.top);
      assert.ok(
        [usu, beginners].every((action) => Math.abs(action.width - signup.width) < 1),
        "Desktop Hero actions must share one row at equal widths.",
      );
      assert.ok(
        [usu, beginners].every((action) => Math.abs(action.height - signup.height) < 1),
        "Desktop Hero actions must share one height.",
      );
      assert.equal(hero.lines.length, 3);
      assert.ok(
        hero.lines[0].bottom <= hero.lines[1].top + 1 && hero.lines[1].bottom <= hero.lines[2].top + 1,
        "Desktop Hero title must stay on three separate lines.",
      );
      // The second title line is the widest and sets the column width.
      assert.ok(Math.abs(hero.lines[1].width - hero.content.width) < 1);
      assert.ok(hero.logo.left > hero.content.right, "Desktop logo must sit beside the title.");
      assert.ok(hero.logo.width >= 300 && hero.logo.width <= 500);
      await assertSpecimenLight(page, specimenRequests);
      for (const selector of [".site-nav", ".page-shell", ".site-footer__inner"]) {
        const box = await page.locator(selector).boundingBox();
        assert.equal(box.width, 80 * 16, `${selector} should share the 80rem content width.`);
      }
    }
    await page.getByRole("link", { name: "View all events" }).waitFor();
    await page.getByText("Join Us !", { exact: true }).waitFor();
    assert.equal(await page.getByText("Open to New Participants").count(), 0);
    await primaryAction.click();
    await page.waitForURL("**/accounts/signup/");
    await context.close();
  }

  // A wide touch screen cannot hover, so it gets neither the layer nor the photo.
  const touchContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1280, height: 800 }, hasTouch: true, isMobile: true },
    externalRequests,
  );
  const touchPage = await touchContext.newPage();
  const touchRequests = [];
  touchPage.on("request", (request) => {
    if (isSpecimenPhoto(request.url())) touchRequests.push(request.url());
  });
  await touchPage.goto(baseUrl, { waitUntil: "networkidle" });
  assert.equal(await touchPage.evaluate(() => matchMedia("(hover: hover)").matches), false);
  assert.equal(await touchPage.locator(".hero-specimen").isVisible(), false);
  assert.deepEqual(touchRequests, [], "Touch screens must not download the specimen photo.");
  await touchContext.close();

  const noJsContext = await createLocalContext(
    browser,
    baseUrl,
    {
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    },
    externalRequests,
  );
  const noJsPage = await noJsContext.newPage();
  await noJsPage.goto(baseUrl);
  for (const text of [
    "New to Armwrestling?",
    "Join Us !",
    "Upcoming Events",
    "No upcoming events are currently available.",
  ]) {
    await noJsPage.getByText(text, { exact: true }).first().waitFor();
  }
  await assertHomeLayout(noJsPage, "No-JavaScript mobile");
  await noJsPage
    .getByRole("link", { name: "New to Armwrestling?", exact: true })
    .click();
  assert.equal(new URL(noJsPage.url()).hash, "#new-to-armwrestling");
  await noJsContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
