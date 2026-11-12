import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

import {
  assertNoExternalRequests,
  createLocalContext,
  requireEnvironment,
} from "./browser-support.mjs";

const baseUrl = requireEnvironment("NULDL_LIVE_SERVER_URL");
const cookieName = requireEnvironment("NULDL_SESSION_COOKIE_NAME");
const cookieValue = requireEnvironment("NULDL_SESSION_COOKIE_VALUE");
const externalRequests = [];
const pageErrors = [];
const browser = await chromium.launch({ headless: true });

const addSession = async (context) => {
  await context.addCookies([{ name: cookieName, value: cookieValue, url: baseUrl }]);
};

const assertAvatarInterface = async (page, label) => {
  await page.getByRole("heading", { level: 1, name: "Edit Profile" }).waitFor();
  const avatar = page.getByRole("img", { name: "Current avatar for avatar-browser" });
  await avatar.waitFor();
  await avatar.evaluate((image) => image.decode());
  const metrics = await avatar.evaluate((image) => {
    const rectangle = image.getBoundingClientRect();
    return {
      height: rectangle.height,
      naturalHeight: image.naturalHeight,
      naturalWidth: image.naturalWidth,
      objectFit: getComputedStyle(image).objectFit,
      width: rectangle.width,
    };
  });
  assert.ok(metrics.naturalWidth > 0 && metrics.naturalHeight > 0, `${label} avatar must load.`);
  assert.ok(Math.abs(metrics.width - metrics.height) <= 1, `${label} avatar must be square.`);
  assert.equal(metrics.objectFit, "cover", `${label} avatar must use object-fit cover.`);
  await page.getByRole("checkbox", { name: "Remove current avatar" }).waitFor();
  await page.getByText(
    "Uploaded images are stored as provided and may contain location, device or other metadata. Remove sensitive metadata before uploading.",
    { exact: true },
  ).waitFor();
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    true,
    `${label} page must not overflow horizontally.`,
  );
};

try {
  const desktopContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 1280, height: 900 } },
    externalRequests,
  );
  await addSession(desktopContext);
  const desktopPage = await desktopContext.newPage();
  desktopPage.on("pageerror", (error) => pageErrors.push(error.message));
  await desktopPage.goto(`${baseUrl}/profile/edit/`);
  await assertAvatarInterface(desktopPage, "Desktop");

  const originalSource = await desktopPage
    .getByRole("img", { name: "Current avatar for avatar-browser" })
    .getAttribute("src");
  await desktopPage.locator('input[type="file"][name="avatar"]').setInputFiles({
    name: "invalid.png",
    mimeType: "image/png",
    buffer: Buffer.from("not an image"),
  });
  await desktopPage.getByRole("button", { name: "Save changes" }).click();
  await desktopPage.getByText("Upload a valid image.", { exact: false }).waitFor();
  assert.equal(
    await desktopPage
      .getByRole("img", { name: "Current avatar for avatar-browser" })
      .getAttribute("src"),
    originalSource,
    "An invalid upload must keep the current avatar.",
  );
  await desktopContext.close();

  const mobileContext = await createLocalContext(
    browser,
    baseUrl,
    { viewport: { width: 390, height: 844 } },
    externalRequests,
  );
  await addSession(mobileContext);
  const mobilePage = await mobileContext.newPage();
  mobilePage.on("pageerror", (error) => pageErrors.push(error.message));
  await mobilePage.goto(`${baseUrl}/profile/edit/`);
  await assertAvatarInterface(mobilePage, "Mobile");
  await mobilePage.getByRole("checkbox", { name: "Remove current avatar" }).focus();
  assert.equal(
    await mobilePage.evaluate(() => document.activeElement?.name),
    "remove_avatar",
    "The remove control must be keyboard focusable.",
  );
  await mobileContext.close();

  assert.deepEqual(pageErrors, [], "Avatar pages must not raise browser errors.");
  assertNoExternalRequests(externalRequests);
} finally {
  await browser.close();
}
