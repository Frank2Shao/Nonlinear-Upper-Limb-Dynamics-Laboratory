import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  addSessionCookie,
  assertFocusIndicator,
  assertNoExternalRequests,
  assertNoHorizontalOverflow,
  assertTouchTargets,
  assertVisibleContentFits,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const VISIBLE_CONTENT = { selector: "h1, h2, h3, p, li, dt, dd, a, button, label, img" };
const mode = process.env.NULDL_PHASE3_MODE || "full";
const externalRequests = [];
const pageErrors = [];
const browser = await chromium.launch({ headless: true });

const assertSemanticPage = async (page, label) => {
  const state = await page.evaluate(() => {
    const visible = (element) => element.checkVisibility();
    return {
      footers: document.querySelectorAll("body > footer").length,
      headers: document.querySelectorAll("body > header").length,
      h1Count: [...document.querySelectorAll("h1")].filter(visible).length,
      imagesWithoutAlt: [...document.querySelectorAll("img")]
        .filter(visible)
        .filter((image) => !image.getAttribute("alt")?.trim())
        .map((image) => image.outerHTML),
      mains: document.querySelectorAll("main#main-content").length,
      unnamedLinks: [...document.querySelectorAll("a")]
        .filter(visible)
        .filter((link) => !link.textContent?.trim() && !link.getAttribute("aria-label"))
        .map((link) => link.outerHTML),
    };
  });
  assert.equal(state.headers, 1, `${label} must contain one site header.`);
  assert.equal(state.mains, 1, `${label} must contain one main landmark.`);
  assert.equal(state.footers, 1, `${label} must contain one site footer.`);
  assert.equal(state.h1Count, 1, `${label} must contain one visible H1.`);
  assert.deepEqual(state.imagesWithoutAlt, [], `${label} contains images without alt text.`);
  assert.deepEqual(state.unnamedLinks, [], `${label} contains unnamed links.`);
};

const assertPage = async (page, path, label) => {
  const response = await page.goto(`${baseUrl}${path}`);
  assert.equal(response?.status(), 200, `${label} returned the wrong status.`);
  await page.locator("main#main-content h1").waitFor();
  await assertSemanticPage(page, label);
  await assertNoHorizontalOverflow(page, label);
  await assertVisibleContentFits(page, label, VISIBLE_CONTENT);
};

const assertEmptyDirectory = async (page, label) => {
  await assertPage(page, "/members/", label);
  await page
    .getByRole("heading", { level: 2, name: "No public member profiles yet" })
    .waitFor();
  assert.equal(await page.locator(".member-card").count(), 0);
};

try {
  if (mode === "empty") {
    for (const options of [
      { viewport: { width: 1440, height: 900 } },
      { viewport: { width: 390, height: 844 } },
      { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
    ]) {
      const context = await createLocalContext(browser, baseUrl, options, externalRequests);
      const page = await context.newPage();
      page.on("pageerror", (error) => pageErrors.push(error.message));
      await assertEmptyDirectory(page, `Empty directory ${JSON.stringify(options)}`);
      await context.close();
    }
  } else {
    const detailPath = requireEnvironment("NULDL_PHASE3_DETAIL_PATH");
    const ownerUsername = requireEnvironment("NULDL_PHASE3_OWNER_USERNAME");
    const privatePaths = [
      "/account/",
      "/profile/edit/",
      "/profile/preview/",
      "/profile/publish/",
      "/profile/unpublish/",
    ];
    const publicPaths = ["/members/", detailPath];

    const desktopContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport: { width: 1440, height: 900 } },
      externalRequests,
    );
    await addSessionCookie(desktopContext, baseUrl, requireEnvironment("NULDL_SESSION_COOKIE_VALUE"));
    const desktopPage = await desktopContext.newPage();
    desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
    for (const path of [...privatePaths, ...publicPaths]) {
      await assertPage(desktopPage, path, `Desktop ${path}`);
    }

    await desktopPage.goto(`${baseUrl}/account/`);
    await desktopPage
      .getByRole("heading", { level: 3, name: "Public member profile" })
      .waitFor();
    await desktopPage.getByText("Unavailable on public pages", { exact: true }).waitFor();
    await desktopPage.getByRole("link", { name: "Edit profile" }).waitFor();
    await desktopPage.getByRole("link", { name: "Preview profile" }).waitFor();
    await desktopPage.getByRole("link", { name: "Unpublish profile" }).waitFor();

    await desktopPage.goto(`${baseUrl}/profile/edit/`);
    const unlabelledControls = await desktopPage
      .locator("input:not([type=hidden]):not([type=submit]), select, textarea")
      .evaluateAll((controls) =>
        controls
          .filter((control) => control.checkVisibility())
          .filter((control) => control.labels?.length === 0)
          .map((control) => control.getAttribute("name")),
      );
    assert.deepEqual(unlabelledControls, [], "Profile edit controls must have labels.");
    const avatar = desktopPage.getByRole("img", {
      name: `Current avatar for ${ownerUsername}`,
    });
    await avatar.evaluate((image) => image.decode());
    assert.ok(await avatar.evaluate((image) => image.naturalWidth > 0));
    await assertFocusIndicator(
      desktopPage.getByRole("button", { name: "Save changes" }),
      "Save changes",
    );

    await desktopPage.locator("#id_other_social_url").fill("http://example.com/not-https");
    await desktopPage.getByRole("button", { name: "Save changes" }).click();
    const invalidSocial = desktopPage.locator("#id_other_social_url");
    assert.equal(await invalidSocial.getAttribute("aria-invalid"), "true");
    const socialErrorId = await invalidSocial.getAttribute("aria-describedby");
    assert.match(socialErrorId, /error/);
    const socialError = desktopPage.locator(`#${socialErrorId}`);
    await socialError.waitFor();
    assert.ok((await socialError.textContent()).trim(), "Invalid social URL must explain the error.");

    for (const path of ["/profile/preview/", "/profile/publish/", "/profile/unpublish/"]) {
      await desktopPage.goto(`${baseUrl}${path}`);
      await desktopPage
        .getByText("This profile is currently unavailable on public pages.", { exact: false })
        .waitFor();
    }
    await desktopPage.goto(`${baseUrl}/profile/preview/`);
    await desktopPage.getByText("UnbrokenOwnerBiography", { exact: false }).waitFor();
    await desktopPage.getByRole("link", { name: "Back to Account" }).waitFor();
    await assertNoHorizontalOverflow(desktopPage, "Desktop unbroken preview biography");
    await desktopPage.goto(`${baseUrl}${detailPath}`);
    await desktopPage.getByText("Long public biography", { exact: false }).waitFor();
    await desktopPage.getByText("UnbrokenPublicBiography", { exact: false }).waitFor();
    await assertNoHorizontalOverflow(desktopPage, "Desktop unbroken public biography");
    const socialLink = desktopPage.getByRole("link", { name: "Other social profile" });
    assert.equal(await socialLink.getAttribute("target"), "_blank");
    assert.equal(await socialLink.getAttribute("rel"), "noopener noreferrer");
    await desktopContext.close();

    const mobileContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport: { width: 390, height: 844 } },
      externalRequests,
    );
    await addSessionCookie(mobileContext, baseUrl, requireEnvironment("NULDL_SESSION_COOKIE_VALUE"));
    const mobilePage = await mobileContext.newPage();
    mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
    for (const path of [...privatePaths, ...publicPaths]) {
      await assertPage(mobilePage, path, `Mobile ${path}`);
      const disclosure = mobilePage.locator("details.nav-disclosure");
      if ((await disclosure.getAttribute("open")) === null) {
        await mobilePage.locator("summary.nav-toggle").click();
      }
      await assertTouchTargets(mobilePage, `Mobile ${path}`);
    }
    await mobilePage.goto(`${baseUrl}/profile/preview/`);
    await assertFocusIndicator(
      mobilePage.getByRole("link", { name: "Edit profile" }),
      "Edit profile",
    );
    await mobileContext.close();

    const zoomContext = await createLocalContext(
      browser,
      baseUrl,
      { viewport: { width: 640, height: 900 } },
      externalRequests,
    );
    await addSessionCookie(zoomContext, baseUrl, requireEnvironment("NULDL_SESSION_COOKIE_VALUE"));
    const zoomPage = await zoomContext.newPage();
    zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
    for (const path of [...privatePaths, ...publicPaths]) {
      await zoomPage.goto(`${baseUrl}${path}`);
      await zoomPage.evaluate(() => {
        document.documentElement.style.fontSize = "200%";
      });
      await assertNoHorizontalOverflow(zoomPage, `200% content zoom ${path}`);
      await assertVisibleContentFits(zoomPage, `200% content zoom ${path}`, VISIBLE_CONTENT);
    }
    await zoomContext.close();

    const noJavaScriptContext = await createLocalContext(
      browser,
      baseUrl,
      { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
      externalRequests,
    );
    await addSessionCookie(noJavaScriptContext, baseUrl, requireEnvironment("NULDL_SESSION_COOKIE_VALUE"));
    const noJavaScriptPage = await noJavaScriptContext.newPage();
    await noJavaScriptPage.goto(`${baseUrl}/profile/edit/`);
    await noJavaScriptPage.locator("#id_display_name").fill("No JavaScript Profile");
    await noJavaScriptPage.getByRole("button", { name: "Save changes" }).click();
    await noJavaScriptPage.getByText("Your profile has been updated.").waitFor();
    assert.equal(new URL(noJavaScriptPage.url()).pathname, "/account/");
    await noJavaScriptPage.goto(`${baseUrl}/profile/unpublish/`);
    await noJavaScriptPage.getByRole("button", { name: "Unpublish profile" }).click();
    await noJavaScriptPage.getByRole("link", { name: "Publish profile" }).waitFor();
    await noJavaScriptPage.goto(`${baseUrl}/profile/publish/`);
    await noJavaScriptPage.getByRole("button", { name: "Publish profile" }).click();
    await noJavaScriptPage.getByRole("link", { name: "Unpublish profile" }).waitFor();
    await noJavaScriptPage
      .getByText("This profile is currently unavailable on public pages.", { exact: false })
      .waitFor();
    await noJavaScriptContext.close();

    const reducedMotionContext = await createLocalContext(
      browser,
      baseUrl,
      { reducedMotion: "reduce", viewport: { width: 1440, height: 900 } },
      externalRequests,
    );
    await addSessionCookie(reducedMotionContext, baseUrl, requireEnvironment("NULDL_SESSION_COOKIE_VALUE"));
    const reducedMotionPage = await reducedMotionContext.newPage();
    reducedMotionPage.on("pageerror", (error) => pageErrors.push(error.message));
    await reducedMotionPage.goto(`${baseUrl}/profile/preview/`);
    const motion = await reducedMotionPage.locator(".button").first().evaluate((element) => ({
      mediaMatches: matchMedia("(prefers-reduced-motion: reduce)").matches,
      transitionDuration: getComputedStyle(element).transitionDuration,
    }));
    assert.equal(motion.mediaMatches, true);
    const reducedDurations = motion.transitionDuration.split(",").map((value) => value.trim());
    assert.ok(
      reducedDurations.every((value) =>
        value.endsWith("ms")
          ? Number.parseFloat(value) <= 0.01
          : value.endsWith("s") && Number.parseFloat(value) <= 0.00001,
      ),
      `Reduced-motion transition durations are too long: ${motion.transitionDuration}`,
    );
    await reducedMotionContext.close();
  }

  assert.deepEqual(pageErrors, [], `Phase 3 browser errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
