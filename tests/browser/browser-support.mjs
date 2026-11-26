import assert from "node:assert/strict";

export function requireEnvironment(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required.`);
  }
  return value;
}

export async function createLocalContext(
  browser,
  baseUrl,
  options = {},
  externalRequests = [],
) {
  const context = await browser.newContext(options);
  const allowedOrigin = new URL(baseUrl).origin;

  await context.route("**/*", async (route) => {
    const requestUrl = new URL(route.request().url());
    if (
      ["http:", "https:"].includes(requestUrl.protocol) &&
      requestUrl.origin !== allowedOrigin
    ) {
      externalRequests.push(requestUrl.href);
      await route.abort("blockedbyclient");
      return;
    }
    await route.continue();
  });

  return context;
}

export function assertNoExternalRequests(externalRequests) {
  assert.deepEqual(
    externalRequests,
    [],
    `Browser tests attempted external requests: ${externalRequests.join(", ")}`,
  );
}

export async function addSessionCookie(
  context,
  baseUrl,
  value,
  name = requireEnvironment("NULDL_SESSION_COOKIE_NAME"),
) {
  await context.addCookies([{ name, value, url: baseUrl }]);
}

// Layout checks measure the rendered page. After a click navigation the new
// document's DOM can be ready before its stylesheet on a slow machine (CI), so
// wait for the load event first. `scope` is a page or a locator within one.
async function waitForStyles(scope) {
  const page = typeof scope.page === "function" ? scope.page() : scope;
  await page.waitForLoadState("load");
}

export async function assertNoHorizontalOverflow(page, label) {
  await waitForStyles(page);
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  assert.ok(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label} has horizontal overflow: ${JSON.stringify(dimensions)}`,
  );
}

export async function assertPageBounds(page, label) {
  await assertNoHorizontalOverflow(page, label);
  const styleSheets = await page.evaluate(() => document.styleSheets.length);
  assert.ok(styleSheets > 0, `${label} did not load project CSS.`);
}

export async function assertPageStructure(page, label) {
  await waitForStyles(page);
  const structure = await page.evaluate(() => ({
    footer: document.querySelectorAll("body > footer").length,
    h1: [...document.querySelectorAll("h1")].filter((element) =>
      element.checkVisibility(),
    ).length,
    header: document.querySelectorAll("body > header").length,
    main: document.querySelectorAll("main#main-content").length,
  }));
  assert.deepEqual(
    structure,
    { footer: 1, h1: 1, header: 1, main: 1 },
    `${label} has an invalid landmark or heading structure.`,
  );
}

// Each scenario passes the element types that carry its page content.
// rejectEmptyBoxes additionally fails visible elements that render with no size.
export async function assertVisibleContentFits(
  page,
  label,
  { selector, rejectEmptyBoxes = false },
) {
  await waitForStyles(page);
  const clipped = await page.locator(selector).evaluateAll(
    (elements, rejectEmpty) =>
      elements
        .filter((element) => {
          if (!element.checkVisibility()) {
            return false;
          }
          const rectangle = element.getBoundingClientRect();
          return (
            (rejectEmpty && (rectangle.width <= 0 || rectangle.height <= 0)) ||
            rectangle.left < -1 ||
            rectangle.right > document.documentElement.clientWidth + 1
          );
        })
        .map(
          (element) =>
            element.textContent?.trim() || element.getAttribute("alt") || element.tagName,
        ),
    rejectEmptyBoxes,
  );
  assert.deepEqual(clipped, [], `${label} contains clipped visible content.`);
}

export const INTERACTIVE_TARGETS = "a:not(.skip-link), button, summary, input, select, textarea";

export async function assertTouchTargets(page, label, selector = INTERACTIVE_TARGETS) {
  await waitForStyles(page);
  const undersized = await page.locator(selector).evaluateAll((elements) =>
    elements
      .filter((element) => element.checkVisibility())
      .map((element) => {
        const rectangle = element.getBoundingClientRect();
        return {
          height: rectangle.height,
          name:
            element.getAttribute("aria-label") ||
            element.textContent?.trim() ||
            element.getAttribute("name") ||
            element.tagName,
          width: rectangle.width,
        };
      })
      .filter(({ height, width }) => height < 24 || width < 24),
  );
  assert.deepEqual(undersized, [], `${label} contains touch targets smaller than 24px.`);
}

export async function assertFocusIndicator(locator, label) {
  await locator.focus();
  const focus = await locator.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      active: document.activeElement === element,
      outlineStyle: style.outlineStyle,
      outlineWidth: Number.parseFloat(style.outlineWidth),
    };
  });
  assert.equal(focus.active, true, `${label} must accept keyboard focus.`);
  assert.notEqual(focus.outlineStyle, "none", `${label} must expose a focus outline.`);
  assert.ok(focus.outlineWidth >= 2, `${label} focus outline must be clearly visible.`);
}
