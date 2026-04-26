# Lab 3.2 — Cursor vs VSCode Copilot Comparison

## Feature Tested
- Lab 3.1: --output flag (VSCode Copilot)
- Lab 3.2: --format flag (Cursor)

## Planning Quality
- VSCode: Listed files to modify before making any changes
- Cursor: Showed inline diff before asking to Keep

## Edit Quality
- VSCode: +47/-9 lines, clean with no code duplication
- Cursor: +25/-13 lines, added constants and helper functions

## Verification Behavior
- VSCode: Ran actual terminal commands, requested Allow for each step
- Cursor: Verified in chat only, did not run terminal commands
- Cursor additionally flagged a Windows encoding bug

## Model Choice Rationale
- VSCode: GPT-5.3-Codex
- Cursor: Auto (model not explicitly shown)

## Summary
Cursor is faster with a smoother UX.
VSCode Copilot performs more thorough verification
by running actual terminal commands at each step.