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
  { name: "tablet", width: 808, height: 900 },
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

    const upcomingResponse = await page.goto(`${baseUrl}/events/`);
    assert.equal(upcomingResponse.status(), 200);
    await page.getByRole("heading", { name: "Events", exact: true }).waitFor();
    await page.getByRole("link", { name: "Upcoming", exact: true }).waitFor();
    await page.getByRole("link", { name: "Past", exact: true }).waitFor();
    if (viewport.width <= 960) {
      await page.waitForFunction(() => Boolean(window.Alpine));
      assert.equal(
        await page.locator("summary.nav-toggle").isVisible(),
        true,
      );
    }
    assert.equal(
      await page.getByRole("link", { name: "All", exact: true }).count(),
      0,
    );
    await assertPageBounds(page, `${viewport.name} Events upcoming`);

    const eventLinks = page.locator(".event-card h3 a");
    if ((await eventLinks.count()) > 0) {
      await eventLinks.first().click();
      assert.match(new URL(page.url()).pathname, /^\/events\/[^/]+\/$/);
      await page.getByRole("link", { name: "Back to events" }).waitFor();
      const registrationText = page.locator("#event-registration");
      await registrationText.waitFor();
      assert.match(
        await registrationText.innerText(),
        /Log in to register|Registration unavailable|Past event/,
      );
      assert.equal(
        await page.getByRole("button", { name: "Register", exact: true }).count(),
        0,
      );
      await assertPageBounds(page, `${viewport.name} Event detail`);
    } else {
      await page.getByText("No events found.", { exact: true }).waitFor();
    }

    const pastResponse = await page.goto(`${baseUrl}/events/?view=past`);
    assert.equal(pastResponse.status(), 200);
    assert.equal(
      await page
        .getByRole("link", { name: "Past", exact: true })
        .getAttribute("aria-current"),
      "page",
    );
    await assertPageBounds(page, `${viewport.name} Events past`);

    assert.deepEqual(pageErrors, [], `${viewport.name} page errors detected.`);
    await context.close();
  }

  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
