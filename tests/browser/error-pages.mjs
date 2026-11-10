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
const errorPages = [
  ["/test-error/403/", 403, "Access Denied"],
  ["/test-error/missing/", 404, "Page Not Found"],
  ["/test-error/500/", 500, "Something Went Wrong"],
];

const assertLayoutAndFocus = async (page, label) => {
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    `${label} must not overflow horizontally.`,
  );
  const homeLink = page.getByRole("link", { name: "Return Home", exact: true });
  await homeLink.focus();
  assert.equal(await homeLink.evaluate((element) => element === document.activeElement), true);
  assert.equal(
    await page.evaluate(() =>
      Array.from(document.styleSheets).some((sheet) => sheet.href?.includes("/static/css/site.css")),
    ),
    true,
    `${label} must load the project CSS.`,
  );
};

try {
  for (const [path, expectedStatus, heading] of errorPages) {
    const desktopContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport: { width: 1440, height: 900 } },
      externalRequests,
    );
    const desktopPage = await desktopContext.newPage();
    desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
    const response = await desktopPage.goto(`${baseUrl}${path}`);
    assert.equal(response.status(), expectedStatus);
    await desktopPage.getByRole("heading", { level: 1, name: heading }).waitFor();
    await assertLayoutAndFocus(desktopPage, `Desktop ${expectedStatus} page`);
    await desktopContext.close();

    const mobileContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport: { width: 390, height: 844 } },
      externalRequests,
    );
    const mobilePage = await mobileContext.newPage();
    mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
    const mobileResponse = await mobilePage.goto(`${baseUrl}${path}`);
    assert.equal(mobileResponse.status(), expectedStatus);
    await mobilePage.getByRole("heading", { level: 1, name: heading }).waitFor();
    await assertLayoutAndFocus(mobilePage, `Mobile ${expectedStatus} page`);
    await mobileContext.close();
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
  const noJsResponse = await noJsPage.goto(`${baseUrl}/test-error/500/`);
  assert.equal(noJsResponse.status(), 500);
  await noJsPage
    .getByRole("heading", { level: 1, name: "Something Went Wrong" })
    .waitFor();
  assert.equal(
    await noJsPage.getByRole("link", { name: "Return Home", exact: true }).isVisible(),
    true,
    "The recovery link must remain visible without JavaScript.",
  );
  await assertLayoutAndFocus(noJsPage, "No-JavaScript 500 page");
  await noJsContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
