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

  const clippedElements = await page.locator("h1, h2, h3, .button").evaluateAll(
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
    .locator("#new-to-armwrestling .content-card h3")
    .evaluateAll((headings) =>
      headings.map((heading) => Number.parseFloat(getComputedStyle(heading).fontSize)),
    );
  assert.equal(cardHeadingSizes.length, 4);
  assert.equal(
    cardHeadingSizes.every((size) => size === 19),
    true,
    `${label} card titles must be three pixels larger than the base text.`,
  );
};

try {
  for (const [label, viewport] of [
    ["Desktop", { width: 1440, height: 900 }],
    ["Mobile", { width: 390, height: 844 }],
  ]) {
    const context = await createLocalContext(
      browser,
      baseUrl,
      { viewport },
      externalRequests,
    );
    const page = await context.newPage();
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto(baseUrl);

    await page
      .getByRole("heading", {
        level: 1,
        name: "Nonlinear Upper Limb Dynamics Laboratory",
      })
      .waitFor();
    await page.getByRole("heading", { level: 2, name: "Upcoming Session" }).waitFor();
    await assertHomeLayout(page, label);

    const primaryAction = page.locator("[data-home-primary]");
    assert.equal(await primaryAction.textContent(), "Join the Club");
    assert.equal(
      await page.locator("[data-session-join]").textContent(),
      "Join",
    );
    await page.getByText("Join Us !", { exact: true }).waitFor();
    assert.equal(await page.getByText("Open to New Participants").count(), 0);
    await primaryAction.click();
    await page.waitForURL("**/accounts/signup/");
    await context.close();
  }

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
    "Upcoming Session",
    "1 December 2026",
    "3:00–7:00 pm",
    "Training Session",
    "Venue details to be confirmed",
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
