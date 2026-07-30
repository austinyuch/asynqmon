import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";

export default tseslint.config(
  { ignores: ["build/**", "node_modules/**", "playwright-report/**", "test-results/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["scripts/**/*.mjs", "vite.config.ts", "playwright.config.ts"],
    languageOptions: { globals: { ...globals.node } },
  },
  {
    files: ["src/**/*.{ts,tsx}", "e2e/**/*.ts"],
    plugins: { "react-hooks": reactHooks },
    languageOptions: { globals: { ...globals.browser } },
    rules: {
      ...reactHooks.configs.recommended.rules,
      // Legacy-code accommodations — rationale in .agents/specs/005-quality-gaps/design.md:
      // the API adapter layer (api.ts, actions/) is intentionally `any`-heavy until typed (SPEC-004 follow-up).
      "@typescript-eslint/no-explicit-any": "off",
      // Pre-existing intentional dep omissions; error would force behavior changes out of scope here.
      "react-hooks/exhaustive-deps": "warn",
      // react-hooks v6 newly flags a legacy ref-read in the GroupSelect
      // listbox adapter; behavior-preserving refactor deferred (same
      // rationale as exhaustive-deps above).
      "react-hooks/refs": "warn",
      // Legacy switch-heavy reducers/components predate the fork:
      // case-block declarations and dead reassignments are stylistic here,
      // and block-scoping refactors are behavior-risk with no user value.
      "no-case-declarations": "off",
      "no-useless-assignment": "off",
      "@typescript-eslint/no-unused-vars": ["error", {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
        caughtErrorsIgnorePattern: "^_",
      }],
    },
  }
);
