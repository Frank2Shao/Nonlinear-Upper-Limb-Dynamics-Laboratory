import assert from "node:assert/strict";
import { chromium } from "@playwright/test";
import {
  addSessionCookie,
  assertFocusIndicator,
  assertNoExternalRequests,
  assertNoHorizontalOverflow,
  assertPageStructure,
  assertTouchTargets,
  assertVisibleContentFits,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const VISIBLE_CONTENT = { selector: "h1, h2, h3, p, a, button, time" };
const jsSession = requireEnvironment("NULDL_JS_SESSION");
const noJsSession = requireEnvironment("NULDL_NOJS_SESSION");
const eventUrl = `${baseUrl}/events/synthetic-registration/`;
const browser = await chromium.launch({ headless: true });
const externalRequests = [];
const pageErrors = [];

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

// Design 7.3: after an HTMX update the replaced panel must take focus, so the
// new status is announced instead of focus falling back to <body>.
async function assertFocusOnStatus(page, label, expectedText) {
  await page.waitForFunction(
    () => document.activeElement?.closest("#event-registration") !== null,
  );
  const focused = await page.evaluate(() => ({
    role: document.activeElement.getAttribute("role"),
    tag: document.activeElement.tagName,
    text: document.activeElement.textContent.trim(),
  }));
  assert.equal(focused.text, expectedText, `${label}: ${JSON.stringify(focused)}`);
}

try {
  const context = await createLocalContext(browser, baseUrl, {}, externalRequests);
  await addSessionCookie(context, baseUrl, jsSession);
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(eventUrl);
  await assertPageStructure(page, "Desktop registration detail");
  await assertNoHorizontalOverflow(page, "Desktop registration detail");
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
  await assertFocusOnStatus(page, "After HTMX registration", "Registered");
  await page.getByRole("link", { name: "Cancel registration", exact: true }).click();
  const cancellationDialog = page.getByRole("dialog", { name: "Cancel registration" });
  await cancellationDialog.waitFor();
  await assertDialogCentered(cancellationDialog, "Cancel registration dialog");
  await cancellationDialog.getByRole("button", { name: "Confirm cancellation" }).click();
  await page.getByRole("link", { name: "Register", exact: true }).waitFor();
  await assertFocusOnStatus(page, "After HTMX cancellation", "Register");
  await page.getByRole("link", { name: "Register", exact: true }).click();
  const repeatDialog = page.getByRole("dialog", { name: "Confirm registration" });
  await repeatDialog.waitFor();
  await repeatDialog.getByText("Participation in armwrestling is voluntary.").waitFor();
  await repeatDialog.getByRole("button", { name: "Confirm registration" }).click();
  await page.getByText("Registered", { exact: true }).waitFor();
  await assertNoHorizontalOverflow(page, "Desktop re-registration detail");
  await context.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  await addSessionCookie(mobileContext, baseUrl, jsSession);
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(eventUrl);
  await assertPageStructure(mobilePage, "Mobile registration detail");
  await assertNoHorizontalOverflow(mobilePage, "Mobile registration detail");
  await assertVisibleContentFits(mobilePage, "Mobile registration detail", VISIBLE_CONTENT);
  await assertTouchTargets(mobilePage, "Mobile registration detail");
  await mobilePage.getByRole("link", { name: "Cancel registration", exact: true }).click();
  const mobileDialog = mobilePage.getByRole("dialog", { name: "Cancel registration" });
  await mobileDialog.waitFor();
  await assertDialogCentered(mobileDialog, "Mobile cancellation dialog");
  await assertNoHorizontalOverflow(mobilePage, "Mobile cancellation dialog");
  await assertVisibleContentFits(mobilePage, "Mobile cancellation dialog", VISIBLE_CONTENT);
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
  await addSessionCookie(zoomContext, baseUrl, jsSession);
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
    await assertNoHorizontalOverflow(zoomPage, `200% content zoom ${path}`);
    await assertVisibleContentFits(zoomPage, `200% content zoom ${path}`, VISIBLE_CONTENT);
  }
  await zoomContext.close();

  const noJsContext = await createLocalContext(
    browser,
    baseUrl,
    { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  await addSessionCookie(noJsContext, baseUrl, noJsSession);
  const noJsPage = await noJsContext.newPage();
  await noJsPage.goto(eventUrl);
  await assertPageStructure(noJsPage, "No-JavaScript registration detail");
  await assertNoHorizontalOverflow(noJsPage, "No-JavaScript registration detail");
  await assertTouchTargets(noJsPage, "No-JavaScript registration detail");
  await noJsPage.getByRole("link", { name: "Register", exact: true }).click();
  await noJsPage.getByRole("heading", { name: "Confirm registration", level: 1 }).waitFor();
  await noJsPage.getByText("By confirming my registration").waitFor();
  await assertPageStructure(noJsPage, "No-JavaScript registration confirmation");
  await assertNoHorizontalOverflow(noJsPage, "No-JavaScript registration confirmation");
  await assertTouchTargets(noJsPage, "No-JavaScript registration confirmation");
  await noJsPage.getByRole("button", { name: "Confirm registration" }).click();
  await noJsPage.getByText("Registered", { exact: true }).waitFor();
  await noJsPage.getByRole("link", { name: "Cancel registration", exact: true }).click();
  await noJsPage.getByRole("heading", { name: "Cancel registration", level: 1 }).waitFor();
  await assertPageStructure(noJsPage, "No-JavaScript cancellation confirmation");
  await assertNoHorizontalOverflow(noJsPage, "No-JavaScript cancellation confirmation");
  await assertTouchTargets(noJsPage, "No-JavaScript cancellation confirmation");
  await noJsPage.getByRole("button", { name: "Confirm cancellation" }).click();
  await noJsPage.getByRole("link", { name: "Register", exact: true }).waitFor();
  await assertNoHorizontalOverflow(noJsPage, "No-JavaScript cancelled detail");
  await noJsContext.close();

  assert.deepEqual(pageErrors, []);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
