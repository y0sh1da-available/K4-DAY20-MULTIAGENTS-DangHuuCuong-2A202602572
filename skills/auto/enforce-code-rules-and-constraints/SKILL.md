---
name: enforce-code-rules-and-constraints
description: WHEN implementing code fixes, refactoring, or writing new modules to ensure compliance with type hints, regression test requirements, changelog entries, and test file preservation.
---
- Never modify existing files inside test suites (create new test files instead if needed).
- Add full type annotations to parameters and return values for all public functions (names not starting with `_`).
- Implement required regression tests in a dedicated test file and verify they pass.
- Record all bug fixes in `CHANGELOG.md` under the `## Unreleased` section using the format `- fix(<function name>): <short description>`.
