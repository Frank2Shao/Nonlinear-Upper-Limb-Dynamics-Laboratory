import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const scenario = requireEnvironment("NULDL_BROWSER_SCENARIO");
const externalRequests = [];
const browser = await chromium.launch({ headless: true });

function required(name) {
  return requireEnvironment(name);
}

async function contextWithOptionalState() {
  const storageState = process.env.NULDL_STORAGE_STATE;
  const options = {
    viewport: { width: 1280, height: 900 },
  };
  if (storageState && scenario !== "signup" && scenario !== "magic-request") {
    options.storageState = storageState;
  }
  return createLocalContext(browser, baseUrl, options, externalRequests);
}

async function saveState(context) {
  await context.storageState({ path: required("NULDL_STORAGE_STATE") });
}

async function logOut(page) {
  await Promise.all([
    page.waitForURL(`${baseUrl}/`),
    page.getByRole("button", { name: "Log out" }).click(),
  ]);
  await page.getByRole("link", { name: "Log in" }).waitFor();
}

try {
  const context = await contextWithOptionalState();
  const page = await context.newPage();

  if (scenario === "signup") {
    await page.goto(`${baseUrl}/accounts/signup/`);
    await page.locator("#id_username").fill(required("NULDL_USERNAME"));
    await page.locator("#id_email").fill(required("NULDL_EMAIL"));
    await page.locator("#id_password1").fill(required("NULDL_PASSWORD"));
    await page.locator("#id_password2").fill(required("NULDL_PASSWORD"));
    await page.locator("#id_is_usyd_student").check();
    await page.locator("#id_usu_id").fill(required("NULDL_USU_ID"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/accounts/confirm-email/`),
      page.getByRole("button", { name: "Create account" }).click(),
    ]);
    await page.getByRole("heading", { name: "Verify your email" }).waitFor();
    await saveState(context);
  } else if (scenario === "verify-signup") {
    await page.goto(`${baseUrl}/accounts/confirm-email/`);
    await page.locator("#id_code").fill(required("NULDL_CODE"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/account/`),
      page.getByRole("button", { name: "Verify email" }).click(),
    ]);
    await page.getByRole("heading", { name: "Account", exact: true }).waitFor();
    await page.getByText(required("NULDL_USERNAME"), { exact: true }).waitFor();
    await page.getByText("Pending", { exact: true }).waitFor();
    await logOut(page);
  } else if (scenario === "password-login") {
    await page.goto(`${baseUrl}/accounts/login/`);
    await page.locator("#id_login").fill(required("NULDL_USERNAME"));
    await page.locator("#id_password").fill(required("NULDL_PASSWORD"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/account/`),
      page.getByRole("button", { name: "Log in", exact: true }).click(),
    ]);
    await page.locator("#id_is_usyd_student").check();
    await page.locator("#id_usu_id").fill(required("NULDL_USU_ID"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/account/`),
      page.getByRole("button", { name: "Update account" }).click(),
    ]);
    await page.getByText("Your account information has been updated.").waitFor();
    await logOut(page);
  } else if (scenario === "magic-request") {
    await page.goto(`${baseUrl}/accounts/login/code/`);
    await page.locator("#id_email").fill(required("NULDL_EMAIL"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/accounts/login/code/confirm/`),
      page.getByRole("button", { name: "Request code" }).click(),
    ]);
    await page.getByRole("heading", { name: "Enter your sign-in code" }).waitFor();
    await saveState(context);
  } else if (scenario === "magic-confirm") {
    await page.goto(`${baseUrl}/accounts/login/code/confirm/`);
    await page.locator("#id_code").fill(required("NULDL_CODE"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/account/`),
      page.getByRole("button", { name: "Confirm code" }).click(),
    ]);
    await page.getByRole("heading", { name: "Account", exact: true }).waitFor();
    await logOut(page);
  } else if (scenario === "admin-review") {
    const targetUserId = required("NULDL_TARGET_USER_ID");
    await page.goto(
      `${baseUrl}/admin/login/?next=/admin/accounts/user/`,
    );
    await page.locator("#id_username").fill(required("NULDL_USERNAME"));
    await page.locator("#id_password").fill(required("NULDL_PASSWORD"));
    await Promise.all([
      page.waitForURL(`${baseUrl}/admin/accounts/user/`),
      page.getByRole("button", { name: "Log in" }).click(),
    ]);
    await page.locator(`input.action-select[value="${targetUserId}"]`).check();
    await page.locator('select[name="action"]').selectOption("verify_usu_ids");
    await Promise.all([
      page.waitForURL(`${baseUrl}/admin/accounts/user/`),
      page.getByRole("button", { name: "Go" }).click(),
    ]);
    await page.getByText("Reviewed 1 USU ID submission(s).").waitFor();
  } else {
    throw new Error(`Unknown browser scenario: ${scenario}`);
  }

  await context.close();
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
