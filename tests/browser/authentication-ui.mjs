import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const externalRequests = [];

const browser = await chromium.launch({ headless: true });

try {
  const context = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const page = await context.newPage();

  await page.goto(`${baseUrl}/accounts/signup/`);
  await page.waitForFunction(() => Boolean(window.Alpine));
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    "Signup must not overflow a 390px viewport.",
  );

  await page.locator("body").focus();
  await page.keyboard.press("Tab");
  assert.equal(
    await page.locator(":focus").getAttribute("href"),
    "#main-content",
    "The skip link must be the first keyboard target.",
  );

  const studentCheckbox = page.locator("#id_is_usyd_student");
  const usuId = page.locator("#id_usu_id");
  await assert.rejects(() => usuId.waitFor({ state: "visible", timeout: 250 }));
  await studentCheckbox.check();
  await usuId.waitFor({ state: "visible" });
  await usuId.fill("00112233");
  await studentCheckbox.uncheck();
  await usuId.waitFor({ state: "hidden" });
  assert.equal(await usuId.inputValue(), "", "Alpine must clear a hidden USU ID.");

  await page.locator("#id_username").fill("browser_pending");
  await page.locator("#id_email").fill("browser-pending@example.net");
  await page.locator("#id_password1").fill("A-valid-password-2026");
  await page.locator("#id_password2").fill("A-valid-password-2026");
  await Promise.all([
    page.waitForURL("**/accounts/confirm-email/"),
    page.getByRole("button", { name: "Create account" }).click(),
  ]);

  const verificationCode = page.locator("#id_code");
  assert.equal(await verificationCode.getAttribute("inputmode"), "numeric");
  await verificationCode.fill("123456789");
  assert.equal(
    await verificationCode.inputValue(),
    "123456789",
    "The complete verification code must be accepted in one input operation.",
  );
  await context.close();

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
  await noJsPage.goto(`${baseUrl}/accounts/signup/`);
  const noJsUsuId = noJsPage.locator("#id_usu_id");
  await noJsUsuId.waitFor({ state: "visible" });
  await noJsPage.locator("#id_username").fill("browser_no_js");
  await noJsPage.locator("#id_email").fill("browser-no-js@example.net");
  await noJsPage.locator("#id_password1").fill("A-valid-password-2026");
  await noJsPage.locator("#id_password2").fill("A-valid-password-2026");
  await noJsUsuId.fill("12345678");
  await noJsPage.getByRole("button", { name: "Create account" }).click();
  await noJsPage.getByText("USU ID is only available to USYD students.").waitFor();
  assert.equal(
    await noJsUsuId.isVisible(),
    true,
    "Server-side errors must remain visible without JavaScript.",
  );
  await noJsContext.close();

  const focusContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const focusPage = await focusContext.newPage();
  await focusPage.goto(`${baseUrl}/accounts/signup/`);
  await focusPage.waitForFunction(() => Boolean(window.Alpine));
  await focusPage.locator("#id_username").fill("browser_focus");
  await focusPage.locator("#id_email").fill("browser-focus@example.net");
  await focusPage.locator("#id_password1").fill("A-valid-password-2026");
  await focusPage.locator("#id_password2").fill("A-valid-password-2026");
  await focusPage.locator("#id_usu_id").evaluate((input) => {
    input.value = "12345678";
    input.form.noValidate = true;
    input.form.requestSubmit();
  });
  await focusPage.getByText("USU ID is only available to USYD students.").waitFor();
  await focusPage.waitForFunction(() => document.activeElement?.id === "id_usu_id");
  assert.equal(await focusPage.locator("#id_usu_id").isVisible(), true);
  await focusContext.close();
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
