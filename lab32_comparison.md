# Lab 3.2 - Cursor vs VSCode Copilot Comparison

## Feature Tested
Same prompt used in both tools:
"Build the medical record summarization feature as defined 
in SPEC.md. Use LlamaIndex for processing and ensure no 
data is stored as per FR-004."

## Planning Quality
- VSCode: Read files one by one before making changes.
  No explicit plan document created.
- Cursor: Explored 9 files and 7 searches automatically.
  Generated a dedicated plan file with 4 structured 
  to-dos before writing any code.
  Winner: Cursor - more thorough upfront planning.

## Edit Quality
- VSCode: main.py (+47/-9) clean edits, no duplication
- Cursor: Plan Mode only - showed src/ layout with 
  separate modules: src/models/records.py and 
  src/services/summarizer.py

## Verification Behavior
- VSCode: Ran actual terminal commands automatically.
  Requested Allow/Skip permission before each step.
  Ran 3 validation tests automatically.
- Cursor: Used Plan Mode - verified via web search 
  for LlamaIndex API before writing code.
  Did not run terminal commands in Plan Mode.

## Model Choice Rationale
- VSCode: Auto (VSCode Copilot default)
- Cursor: Auto (shown at bottom of Agent panel)

## Summary
Cursor Plan Mode provides more structured upfront planning.
VSCode Copilot performs more thorough runtime verification
by running actual terminal commands at each step.