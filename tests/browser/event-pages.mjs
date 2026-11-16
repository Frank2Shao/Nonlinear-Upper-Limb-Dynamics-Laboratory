import assert from "node:assert/strict";
import { chromium } from "@playwright/test";
import { assertNoExternalRequests, createLocalContext, requireEnvironment } from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const browser = await chromium.launch({ headless: true });
const externalRequests = [];
const pageErrors = [];

async function assertPageStructure(page, label) {
  const structure = await page.evaluate(() => ({
    footer: document.querySelectorAll("body > footer").length,
    h1: [...document.querySelectorAll("h1")].filter((element) =>
      element.checkVisibility(),
    ).length,
    header: document.querySelectorAll("body > header").length,
    main: document.querySelectorAll("main#main-content").length,
  }));
  assert.deepEqual(
    structure,
    { footer: 1, h1: 1, header: 1, main: 1 },
    `${label} has an invalid landmark or heading structure.`,
  );
}

async function assertNoOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  assert.ok(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label} has horizontal overflow: ${JSON.stringify(dimensions)}`,
  );
}

async function assertVisibleContentFits(page, label) {
  const clipped = await page
    .locator("h1, h2, h3, p, a, button, time")
    .evaluateAll((elements) =>
      elements
        .filter((element) => element.checkVisibility())
        .filter((element) => {
          const rectangle = element.getBoundingClientRect();
          return rectangle.left < -1 || rectangle.right > document.documentElement.clientWidth + 1;
        })
        .map((element) => element.textContent?.trim()),
    );
  assert.deepEqual(clipped, [], `${label} contains clipped visible content.`);
}

async function assertTouchTargets(page, label) {
  const undersized = await page
    .locator("a:not(.skip-link), button, summary")
    .evaluateAll((elements) =>
      elements
        .filter((element) => element.checkVisibility())
        .map((element) => {
          const rectangle = element.getBoundingClientRect();
          return {
            height: rectangle.height,
            name: element.textContent?.trim() || element.getAttribute("aria-label"),
            width: rectangle.width,
          };
        })
        .filter(({ height, width }) => height < 24 || width < 24),
    );
  assert.deepEqual(undersized, [], `${label} contains touch targets smaller than 24px.`);
}

async function assertFocusIndicator(locator, label) {
  await locator.focus();
  const focus = await locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      active: document.activeElement === element,
      outlineStyle: style.outlineStyle,
      outlineWidth: Number.parseFloat(style.outlineWidth),
    };
  });
  assert.equal(focus.active, true, `${label} must accept keyboard focus.`);
  assert.notEqual(focus.outlineStyle, "none", `${label} must expose a focus outline.`);
  assert.ok(focus.outlineWidth >= 2, `${label} focus outline must be clearly visible.`);
}

try {
  for (const options of [
    { viewport: { width: 1440, height: 900 } },
    { viewport: { width: 390, height: 844 } },
    { viewport: { width: 390, height: 844 }, javaScriptEnabled: false },
  ]) {
    const context = await createLocalContext(browser, baseUrl, options, externalRequests);
    const page = await context.newPage();
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto(baseUrl);
    const homeEventCard = page.locator(".session-card .event-card").last();
    const viewAllEvents = page.getByRole("link", { name: "View all events" });
    const [cardBox, actionBox] = await Promise.all([
      homeEventCard.boundingBox(),
      viewAllEvents.boundingBox(),
    ]);
    assert.ok(cardBox && actionBox);
    assert.ok(
      actionBox.y - (cardBox.y + cardBox.height) >= 20,
      "Home Event card and View all events must have visible spacing.",
    );
    await viewAllEvents.click();
    await assertPageStructure(page, `Events list ${JSON.stringify(options)}`);
    await assertNoOverflow(page, `Events list ${JSON.stringify(options)}`);
    await assertVisibleContentFits(page, `Events list ${JSON.stringify(options)}`);
    if (options.viewport.width === 390) {
      await assertTouchTargets(page, `Events list ${JSON.stringify(options)}`);
    } else {
      await assertFocusIndicator(
        page.getByRole("link", { name: "Upcoming", exact: true }),
        "Upcoming filter",
      );
    }
    await page.getByRole("link", { name: "Past", exact: true }).click();
    await page.getByText("No events found.").waitFor();
    await page.getByRole("link", { name: "Upcoming", exact: true }).click();
    await page.getByRole("link", { name: "Synthetic Training Session" }).click();
    await page.getByRole("heading", { name: "Synthetic Training Session", level: 1 }).waitFor();
    assert.equal(await page.getByRole("link", { name: "View location in map" }).getAttribute("href"), "https://maps.google.com/?q=synthetic");
    assert.equal(await page.locator("form").count(), 0);
    await assertPageStructure(page, `Event detail ${JSON.stringify(options)}`);
    await assertNoOverflow(page, `Event detail ${JSON.stringify(options)}`);
    await assertVisibleContentFits(page, `Event detail ${JSON.stringify(options)}`);
    await context.close();
  }

  const zoomContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 640, height: 900 } },
    externalRequests,
  );
  const zoomPage = await zoomContext.newPage();
  zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
  for (const path of ["/events/", "/events/synthetic-training/"]) {
    await zoomPage.goto(`${baseUrl}${path}`);
    await zoomPage.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    await assertNoOverflow(zoomPage, `200% content zoom ${path}`);
    await assertVisibleContentFits(zoomPage, `200% content zoom ${path}`);
  }
  await zoomContext.close();

  assert.deepEqual(pageErrors, []);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
