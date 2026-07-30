# SplitButton Ref Correctness Review

- **CR**: CR-2026-07-30-003
- **Verdict**: PASS
- **Blocking findings**: 0

The change defers `anchorRef.current` access through MUI Popper's existing lazy `anchorEl` contract. It does not change the anchor element, menu state, selection callback, click-away containment check, or public props.

Acceptance evidence is `yarn lint` with zero warnings, Vitest 3/3, TypeScript/Vite build and Go-template token gate, rebuilt committed `ui/build/`, correlated local security gate, and hosted real-data E2E/CodeQL.

Residual risk is limited to the mounted/open invariant behind the callback-local non-null assertion. The Popper can open only from the rendered button group, and the hosted browser test exercises the dashboard containing this control.

The deterministic TypeScript AST review reports one pre-existing low-severity `REVIEW_LONG_METHOD` finding for the 93-line component. Extracting JSX solely to satisfy that threshold would expand this one-line correctness CR without improving its tested behavior, so it remains a future maintainability candidate rather than a blocker.
