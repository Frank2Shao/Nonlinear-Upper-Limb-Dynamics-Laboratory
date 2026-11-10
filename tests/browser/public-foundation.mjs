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

try {
  const desktopContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1440, height: 900 } },
    externalRequests,
  );
  const desktopPage = await desktopContext.newPage();
  desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
  await desktopPage.goto(baseUrl);

  await desktopPage
    .getByRole("link", { name: "NULDL Armwrestling Club home" })
    .waitFor();
  const desktopNavigation = desktopPage.getByRole("navigation", {
    name: "Primary navigation",
  });
  assert.equal(await desktopPage.getByText("Menu", { exact: true }).isHidden(), true);
  await desktopNavigation.getByRole("link", { name: "Home", exact: true }).waitFor();
  await desktopNavigation.getByRole("link", { name: "Log in", exact: true }).waitFor();
  await desktopNavigation
    .getByRole("link", { name: "Join the Club", exact: true })
    .waitFor();
  assert.equal(
    await desktopPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    "Desktop navigation must not overflow the viewport.",
  );
  await desktopContext.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(baseUrl);
  await mobilePage.waitForFunction(() => Boolean(window.Alpine));

  const disclosure = mobilePage.locator("details.nav-disclosure");
  const toggle = mobilePage.locator("summary.nav-toggle");
  assert.equal(await disclosure.getAttribute("open"), null);
  assert.equal(
    await mobilePage.getByRole("link", { name: "Home", exact: true }).isHidden(),
    true,
  );

  await mobilePage.locator("body").focus();
  await mobilePage.keyboard.press("Tab");
  assert.equal(await mobilePage.locator(":focus").getAttribute("href"), "#main-content");
  await toggle.focus();
  const outlineStyle = await toggle.evaluate(
    (element) => getComputedStyle(element).outlineStyle,
  );
  assert.notEqual(outlineStyle, "none", "The menu toggle must expose visible focus.");
  await mobilePage.keyboard.press("Enter");
  assert.equal(await disclosure.getAttribute("open"), "");
  await mobilePage.getByRole("link", { name: "Home", exact: true }).waitFor();
  await mobilePage.keyboard.press("Space");
  assert.equal(await disclosure.getAttribute("open"), null);
  assert.equal(
    await mobilePage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    "Mobile navigation must not overflow the viewport.",
  );
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
  await noJsPage.goto(baseUrl);
  assert.equal(
    await noJsPage.getByRole("link", { name: "Log in", exact: true }).isVisible(),
    true,
    "Navigation links must remain visible when JavaScript is disabled.",
  );
  await noJsPage.getByRole("link", { name: "Log in", exact: true }).click();
  await noJsPage.waitForURL("**/accounts/login/");
  assert.equal(
    await noJsPage.getByRole("heading", { level: 1, name: "Log in" }).isVisible(),
    true,
    "Navigation links must work when JavaScript is disabled.",
  );
  await noJsContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
