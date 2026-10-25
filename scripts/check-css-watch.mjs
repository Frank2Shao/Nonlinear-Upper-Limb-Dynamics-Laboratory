import { spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = await mkdtemp(path.join(os.tmpdir(), "nuldl-tailwind-"));
const outputFile = path.join(outputDirectory, "site.css");
const cli = path.join(
  projectRoot,
  "node_modules",
  "@tailwindcss",
  "cli",
  "dist",
  "index.mjs",
);
const child = spawn(
  process.execPath,
  [
    cli,
    "-i",
    "./static_src/css/site.css",
    "-o",
    outputFile,
    "--watch=always",
  ],
  { cwd: projectRoot, stdio: ["ignore", "pipe", "pipe"] },
);

let output = "";
const timeout = setTimeout(() => {
  child.kill();
  throw new Error(`Tailwind watch did not build within 20 seconds.\n${output}`);
}, 20_000);

const capture = (chunk) => {
  output += chunk.toString();
  if (output.includes("Done in")) {
    clearTimeout(timeout);
    child.kill();
  }
};

child.stdout.on("data", capture);
child.stderr.on("data", capture);

await new Promise((resolve, reject) => {
  child.on("error", reject);
  child.on("exit", (code, signal) => {
    clearTimeout(timeout);
    if (output.includes("Done in") && (signal || code === 0)) {
      resolve();
    } else {
      reject(new Error(`Tailwind watch failed.\n${output}`));
    }
  });
});

await rm(outputDirectory, { recursive: true, force: true });
