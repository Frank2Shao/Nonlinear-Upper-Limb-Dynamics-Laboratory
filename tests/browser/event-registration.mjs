import assert from "node:assert/strict";
import { chromium } from "@playwright/test";
import { assertNoExternalRequests, createLocalContext, requireEnvironment } from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const cookieName = requireEnvironment("NULDL_SESSION_COOKIE_NAME");
const jsSession = requireEnvironment("NULDL_JS_SESSION");
const noJsSession = requireEnvironment("NULDL_NOJS_SESSION");
const eventUrl = `${baseUrl}/events/synthetic-registration/`;
const browser = await chromium.launch({ headless: true });
const externalRequests = [];
const pageErrors = [];

async function addSession(context, value) {
  await context.addCookies([{ name: cookieName, value, url: baseUrl }]);
}

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

async function assertDialogCentered(dialog, label) {
  const geometry = await dialog.evaluate((element) => {
    const rectangle = element.getBoundingClientRect();
    return {
      dialogX: rectangle.left + rectangle.width / 2,
      dialogY: rectangle.top + rectangle.height / 2,
      viewportX: window.innerWidth / 2,
      viewportY: window.innerHeight / 2,
    };
  });
  assert.ok(
    Math.abs(geometry.dialogX - geometry.viewportX) <= 2,
    `${label} must be horizontally centred: ${JSON.stringify(geometry)}`,
  );
  assert.ok(
    Math.abs(geometry.dialogY - geometry.viewportY) <= 2,
    `${label} must be vertically centred: ${JSON.stringify(geometry)}`,
  );
}

try {
  const context = await createLocalContext(browser, baseUrl, {}, externalRequests);
  await addSession(context, jsSession);
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(eventUrl);
  await assertPageStructure(page, "Desktop registration detail");
  await assertNoOverflow(page, "Desktop registration detail");
  await assertFocusIndicator(
    page.getByRole("link", { name: "Register", exact: true }),
    "Register link",
  );
  await page.getByRole("link", { name: "Register", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Confirm registration" });
  await dialog.waitFor();
  await assertDialogCentered(dialog, "Confirm registration dialog");
  await dialog.getByText("Participation in armwrestling is voluntary.").waitFor();
  await assertFocusIndicator(
    dialog.getByRole("button", { name: "Confirm registration" }),
    "Confirm registration button",
  );
  await dialog.getByRole("button", { name: "Confirm registration" }).click();
  await page.getByText("Registered", { exact: true }).waitFor();
  assert.equal(await page.getByRole("dialog").count(), 0);
  await page.getByRole("link", { name: "Cancel registration", exact: true }).click();
  const cancellationDialog = page.getByRole("dialog", { name: "Cancel registration" });
  await cancellationDialog.waitFor();
  await assertDialogCentered(cancellationDialog, "Cancel registration dialog");
  await cancellationDialog.getByRole("button", { name: "Confirm cancellation" }).click();
  await page.getByRole("link", { name: "Register", exact: true }).waitFor();
  await page.getByRole("link", { name: "Register", exact: true }).click();
  const repeatDialog = page.getByRole("dialog", { name: "Confirm registration" });
  await repeatDialog.waitFor();
  await repeatDialog.getByText("Participation in armwrestling is voluntary.").waitFor();
  await repeatDialog.getByRole("button", { name: "Confirm registration" }).click();
  await page.getByText("Registered", { exact: true }).waitFor();
  await assertNoOverflow(page, "Desktop re-registration detail");
  await context.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  await addSession(mobileContext, jsSession);
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(eventUrl);
  await assertPageStructure(mobilePage, "Mobile registration detail");
  await assertNoOverflow(mobilePage, "Mobile registration detail");
  await assertVisibleContentFits(mobilePage, "Mobile registration detail");
  await assertTouchTargets(mobilePage, "Mobile registration detail");
  await mobilePage.getByRole("link", { name: "Cancel registration", exact: true }).click();
  const mobileDialog = mobilePage.getByRole("dialog", { name: "Cancel registration" });
  await mobileDialog.waitFor();
  await assertDialogCentered(mobileDialog, "Mobile cancellation dialog");
  await assertNoOverflow(mobilePage, "Mobile cancellation dialog");
  await assertVisibleContentFits(mobilePage, "Mobile cancellation dialog");
  await assertTouchTargets(mobileDialog, "Mobile cancellation dialog");
  await mobileDialog.getByRole("button", { name: "Keep registration" }).click();
  await mobileDialog.waitFor({ state: "hidden" });
  await mobileContext.close();

  const zoomContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 640, height: 900 } },
    externalRequests,
  );
  await addSession(zoomContext, jsSession);
  const zoomPage = await zoomContext.newPage();
  zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
  for (const path of [
    "/events/synthetic-registration/",
    "/events/synthetic-registration/cancel/",
  ]) {
    await zoomPage.goto(`${baseUrl}${path}`);
    await zoomPage.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    await assertNoOverflow(zoomPage, `200% content zoom ${path}`);
    await assertVisibleContentFits(zoomPage, `200% content zoom ${path}`);
  }
  await zoomContext.close();

  const noJsContext = await createLocalContext(
    browser,
    baseUrl,
    { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  await addSession(noJsContext, noJsSession);
  const noJsPage = await noJsContext.newPage();
  await noJsPage.goto(eventUrl);
  await assertPageStructure(noJsPage, "No-JavaScript registration detail");
  await assertNoOverflow(noJsPage, "No-JavaScript registration detail");
  await assertTouchTargets(noJsPage, "No-JavaScript registration detail");
  await noJsPage.getByRole("link", { name: "Register", exact: true }).click();
  await noJsPage.getByRole("heading", { name: "Confirm registration", level: 1 }).waitFor();
  await noJsPage.getByText("By confirming my registration").waitFor();
  await assertPageStructure(noJsPage, "No-JavaScript registration confirmation");
  await assertNoOverflow(noJsPage, "No-JavaScript registration confirmation");
  await assertTouchTargets(noJsPage, "No-JavaScript registration confirmation");
  await noJsPage.getByRole("button", { name: "Confirm registration" }).click();
  await noJsPage.getByText("Registered", { exact: true }).waitFor();
  await noJsPage.getByRole("link", { name: "Cancel registration", exact: true }).click();
  await noJsPage.getByRole("heading", { name: "Cancel registration", level: 1 }).waitFor();
  await assertPageStructure(noJsPage, "No-JavaScript cancellation confirmation");
  await assertNoOverflow(noJsPage, "No-JavaScript cancellation confirmation");
  await assertTouchTargets(noJsPage, "No-JavaScript cancellation confirmation");
  await noJsPage.getByRole("button", { name: "Confirm cancellation" }).click();
  await noJsPage.getByRole("link", { name: "Register", exact: true }).waitFor();
  await assertNoOverflow(noJsPage, "No-JavaScript cancelled detail");
  await noJsContext.close();

  assert.deepEqual(pageErrors, []);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
