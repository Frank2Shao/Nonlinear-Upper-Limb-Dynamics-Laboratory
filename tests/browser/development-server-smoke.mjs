import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const browser = await chromium.launch({ headless: true });
const externalRequests = [];
const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

async function assertPageBounds(page, label) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    styleSheets: document.styleSheets.length,
  }));
  assert.ok(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label} has horizontal overflow: ${JSON.stringify(dimensions)}`,
  );
  assert.ok(dimensions.styleSheets > 0, `${label} did not load project CSS.`);
}

try {
  for (const viewport of viewports) {
    const context = await createLocalContext(
      browser,
      baseUrl,
      { viewport },
      externalRequests,
    );
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    let response = await page.goto(`${baseUrl}/`);
    assert.equal(response.status(), 200);
    await page
      .getByRole("heading", {
        name: "Nonlinear Upper Limb Dynamics Laboratory",
        exact: true,
      })
      .waitFor();
    await assertPageBounds(page, `${viewport.name} Home`);

    response = await page.goto(`${baseUrl}/accounts/signup/`);
    assert.equal(response.status(), 200);
    await page
      .getByRole("heading", { name: "Join the Club", exact: true })
      .waitFor();
    await assertPageBounds(page, `${viewport.name} Signup`);

    response = await page.goto(`${baseUrl}/accounts/login/`);
    assert.equal(response.status(), 200);
    await page
      .getByRole("heading", { name: "Log in", exact: true })
      .waitFor();
    await assertPageBounds(page, `${viewport.name} Login`);

    await page.goto(`${baseUrl}/account/`);
    await page.waitForURL(`${baseUrl}/accounts/login/?next=/account/`);
    await page
      .getByRole("heading", { name: "Log in", exact: true })
      .waitFor();

    const bodyText = await page.locator("body").innerText();
    assert.doesNotMatch(bodyText, /University of Sydney/i);
    assert.doesNotMatch(bodyText, /University (?:logo|crest)/i);
    assert.deepEqual(pageErrors, [], `${viewport.name} page errors detected.`);
    await context.close();
  }

  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
