// Post-build gate (SPEC-002 FMEA R-1): the Go server templates
// build/index.html with custom delimiters "/[[" and "]]". If Vite ever
// URL-encodes the brackets or drops the base prefix, RootPath substitution
// silently breaks for sub-path deployments — fail the build instead.
import { readdirSync, readFileSync } from "node:fs";

const html = readFileSync(new URL("../build/index.html", import.meta.url), "utf8");
const assetsDir = new URL("../build/assets/", import.meta.url);
const javascript = readdirSync(assetsDir)
  .filter((name) => name.endsWith(".js"))
  .map((name) => readFileSync(new URL(name, assetsDir), "utf8"))
  .join("\n");

const mustContain = [
  '<base href="/[[.RootPath]]/"', // only HTML is Go-template rendered
  'window.FLAG_ROOT_PATH = "/[[.RootPath]]"', // flag line for parseFlags
  "/[[.PrometheusAddr]]",
  "/[[.ReadOnly]]",
  './assets/', // entry assets resolve through the templated HTML base
];
const mustNotContain = ["%5B", "%5D", "%PUBLIC_URL%"];

const errors = [];
for (const s of mustContain) {
  if (!html.includes(s)) errors.push(`missing token: ${s}`);
}
for (const s of mustNotContain) {
  if (html.includes(s)) errors.push(`forbidden token present: ${s}`);
}
if (javascript.includes("/[[.RootPath]]")) {
  errors.push("RootPath template token leaked into JavaScript chunks");
}

if (errors.length > 0) {
  console.error("verify-go-template-tokens: FAIL");
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log("verify-go-template-tokens: OK");
