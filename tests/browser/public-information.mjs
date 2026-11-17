import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  assertNoHorizontalOverflow,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const externalRequests = [];
const pageErrors = [];
const browser = await chromium.launch({ headless: true });

const assertReadableElements = async (page, label) => {
  const clipped = await page.locator("h1, h2, p, li, .button").evaluateAll(
    (elements) =>
      elements
        .filter((element) => {
          if (!element.checkVisibility()) {
            return false;
          }
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
  assert.deepEqual(clipped, [], `${label} content must remain readable.`);
};

try {
  const desktopContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1440, height: 900 } },
    externalRequests,
  );
  const desktopPage = await desktopContext.newPage();
  desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
  await desktopPage.goto(`${baseUrl}/about/`);
  await desktopPage
    .getByRole("heading", { level: 1, name: "About NULDL Armwrestling Club" })
    .waitFor();
  const desktopNavigation = desktopPage.getByRole("navigation", {
    name: "Primary navigation",
  });
  assert.equal(
    await desktopNavigation
      .getByRole("link", { name: "About", exact: true })
      .getAttribute("aria-current"),
    "page",
  );
  const joinAction = desktopPage.getByRole("link", { name: "Join", exact: true });
  const joinMetrics = await joinAction.evaluate((element) => {
    const rectangle = element.getBoundingClientRect();
    const parentRectangle = element.parentElement.getBoundingClientRect();
    return {
      fontSize: Number.parseFloat(getComputedStyle(element).fontSize),
      height: rectangle.height,
      widthRatio: rectangle.width / parentRectangle.width,
      horizontalOffset: Math.abs(
        rectangle.left + rectangle.width / 2 -
          (parentRectangle.left + parentRectangle.width / 2),
      ),
      parentBorderWidth: getComputedStyle(element.parentElement).borderTopWidth,
    };
  });
  assert.ok(joinMetrics.fontSize >= 32, "About Join text must be doubled in size.");
  assert.ok(
    joinMetrics.height >= 74 && joinMetrics.height <= 76,
    `About Join button height must be reduced by approximately fifteen percent: ${JSON.stringify(joinMetrics)}`,
  );
  assert.ok(
    Math.abs(joinMetrics.widthRatio - 0.9) <= 0.01,
    "About Join button must fill ninety percent of the content width.",
  );
  assert.ok(joinMetrics.horizontalOffset <= 1, "About Join button must be centred.");
  assert.equal(
    joinMetrics.parentBorderWidth,
    "0px",
    "About Join wrapper must not have the former gold border.",
  );
  await desktopNavigation
    .getByRole("link", { name: "Beginners & Safety", exact: true })
    .focus();
  await desktopPage.keyboard.press("Enter");
  await desktopPage.waitForURL("**/beginners-safety/");
  await desktopPage
    .getByRole("heading", { level: 1, name: "Beginners Are Welcome" })
    .waitFor();
  await assertNoHorizontalOverflow(desktopPage, "Desktop public page");
  await assertReadableElements(desktopPage, "Desktop public page");
  await desktopContext.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(`${baseUrl}/about/`);
  await mobilePage.waitForFunction(() => Boolean(window.Alpine));
  const disclosure = mobilePage.locator("details.nav-disclosure");
  const toggle = mobilePage.locator("summary.nav-toggle");
  assert.equal(await disclosure.getAttribute("open"), null);
  await toggle.focus();
  await mobilePage.keyboard.press("Enter");
  assert.equal(await disclosure.getAttribute("open"), "");
  await mobilePage
    .getByRole("link", { name: "Beginners & Safety", exact: true })
    .focus();
  await mobilePage.keyboard.press("Enter");
  await mobilePage.waitForURL("**/beginners-safety/");
  await mobilePage
    .getByText("Stop immediately if you experience pain, numbness, dizziness or other discomfort.", {
      exact: true,
    })
    .waitFor();
  await mobilePage
    .getByText("Introductions to the session and equipment", { exact: true })
    .waitFor();
  await assertNoHorizontalOverflow(mobilePage, "Mobile public page");
  await assertReadableElements(mobilePage, "Mobile public page");
  await mobileContext.close();

  const zoomContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 640, height: 900 } },
    externalRequests,
  );
  const zoomPage = await zoomContext.newPage();
  zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
  await zoomPage.goto(`${baseUrl}/beginners-safety/`);
  await zoomPage.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
  await assertNoHorizontalOverflow(zoomPage, "Two-hundred-percent text zoom");
  await assertReadableElements(zoomPage, "Two-hundred-percent text zoom");
  await zoomContext.close();

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
  await noJsPage.goto(`${baseUrl}/beginners-safety/`);
  for (const text of [
    "Beginners Are Welcome",
    "What to Expect",
    "Armwrestling Involves Risk",
    "Before Participating",
    "During Training",
    "Shared Responsibility",
  ]) {
    await noJsPage.getByText(text, { exact: true }).waitFor();
  }
  assert.equal(
    await noJsPage
      .getByRole("link", { name: "About", exact: true })
      .isVisible(),
    true,
    "Public navigation must remain visible without JavaScript.",
  );
  await assertNoHorizontalOverflow(noJsPage, "No-JavaScript public page");
  await assertReadableElements(noJsPage, "No-JavaScript public page");
  await noJsContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
