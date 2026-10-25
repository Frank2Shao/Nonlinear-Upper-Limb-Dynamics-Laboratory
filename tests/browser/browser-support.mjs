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
