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

const pages = [
  {
    path: "/",
    heading: "Nonlinear Upper Limb Dynamics Laboratory",
    requiredText: [
      "1 December 2026",
      "3:00–7:00 pm",
      "Venue details to be confirmed",
    ],
  },
  {
    path: "/about/",
    heading: "About NULDL Armwrestling Club",
    requiredText: ["student-led, community-focused armwrestling club"],
  },
  {
    path: "/beginners-safety/",
    heading: "Beginners Are Welcome",
    requiredText: ["Armwrestling Involves Risk"],
  },
  {
    path: "/risk-notice/",
    heading: "Draft Risk Notice",
    requiredText: ["DRAFT — NOT APPROVED FOR PARTICIPATION USE"],
  },
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

    for (const pageDefinition of pages) {
      const response = await page.goto(`${baseUrl}${pageDefinition.path}`);
      assert.equal(response.status(), 200);
      await page
        .getByRole("heading", {
          name: pageDefinition.heading,
          exact: true,
        })
        .waitFor();
      for (const text of pageDefinition.requiredText) {
        await page.getByText(text, { exact: false }).first().waitFor();
      }
      await page
        .getByRole("link", {
          name: "Follow NULDL Armwrestling Club on Instagram: @nuldl_armwrestlingclub",
          exact: true,
        })
        .waitFor();
      const bodyText = await page.locator("body").innerText();
      assert.doesNotMatch(bodyText, /University of Sydney/i);
      assert.doesNotMatch(bodyText, /University (?:logo|crest)/i);
      await assertPageBounds(
        page,
        `${viewport.name} ${pageDefinition.heading}`,
      );
    }

    const sitemapResponse = await page.goto(`${baseUrl}/sitemap.xml`);
    assert.equal(sitemapResponse.status(), 200);
    const sitemap = await sitemapResponse.text();
    assert.match(sitemap, /<loc>[^<]*<\/loc>/);
    assert.doesNotMatch(sitemap, /risk-notice|accounts|admin/);

    assert.deepEqual(pageErrors, [], `${viewport.name} page errors detected.`);
    await context.close();
  }

  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
