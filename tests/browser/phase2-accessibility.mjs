import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  assertNoHorizontalOverflow,
  assertTouchTargets,
  assertVisibleContentFits,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const VISIBLE_CONTENT = {
  selector: "h1, h2, h3, p, li, dt, dd, a, summary, img",
  rejectEmptyBoxes: true,
};
const externalRequests = [];
const pageErrors = [];

const publicPages = [
  { path: "/", status: 200, required: [".home-hero", ".home-hero__logo", ".button"] },
  { path: "/about/", status: 200, required: [".public-page", ".button"] },
  {
    path: "/beginners-safety/",
    status: 200,
    required: [".step-list", ".safety-list", ".safety-panel", ".button"],
  },
  { path: "/risk-notice/", status: 200, required: [".status-banner"] },
  { path: "/test-error/403/", status: 403, required: [".button"] },
  { path: "/test-error/missing/", status: 404, required: [".button"] },
  { path: "/test-error/500/", status: 500, required: [".button"] },
];

const browser = await chromium.launch({ headless: true });

const parseRgb = (value) => {
  const channels = value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
  assert.equal(channels?.length, 3, `Unable to parse colour: ${value}`);
  return channels;
};

const luminance = (channels) => {
  const linear = channels.map((channel) => {
    const value = channel / 255;
    return value <= 0.04045
      ? value / 12.92
      : ((value + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
};

const contrastRatio = (foreground, background) => {
  const foregroundLuminance = luminance(parseRgb(foreground));
  const backgroundLuminance = luminance(parseRgb(background));
  return (
    (Math.max(foregroundLuminance, backgroundLuminance) + 0.05) /
    (Math.min(foregroundLuminance, backgroundLuminance) + 0.05)
  );
};

const assertSemanticStructure = async (page, label) => {
  const structure = await page.evaluate(() => {
    const visible = (element) => element.checkVisibility();
    const headings = [...document.querySelectorAll("h1, h2, h3, h4, h5, h6")]
      .filter(visible)
      .map((heading) => ({
        level: Number(heading.tagName.slice(1)),
        text: heading.textContent.trim(),
      }));
    const unnamedLinks = [...document.querySelectorAll("a")]
      .filter(visible)
      .filter((link) => {
        const imageText = [...link.querySelectorAll("img")]
          .map((image) => image.getAttribute("alt") || "")
          .join(" ");
        return !(link.getAttribute("aria-label") || link.textContent || imageText).trim();
      })
      .map((link) => link.outerHTML);
    const invalidImages = [...document.querySelectorAll("img")]
      .filter(visible)
      .filter((image) => image.getAttribute("alt") === null || !image.getAttribute("alt").trim())
      .map((image) => image.outerHTML);

    return {
      headers: document.querySelectorAll("body > header").length,
      primaryNavigations: document.querySelectorAll('nav[aria-label="Primary navigation"]').length,
      mains: document.querySelectorAll("main#main-content").length,
      footers: document.querySelectorAll("body > footer").length,
      headings,
      unnamedLinks,
      invalidImages,
    };
  });

  assert.equal(structure.headers, 1, `${label} must contain one site header.`);
  assert.equal(structure.primaryNavigations, 1, `${label} must contain one named primary navigation.`);
  assert.equal(structure.mains, 1, `${label} must contain one main landmark.`);
  assert.equal(structure.footers, 1, `${label} must contain one site footer.`);
  assert.equal(
    structure.headings.filter(({ level }) => level === 1).length,
    1,
    `${label} must contain one visible H1.`,
  );
  assert.equal(structure.headings[0]?.level, 1, `${label} heading order must begin with H1.`);
  for (let index = 1; index < structure.headings.length; index += 1) {
    assert.ok(
      structure.headings[index].level <= structure.headings[index - 1].level + 1,
      `${label} skips a heading level before "${structure.headings[index].text}".`,
    );
  }
  assert.deepEqual(structure.unnamedLinks, [], `${label} contains unnamed links.`);
  assert.deepEqual(structure.invalidImages, [], `${label} contains images without useful alt text.`);
};

const assertRequiredContent = async (page, definition) => {
  for (const selector of definition.required) {
    assert.equal(
      await page.locator("main").locator(selector).first().isVisible(),
      true,
      `${definition.path} must expose ${selector}.`,
    );
  }
  assert.equal(
    await page.locator(".site-footer").isVisible(),
    true,
    `${definition.path} must expose the shared footer.`,
  );
};

const assertPage = async (page, definition, label) => {
  const response = await page.goto(`${baseUrl}${definition.path}`);
  assert.equal(response?.status(), definition.status, `${label} returned the wrong HTTP status.`);
  await page.locator("main#main-content h1").waitFor();
  await assertSemanticStructure(page, label);
  await assertRequiredContent(page, definition);
  await assertNoHorizontalOverflow(page, label);
  await assertVisibleContentFits(page, label, VISIBLE_CONTENT);
};

const assertFocusVisibleAndInViewport = async (page, expectedName) => {
  const focused = await page.evaluate(() => {
    const element = document.activeElement;
    const rectangle = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
      name: element.getAttribute("aria-label") || element.textContent.trim(),
      outlineStyle: style.outlineStyle,
      outlineWidth: Number.parseFloat(style.outlineWidth),
      rectangle: {
        bottom: rectangle.bottom,
        left: rectangle.left,
        right: rectangle.right,
        top: rectangle.top,
      },
    };
  });
  assert.equal(focused.name, expectedName, `Expected keyboard focus on ${expectedName}.`);
  assert.notEqual(focused.outlineStyle, "none", `${expectedName} must expose a focus outline.`);
  assert.ok(focused.outlineWidth >= 2, `${expectedName} focus outline must be clearly visible.`);
  assert.ok(focused.rectangle.left >= -1 && focused.rectangle.right <= 391);
  assert.ok(focused.rectangle.top >= -1 && focused.rectangle.bottom <= 845);
};

const effectiveColours = async (locator) =>
  locator.evaluate((element) => {
    const foreground = getComputedStyle(element).color;
    const transparent = /rgba?\(0, 0, 0, 0\)/;
    // Buttons paint their fill on ::after/::before layers behind the text.
    let background = getComputedStyle(element).backgroundColor;
    for (const pseudo of ["::after", "::before"]) {
      if (transparent.test(background)) {
        background = getComputedStyle(element, pseudo).backgroundColor;
      }
    }
    let current = element.parentElement;
    while (current && transparent.test(background)) {
      background = getComputedStyle(current).backgroundColor;
      current = current.parentElement;
    }
    return { background, foreground };
  });

try {
  const desktopContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1440, height: 900 } },
    externalRequests,
  );
  const desktopPage = await desktopContext.newPage();
  desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
  for (const definition of publicPages) {
    await assertPage(desktopPage, definition, `Desktop ${definition.path}`);
  }

  await desktopPage.goto(baseUrl);
  const logo = desktopPage.locator(".home-hero__logo");
  const logoState = await logo.evaluate((image) => ({
    alt: image.alt,
    complete: image.complete,
    naturalHeight: image.naturalHeight,
    naturalWidth: image.naturalWidth,
  }));
  assert.equal(logoState.alt, "Nonlinear Upper Limb Dynamics Laboratory logo");
  assert.equal(logoState.complete, true);
  assert.ok(logoState.naturalWidth > 0 && logoState.naturalHeight > 0);

  for (const [selector, minimum] of [
    ["body", 4.5],
    [".home-hero__intro", 4.5],
    [".gold-tag", 4.5],
    [".home-hero__tagline .label-mono", 4.5],
    [".home-hero__note", 4.5],
    [".drawing-block dt", 4.5],
    [".drawing-block dd", 4.5],
    ["main .button", 4.5],
    ["main .button--secondary", 4.5],
    [".site-header .button", 4.5],
  ]) {
    const colours = await effectiveColours(desktopPage.locator(selector).first());
    assert.ok(
      contrastRatio(colours.foreground, colours.background) >= minimum,
      `${selector} does not meet ${minimum}:1 contrast: ${JSON.stringify(colours)}`,
    );
  }
  await desktopPage.goto(`${baseUrl}/risk-notice/`);
  const bannerColours = await effectiveColours(desktopPage.locator(".status-banner"));
  assert.ok(
    contrastRatio(bannerColours.foreground, bannerColours.background) >= 4.5,
    `Draft banner does not meet text contrast: ${JSON.stringify(bannerColours)}`,
  );
  const outlineColour = await desktopPage.locator("body").evaluate(() => {
    const probe = document.createElement("a");
    probe.href = "#";
    probe.textContent = "Focus contrast probe";
    document.body.append(probe);
    probe.focus();
    const value = getComputedStyle(probe).outlineColor;
    probe.remove();
    return value;
  });
  const bodyBackground = await desktopPage.locator("body").evaluate(
    (element) => getComputedStyle(element).backgroundColor,
  );
  assert.ok(
    contrastRatio(outlineColour, bodyBackground) >= 3,
    "The focus indicator must meet 3:1 contrast against the page background.",
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
  for (const definition of publicPages) {
    await assertPage(mobilePage, definition, `Mobile ${definition.path}`);
    await mobilePage.waitForFunction(() => Boolean(window.Alpine));
    const disclosure = mobilePage.locator("details.nav-disclosure");
    if ((await disclosure.getAttribute("open")) === null) {
      await mobilePage.locator("summary.nav-toggle").click();
    }
    await assertTouchTargets(mobilePage, `Mobile ${definition.path}`);
  }

  await mobilePage.goto(baseUrl);
  await mobilePage.waitForFunction(() => Boolean(window.Alpine));
  await mobilePage.locator("body").focus();
  await mobilePage.keyboard.press("Tab");
  await assertFocusVisibleAndInViewport(mobilePage, "Skip to main content");
  await mobilePage.keyboard.press("Tab");
  await assertFocusVisibleAndInViewport(mobilePage, "NULDL Armwrestling Club home");
  await mobilePage.keyboard.press("Tab");
  await assertFocusVisibleAndInViewport(mobilePage, "Menu");
  await mobilePage.keyboard.press("Enter");
  assert.equal(await mobilePage.locator("details.nav-disclosure").getAttribute("open"), "");
  for (const name of [
    "Home",
    "About",
    "Beginners & Safety",
    "Events",
    "Members",
    "Draft Risk Notice",
    "Log in",
    "Join the Club",
  ]) {
    await mobilePage.keyboard.press("Tab");
    await assertFocusVisibleAndInViewport(mobilePage, name);
  }
  await mobileContext.close();

  const zoomContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 640, height: 900 } },
    externalRequests,
  );
  const zoomPage = await zoomContext.newPage();
  zoomPage.on("pageerror", (error) => pageErrors.push(error.message));
  for (const definition of publicPages) {
    const response = await zoomPage.goto(`${baseUrl}${definition.path}`);
    assert.equal(response?.status(), definition.status);
    await zoomPage.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    await assertNoHorizontalOverflow(zoomPage, `200% content zoom ${definition.path}`);
    await assertVisibleContentFits(zoomPage, `200% content zoom ${definition.path}`, VISIBLE_CONTENT);
  }
  await zoomContext.close();

  const noJsContext = await createLocalContext(
    browser,
    baseUrl,
    { javaScriptEnabled: false, viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  const noJsPage = await noJsContext.newPage();
  for (const definition of publicPages) {
    await assertPage(noJsPage, definition, `No-JavaScript ${definition.path}`);
    assert.equal(
      await noJsPage.getByRole("link", { name: "About", exact: true }).isVisible(),
      true,
      `${definition.path} navigation must remain available without JavaScript.`,
    );
  }
  await noJsContext.close();

  const reducedMotionContext = await createLocalContext(
    browser,
    baseUrl,
    { reducedMotion: "reduce", viewport: { width: 1440, height: 900 } },
    externalRequests,
  );
  const reducedMotionPage = await reducedMotionContext.newPage();
  reducedMotionPage.on("pageerror", (error) => pageErrors.push(error.message));
  await reducedMotionPage.goto(baseUrl);
  const motionState = await reducedMotionPage.locator(".button").first().evaluate((element) => ({
    animationDuration: getComputedStyle(element).animationDuration,
    animationIterationCount: getComputedStyle(element).animationIterationCount,
    mediaMatches: matchMedia("(prefers-reduced-motion: reduce)").matches,
    transitionDuration: getComputedStyle(element).transitionDuration,
  }));
  const durationInMilliseconds = (duration) =>
    Math.max(
      ...duration.split(",").map((value) => {
        const parsed = Number.parseFloat(value);
        return value.trim().endsWith("ms") ? parsed : parsed * 1000;
      }),
    );
  assert.equal(motionState.mediaMatches, true);
  assert.ok(durationInMilliseconds(motionState.animationDuration) <= 0.01);
  assert.ok(durationInMilliseconds(motionState.transitionDuration) <= 0.01);
  assert.equal(motionState.animationIterationCount, "1");
  await reducedMotionContext.close();

  assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join(", ")}`);
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
