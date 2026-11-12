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
  const membersLink = desktopPage.getByRole("link", { name: "Members", exact: true });
  assert.equal(await membersLink.getAttribute("aria-current"), "page");
  await membersLink.focus();
  assert.equal(
    await desktopPage.evaluate(() => document.activeElement?.textContent?.trim()),
    "Members",
    "Members navigation must be keyboard focusable.",
  );
  await desktopPage.getByRole("link", { name: "Alpha Member", exact: true }).click();
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
