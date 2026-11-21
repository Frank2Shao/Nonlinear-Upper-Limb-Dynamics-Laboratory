import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  INTERACTIVE_TARGETS,
  assertNoExternalRequests,
  assertNoHorizontalOverflow,
  assertTouchTargets,
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

  // Access page layout (design_document.md 7.11): heading beside the framed
  // panel on wide screens, above it on phones; mono labels without colons;
  // checkboxes before their labels; the main action spans the panel.
  for (const [device, viewport] of [
    ["desktop", { width: 1440, height: 900 }],
    ["mobile", { width: 390, height: 844 }],
  ]) {
    const layoutContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport },
      externalRequests,
    );
    const layoutPage = await layoutContext.newPage();
    for (const path of [
      "/accounts/login/",
      "/accounts/signup/",
      "/accounts/login/code/",
      "/accounts/password/reset/",
    ]) {
      await layoutPage.goto(`${baseUrl}${path}`);
      const label = `${device} ${path}`;
      await assertNoHorizontalOverflow(layoutPage, label);
      await assertTouchTargets(layoutPage, label, `main :is(${INTERACTIVE_TARGETS})`);
      const layout = await layoutPage.evaluate(() => {
        const box = (element) => element.getBoundingClientRect().toJSON();
        const panel = document.querySelector(".access-panel");
        const form = panel.querySelector("form");
        return {
          heading: box(document.querySelector(".access-page .page-heading")),
          panel: box(panel),
          form: box(form),
          submit: box(form.querySelector(":scope > button[type=submit]")),
          labels: [...document.querySelectorAll("main .field label")].map((element) => ({
            text: element.textContent.trim(),
            font: getComputedStyle(element).fontFamily,
            transform: getComputedStyle(element).textTransform,
          })),
        };
      });
      if (device === "desktop") {
        assert.ok(
          layout.panel.left >= layout.heading.right,
          `${label}: the panel must sit to the right of the heading.`,
        );
        assert.ok(layout.panel.width <= 481, `${label}: the panel must be at most 30rem wide.`);
      } else {
        assert.ok(
          layout.panel.top >= layout.heading.bottom,
          `${label}: the panel must sit below the heading on phones.`,
        );
      }
      assert.ok(
        Math.abs(layout.submit.width - layout.form.width) <= 1,
        `${label}: the main action must span the panel.`,
      );
      assert.ok(layout.labels.length > 0, `${label}: the form must have labels.`);
      for (const { text, font, transform } of layout.labels) {
        assert.ok(!text.endsWith(":"), `${label}: "${text}" must not end with a colon.`);
        assert.match(font, /JetBrains Mono/, `${label}: labels use the mono face.`);
        assert.equal(transform, "uppercase", `${label}: labels are uppercase.`);
      }
    }

    await layoutPage.goto(`${baseUrl}/accounts/login/`);
    const checkbox = await layoutPage.evaluate(() => {
      const input = document.querySelector("#id_remember").getBoundingClientRect();
      const text = document.querySelector('label[for="id_remember"]').getBoundingClientRect();
      return {
        before: input.right <= text.left,
        sameLine: Math.abs(input.top + input.height / 2 - (text.top + text.height / 2)) <= 4,
      };
    });
    assert.deepEqual(
      checkbox,
      { before: true, sameLine: true },
      `${device}: the checkbox must sit before its label on one line.`,
    );
    const alternative = layoutPage
      .locator(".access-panel__alt")
      .getByRole("link", { name: "Log in by email code" });
    const [alternativeBox, panelForm] = await Promise.all([
      alternative.boundingBox(),
      layoutPage.locator(".access-panel form").boundingBox(),
    ]);
    assert.ok(
      Math.abs(alternativeBox.width - panelForm.width) <= 1,
      `${device}: "Log in by email code" must span the panel below the hairline.`,
    );
    await layoutContext.close();
  }

  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
