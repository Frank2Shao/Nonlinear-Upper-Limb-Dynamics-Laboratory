import assert from "node:assert/strict";
import { chromium } from "@playwright/test";
import {
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
const browser = await chromium.launch({ headless: true });
const externalRequests = [];
const pageErrors = [];

try {
  for (const options of [
    { viewport: { width: 1440, height: 900 } },
    { viewport: { width: 390, height: 844 } },
    { viewport: { width: 390, height: 844 }, javaScriptEnabled: false },
  ]) {
    const context = await createLocalContext(browser, baseUrl, options, externalRequests);
    const page = await context.newPage();
    page.on("pageerror", (error) => pageErrors.push(error.message));
    await page.goto(baseUrl);
    const homeEventCard = page.locator(".event-stack .event-card").first();
    const viewAllEvents = page.getByRole("link", { name: "View all events" });
    const [cardBox, actionBox] = await Promise.all([
      homeEventCard.boundingBox(),
      viewAllEvents.boundingBox(),
    ]);
    assert.ok(cardBox && actionBox);
    assert.ok(
      cardBox.y - (actionBox.y + actionBox.height) >= 16,
      "View all events must sit in the section heading, clearly above the Event cards.",
    );
    await viewAllEvents.click();
    await assertPageStructure(page, `Events list ${JSON.stringify(options)}`);
    await assertNoHorizontalOverflow(page, `Events list ${JSON.stringify(options)}`);
    await assertVisibleContentFits(page, `Events list ${JSON.stringify(options)}`, VISIBLE_CONTENT);
    // The status is an unfilled label, as wide as the details action beside it.
    const aside = await page.locator(".event-card__aside").first().evaluate((element) => {
      const status = element.querySelector(".status-tag");
      const action = element.querySelector(".button");
      return {
        statusWidth: status.getBoundingClientRect().width,
        actionWidth: action.getBoundingClientRect().width,
        statusBackground: getComputedStyle(status).backgroundImage,
      };
    });
    assert.ok(Math.abs(aside.statusWidth - aside.actionWidth) < 1, JSON.stringify(aside));
    assert.equal(aside.statusBackground, "none");
    if (options.viewport.width === 390) {
      await assertTouchTargets(page, `Events list ${JSON.stringify(options)}`);
    } else {
      await assertFocusIndicator(
        page.getByRole("link", { name: "Upcoming", exact: true }),
        "Upcoming filter",
      );
    }
    await page.getByRole("link", { name: "Past", exact: true }).click();
    await page.getByText("No events found.").waitFor();
    await page.getByRole("link", { name: "Upcoming", exact: true }).click();
    await page.getByRole("link", { name: "Synthetic Training Session", exact: true }).click();
    await page.getByRole("heading", { name: "Synthetic Training Session", level: 1 }).waitFor();
    assert.equal(await page.getByRole("link", { name: "View location in map" }).getAttribute("href"), "https://maps.google.com/?q=synthetic");
    assert.equal(await page.locator("form").count(), 0);
    await assertPageStructure(page, `Event detail ${JSON.stringify(options)}`);
    await assertNoHorizontalOverflow(page, `Event detail ${JSON.stringify(options)}`);
    await assertVisibleContentFits(page, `Event detail ${JSON.stringify(options)}`, VISIBLE_CONTENT);
    await context.close();
  }

  const zoomContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 640, height: 900 } },
    externalRequests,
  );
  const zoomPage = await zoomContext.newPage();
  zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
  for (const path of ["/events/", "/events/synthetic-training/"]) {
    await zoomPage.goto(`${baseUrl}${path}`);
    await zoomPage.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    await assertNoHorizontalOverflow(zoomPage, `200% content zoom ${path}`);
    await assertVisibleContentFits(zoomPage, `200% content zoom ${path}`, VISIBLE_CONTENT);
  }
  await zoomContext.close();

  assert.deepEqual(pageErrors, []);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
