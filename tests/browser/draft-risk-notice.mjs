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

const assertLayout = async (page, label) => {
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    `${label} must not overflow horizontally.`,
  );
  const clipped = await page.locator("h1, h2, p, li, .button").evaluateAll(
    (elements) =>
      elements
        .filter((element) => {
          if (!element.checkVisibility()) return false;
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
  await desktopPage.goto(`${baseUrl}/beginners-safety/`);
  const draftAction = desktopPage
    .locator(".risk-panel")
    .getByRole("link", {
      name: "Read the Draft Risk Notice",
      exact: true,
    });
  const panelAlignment = await draftAction.evaluate((element) => {
    const panel = element.closest(".risk-panel");
    const contentLeft =
      panel.getBoundingClientRect().left +
      Number.parseFloat(getComputedStyle(panel).borderLeftWidth) +
      Number.parseFloat(getComputedStyle(panel).paddingLeft);
    const paragraph = panel.querySelector("p").getBoundingClientRect();
    const action = element.getBoundingClientRect();
    return { offset: Math.abs(action.left - contentLeft), below: action.top >= paragraph.bottom };
  });
  assert.ok(
    panelAlignment.offset <= 1 && panelAlignment.below,
    `Draft Risk Notice action must sit left-aligned under the risk text: ${JSON.stringify(panelAlignment)}`,
  );
  await draftAction.focus();
  await desktopPage.keyboard.press("Enter");
  await desktopPage.waitForURL("**/risk-notice/");
  await desktopPage
    .getByRole("heading", { level: 1, name: "Draft Risk Notice" })
    .waitFor();
  assert.equal(
    await desktopPage.locator('meta[name="robots"]').getAttribute("content"),
    "noindex, nofollow",
  );
  assert.equal(
    await desktopPage
      .getByText("DRAFT — NOT APPROVED FOR PARTICIPATION USE", { exact: true })
      .isVisible(),
    true,
  );
  await assertLayout(desktopPage, "Desktop draft Risk Notice");
  await desktopContext.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(`${baseUrl}/risk-notice/`);
  await mobilePage
    .getByText(
      "By participating, you acknowledge that you have read and understood this risk notice. If you are unsure about your health or the risks of the activity, do not participate.",
      { exact: true },
    )
    .waitFor();
  await assertLayout(mobilePage, "Mobile draft Risk Notice");
  await mobileContext.close();

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
  await noJsPage.goto(`${baseUrl}/risk-notice/`);
  await noJsPage
    .getByRole("heading", { level: 1, name: "Draft Risk Notice" })
    .waitFor();
  assert.equal(
    await noJsPage
      .getByRole("link", { name: "Draft Risk Notice", exact: true })
      .isVisible(),
    true,
    "Draft navigation must remain visible without JavaScript.",
  );
  await assertLayout(noJsPage, "No-JavaScript draft Risk Notice");
  await noJsContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
