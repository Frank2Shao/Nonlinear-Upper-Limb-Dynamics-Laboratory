import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const externalRequests = [];
const pageErrors = [];
const browser = await chromium.launch({ headless: true });

const assertDirectory = async (page, label) => {
  await page.getByRole("heading", { level: 1, name: "Members" }).waitFor();
  const cards = page.locator(".member-card");
  assert.equal(await cards.count(), 2, `${label} must show both public profiles.`);
  assert.deepEqual(
    (await cards.getByRole("heading", { level: 2 }).allTextContents()).map((text) =>
      text.trim(),
    ),
    ["Alpha Member", "Bravo Member"],
    `${label} must preserve the public directory order.`,
  );
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    `${label} must not overflow horizontally.`,
  );
  const cardLayout = await cards.first().evaluate((card) => {
    const avatar = card.querySelector(".member-card__avatar, .member-card__avatar-fallback");
    const content = card.querySelector(".member-card__content");
    const avatarBounds = avatar.getBoundingClientRect();
    const contentBounds = content.getBoundingClientRect();
    return {
      avatarRight: avatarBounds.right,
      avatarWidth: avatarBounds.width,
      contentLeft: contentBounds.left,
    };
  });
  assert.ok(
    cardLayout.avatarRight <= cardLayout.contentLeft,
    `${label} must place the avatar to the left of member information.`,
  );
  assert.ok(
    cardLayout.avatarWidth <= 160,
    `${label} avatar must remain compact: ${JSON.stringify(cardLayout)}`,
  );
  const tagLayout = await cards.first().evaluate((card) => {
    const tag = card.querySelector(".member-card__tag");
    const heading = card.querySelector("h2");
    const tagBounds = tag.getBoundingClientRect();
    const headingBounds = heading.getBoundingClientRect();
    return {
      text: tag.textContent.trim(),
      tagBottom: tagBounds.bottom,
      tagLeft: tagBounds.left,
      headingTop: headingBounds.top,
      headingLeft: headingBounds.left,
    };
  });
  assert.equal(tagLayout.text, "Researcher 07", `${label} must show the assigned number.`);
  assert.ok(
    tagLayout.tagBottom <= tagLayout.headingTop &&
      Math.abs(tagLayout.tagLeft - tagLayout.headingLeft) <= 1,
    `${label} Researcher tag must sit directly above the name: ${JSON.stringify(tagLayout)}`,
  );
  assert.equal(
    await cards.nth(1).locator(".member-card__tag").count(),
    0,
    `${label} must not show a tag for a member without a number.`,
  );
};

const assertCardsShareARow = async (page) => {
  const [first, second] = await page
    .locator(".member-card")
    .evaluateAll((cards) => cards.map((card) => card.getBoundingClientRect().toJSON()));
  assert.ok(
    second.left >= first.right && Math.abs(second.top - first.top) <= 1,
    `Desktop cards must sit side by side: ${JSON.stringify([first, second])}`,
  );
};

const assertCardFocusRing = async (page) => {
  await page.getByRole("link", { name: "Alpha Member", exact: true }).focus();
  const outline = await page
    .locator(".member-card")
    .first()
    .evaluate((card) => getComputedStyle(card).outlineStyle);
  assert.notEqual(outline, "none", "Keyboard focus on a name must outline the whole card.");
};

try {
  const desktopContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1280, height: 900 } },
    externalRequests,
  );
  const desktopPage = await desktopContext.newPage();
  desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
  await desktopPage.goto(`${baseUrl}/members/`);
  await assertDirectory(desktopPage, "Desktop");
  await assertCardsShareARow(desktopPage);
  await assertCardFocusRing(desktopPage);
  const membersLink = desktopPage.getByRole("link", { name: "Members", exact: true });
  assert.equal(await membersLink.getAttribute("aria-current"), "page");
  await membersLink.focus();
  assert.equal(
    await desktopPage.evaluate(() => document.activeElement?.textContent?.trim()),
    "Members",
    "Members navigation must be keyboard focusable.",
  );
  // The whole card is the target: a click on its lower-right corner opens the profile.
  const firstCard = desktopPage.locator(".member-card").first();
  const cardBox = await firstCard.boundingBox();
  await firstCard.click({ position: { x: cardBox.width - 8, y: cardBox.height - 8 } });
  await desktopPage.getByRole("heading", { level: 1, name: "Alpha Member" }).waitFor();
  assert.equal(
    new URL(desktopPage.url()).pathname,
    "/members/browser-alpha/",
    "A member card must navigate to the stable Username detail URL.",
  );
  assert.equal(
    await desktopPage.locator('meta[name="robots"]').getAttribute("content"),
    "index, follow",
    "Member detail must use ordinary public robots rules.",
  );
  await desktopPage.getByText("Public bio for Alpha Member.").waitFor();
  const instagramLink = desktopPage.getByRole("link", {
    name: "Instagram: @browser_alpha.club",
  });
  assert.equal(await instagramLink.getAttribute("target"), "_blank");
  assert.equal(await instagramLink.getAttribute("rel"), "noopener noreferrer");
  assert.equal(
    await desktopPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    "Desktop member detail must not overflow horizontally.",
  );
  await desktopContext.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(`${baseUrl}/members/`);
  await mobilePage.locator("summary.nav-toggle").click();
  await assertDirectory(mobilePage, "Mobile");
  await mobilePage.goto(`${baseUrl}/members/browser-bravo/`);
  await mobilePage.getByRole("heading", { level: 1, name: "Bravo Member" }).waitFor();
  assert.equal(
    await mobilePage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    "Mobile member detail must not overflow horizontally.",
  );
  await mobileContext.close();

  const noJavaScriptContext = await createLocalContext(
    browser,
    baseUrl,
    { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const noJavaScriptPage = await noJavaScriptContext.newPage();
  await noJavaScriptPage.goto(`${baseUrl}/members/`);
  await assertDirectory(noJavaScriptPage, "No-JavaScript mobile");
  assert.equal(
    await noJavaScriptPage.getByRole("link", { name: "Members", exact: true }).isVisible(),
    true,
    "Members navigation must remain visible without JavaScript.",
  );
  await noJavaScriptPage
    .getByRole("link", { name: "Bravo Member", exact: true })
    .click();
  await noJavaScriptPage
    .getByRole("heading", { level: 1, name: "Bravo Member" })
    .waitFor();
  await noJavaScriptContext.close();

  assert.deepEqual(pageErrors, [], "Members directory must not raise browser errors.");
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
