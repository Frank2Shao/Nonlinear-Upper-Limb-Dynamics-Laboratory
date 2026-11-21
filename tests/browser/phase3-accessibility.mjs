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

// Account (design_document.md 7.11): drawing-table rows put the label beside
// the value on wide screens and above it on phones; the avatar sits beside the
// summary; settings buttons keep their own width on wide screens.
const accountLayout = (page) =>
  page.evaluate(() => {
    const box = (element) => element.getBoundingClientRect().toJSON();
    const row = document.querySelector(".facts-table > div");
    const form = document.querySelector("#account-usyd-title")
      .closest(".report-section")
      .querySelector("form");
    return {
      label: box(row.querySelector("dt")),
      value: box(row.querySelector("dd")),
      avatar: box(document.querySelector(".account-summary > :first-child")),
      identity: box(document.querySelector(".account-summary__identity")),
      update: box(form.querySelector("button[type=submit]")),
      form: box(form),
      tagFont: getComputedStyle(document.querySelector(".account-summary .status-tag"))
        .fontFamily,
    };
  });

// Edit Profile and Preview (design_document.md 7.11): the current avatar sits
// beside the upload controls on wide screens and above them on phones; the two
// short fields pair up when there is room; the actions keep their own width;
// the Preview frame is dashed and labelled "Public view".
const profileEditLayout = (page) =>
  page.evaluate(() => {
    const box = (element) => element.getBoundingClientRect().toJSON();
    const form = document.querySelector("form.settings-form");
    return {
      current: box(document.querySelector(".avatar-editor__current")),
      controls: box(document.querySelector(".avatar-editor__controls")),
      experience: box(document.querySelector("#id_experience_level")),
      arm: box(document.querySelector("#id_preferred_arm")),
      save: box(form.querySelector("button[type=submit]")),
      form: box(form),
    };
  });

const previewFrame = (page) =>
  page.evaluate(() => {
    const frame = document.querySelector(".preview-frame");
    return {
      borderStyle: getComputedStyle(frame).borderTopStyle,
      label: frame.querySelector(".preview-frame__label").textContent.replace(/\s+/g, " ").trim(),
      containsPanel: Boolean(frame.querySelector(".profile-panel")),
      containsActions: Boolean(frame.querySelector(".button")),
    };
  });

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
      .getByRole("heading", { level: 2, name: "Public member profile" })
      .waitFor();
    await desktopPage.getByText("Unavailable on public pages", { exact: true }).waitFor();
    await desktopPage.getByRole("link", { name: "Edit profile" }).waitFor();
    await desktopPage.getByRole("link", { name: "Preview profile" }).waitFor();
    await desktopPage.getByRole("link", { name: "Unpublish profile" }).waitFor();
    const desktopAccount = await accountLayout(desktopPage);
    assert.ok(
      desktopAccount.value.left >= desktopAccount.label.right &&
        Math.abs(desktopAccount.value.top - desktopAccount.label.top) <= 4,
      "Desktop Account facts must put the label beside the value.",
    );
    assert.ok(
      desktopAccount.identity.left >= desktopAccount.avatar.right,
      "Desktop Account summary must put the avatar beside the identity.",
    );
    assert.ok(
      desktopAccount.update.width < desktopAccount.form.width / 2 &&
        Math.abs(desktopAccount.update.left - desktopAccount.form.left) <= 1,
      "Desktop Update account must be left-aligned at its own width.",
    );
    assert.match(desktopAccount.tagFont, /JetBrains Mono/);

    await desktopPage.goto(`${baseUrl}/profile/edit/`);
    const desktopEdit = await profileEditLayout(desktopPage);
    assert.ok(
      desktopEdit.controls.left >= desktopEdit.current.right &&
        Math.abs(desktopEdit.controls.top - desktopEdit.current.top) <= 4,
      "Desktop Edit Profile must put the current avatar beside the upload controls.",
    );
    assert.ok(
      desktopEdit.arm.left >= desktopEdit.experience.right &&
        Math.abs(desktopEdit.arm.top - desktopEdit.experience.top) <= 1,
      "Desktop Edit Profile must pair Experience level and Preferred arm.",
    );
    assert.ok(
      desktopEdit.save.width < desktopEdit.form.width / 2 &&
        Math.abs(desktopEdit.save.left - desktopEdit.form.left) <= 1,
      "Desktop Save changes must be left-aligned at its own width.",
    );
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
    assert.deepEqual(await previewFrame(desktopPage), {
      borderStyle: "dashed",
      label: `Public view /members/${ownerUsername}/`,
      containsPanel: true,
      containsActions: false,
    });
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
    await mobilePage.goto(`${baseUrl}/account/`);
    const mobileAccount = await accountLayout(mobilePage);
    assert.ok(
      mobileAccount.value.top >= mobileAccount.label.bottom,
      "Mobile Account facts must put the label above the value.",
    );
    assert.ok(
      mobileAccount.identity.left >= mobileAccount.avatar.right,
      "Mobile Account summary keeps the compact avatar beside the identity.",
    );
    await mobilePage.goto(`${baseUrl}/profile/edit/`);
    const mobileEdit = await profileEditLayout(mobilePage);
    assert.ok(
      mobileEdit.controls.top >= mobileEdit.current.bottom,
      "Mobile Edit Profile must put the current avatar above the upload controls.",
    );
    assert.ok(
      mobileEdit.arm.top >= mobileEdit.experience.bottom,
      "Mobile Edit Profile must stack Experience level and Preferred arm.",
    );
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
