import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const checkOnly = process.argv.includes("--check");
const packageJson = JSON.parse(
  await readFile(path.join(projectRoot, "package.json"), "utf8"),
);

const assets = [
  ["node_modules/alpinejs/dist/cdn.min.js", "static/vendor/alpine/alpine.min.js"],
  ["node_modules/htmx.org/dist/htmx.min.js", "static/vendor/htmx/htmx.min.js"],
  [
    "node_modules/maplibre-gl/dist/maplibre-gl.mjs",
    "static/vendor/maplibre/maplibre-gl.mjs",
  ],
  [
    "node_modules/maplibre-gl/dist/maplibre-gl.css",
    "static/vendor/maplibre/maplibre-gl.css",
  ],
  [
    "node_modules/@fontsource/inter/files/inter-latin-400-normal.woff2",
    "static/fonts/inter-latin-400-normal.woff2",
  ],
  [
    "node_modules/@fontsource/inter/files/inter-latin-500-normal.woff2",
    "static/fonts/inter-latin-500-normal.woff2",
  ],
  [
    "node_modules/@fontsource/inter/files/inter-latin-600-normal.woff2",
    "static/fonts/inter-latin-600-normal.woff2",
  ],
  [
    "node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-600-normal.woff2",
    "static/fonts/barlow-condensed-latin-600-normal.woff2",
  ],
  [
    "node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-700-normal.woff2",
    "static/fonts/barlow-condensed-latin-700-normal.woff2",
  ],
  [
    "node_modules/@fontsource/barlow-condensed/files/barlow-condensed-latin-800-normal.woff2",
    "static/fonts/barlow-condensed-latin-800-normal.woff2",
  ],
  ["node_modules/htmx.org/LICENSE", "static/vendor/licenses/htmx.txt"],
  [
    "node_modules/maplibre-gl/LICENSE.txt",
    "static/vendor/licenses/maplibre-gl.txt",
  ],
  [
    "node_modules/@fontsource/inter/LICENSE",
    "static/vendor/licenses/inter.txt",
  ],
  [
    "node_modules/@fontsource/barlow-condensed/LICENSE",
    "static/vendor/licenses/barlow-condensed.txt",
  ],
];

const sha256 = (buffer) => createHash("sha256").update(buffer).digest("hex");
const manifest = {
  packages: {
    "@fontsource/barlow-condensed":
      packageJson.dependencies["@fontsource/barlow-condensed"],
    "@fontsource/inter": packageJson.dependencies["@fontsource/inter"],
    alpinejs: packageJson.dependencies.alpinejs,
    "htmx.org": packageJson.dependencies["htmx.org"],
    "maplibre-gl": packageJson.dependencies["maplibre-gl"],
  },
  files: {},
};

for (const [sourceName, targetName] of assets) {
  const source = path.join(projectRoot, sourceName);
  const target = path.join(projectRoot, targetName);
  const sourceBytes = await readFile(source);
  manifest.files[targetName.replaceAll("\\", "/")] = sha256(sourceBytes);

  if (checkOnly) {
    const targetBytes = await readFile(target);
    if (sha256(targetBytes) !== sha256(sourceBytes)) {
      throw new Error(`Generated asset is stale: ${targetName}`);
    }
  } else {
    await mkdir(path.dirname(target), { recursive: true });
    await copyFile(source, target);
  }
}

const manifestPath = path.join(projectRoot, "static/vendor/manifest.json");
const manifestText = `${JSON.stringify(manifest, null, 2)}\n`;
if (checkOnly) {
  if ((await readFile(manifestPath, "utf8")) !== manifestText) {
    throw new Error("Generated vendor manifest is stale.");
  }
} else {
  await mkdir(path.dirname(manifestPath), { recursive: true });
  await writeFile(manifestPath, manifestText, "utf8");
}
