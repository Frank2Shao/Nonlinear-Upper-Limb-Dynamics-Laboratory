import assert from "node:assert/strict";

import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  assertPageBounds,
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

    const membersResponse = await page.goto(`${baseUrl}/members/`);
    assert.equal(membersResponse.status(), 200);
    await page.getByRole("heading", { name: "Members", exact: true }).waitFor();
    await page.getByRole("navigation", { name: "Primary" }).waitFor();
    await assertPageBounds(page, `${viewport.name} Members`);

    const profileResponse = await page.goto(`${baseUrl}/profile/edit/`);
    assert.equal(profileResponse.status(), 200);
    assert.match(new URL(page.url()).pathname, /^\/accounts\/login\/$/);
    await page.getByRole("heading", { name: "Log in", exact: true }).waitFor();
    await assertPageBounds(page, `${viewport.name} Profile login redirect`);

    const missingMemberResponse = await page.goto(
      `${baseUrl}/members/synthetic-missing-member/`,
    );
    assert.equal(missingMemberResponse.status(), 404);
    await page.getByRole("heading", { name: "Page Not Found" }).waitFor();

    const missingMediaResponse = await page.goto(
      `${baseUrl}/media/avatars/synthetic-missing-avatar.png`,
    );
    assert.equal(missingMediaResponse.status(), 404);

    assert.deepEqual(pageErrors, [], `${viewport.name} page errors detected.`);
    await context.close();
  }

  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
