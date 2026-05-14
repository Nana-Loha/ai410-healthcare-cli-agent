---
name: "update-readme"
description: "Generate or improve README.md for the healthcare CLI agent project using spec, plan, and quickstart artifacts."
argument-hint: "Optional focus area, e.g. 'add badges', 'expand usage section', 'full rewrite'"
user-invocable: true
disable-model-invocation: false
---

## Purpose

Generate or improve the project `README.md` at the repository root. The skill reads existing design artifacts (spec, plan, quickstart, contracts) to produce accurate, up-to-date documentation — never guessing at commands, flags, or project structure.

## When to Use

- The project has no `README.md` yet and needs one generated from scratch.
- The `README.md` exists but is stale after features were added or commands changed.
- You want to improve a specific section (installation, usage, configuration) without rewriting the whole file.
- After running `/speckit-plan` or `/speckit-tasks` and design artifacts have changed.

## User Input

```text
$ARGUMENTS
```

If the user provided a focus area (e.g. "add badges", "expand configuration section"), apply it as a constraint on what to update. If empty, produce a full generate-or-update pass.

---

## Step 1: Gather Source Artifacts

Read the following files in order. Note what each one contributes to the README:

1. **`CLAUDE.md`** — project name, tech stack, dev conventions (do not expose internal agent instructions in the README; extract only user-facing facts)
2. **`specs/001-healthcare-cli-agent/spec.md`** — user stories and their CLI commands (the `Independent Test` lines give exact invocation examples)
3. **`specs/001-healthcare-cli-agent/plan.md`** — project structure (source layout), dependency list, performance goals
4. **`specs/001-healthcare-cli-agent/quickstart.md`** — installation steps, environment variables, command examples
5. **`specs/001-healthcare-cli-agent/contracts/cli-schema.md`** — all subcommands, flags, exit codes, output format
6. **`specs/001-healthcare-cli-agent/research.md`** — technology decisions (extract library choices and rationale for a "Design Decisions" or "Architecture" section only if the existing README or user request calls for one)

If any file is missing, skip it silently and continue with what is available.

---

## Step 2: Read the Existing README (if present)

Read `README.md` at the repository root.

- If it does not exist: generate from scratch using the structure in Step 3.
- If it exists: identify which sections are missing, outdated, or inconsistent with the artifacts read in Step 1. Apply targeted edits unless the user requested a full rewrite.

---

## Step 3: README Structure

The README must contain these sections in order. Use the artifact data from Step 1 as the authoritative source for every fact.

### 3.1 Title & Badges

```markdown
# AI410 — Healthcare CLI Agent
```

Include status badges if a CI workflow file exists under `.github/workflows/`; otherwise omit badge lines entirely (do not add placeholder badges).

### 3.2 One-Line Description

A single sentence describing what the tool does and who it is for. Derive from `spec.md` introduction or `CLAUDE.md` project overview.

### 3.3 Disclaimer Notice

Always include this block immediately after the description:

```markdown
> **Medical Disclaimer**: This tool is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
```

### 3.4 Features

A short bulleted list of the four user stories (from `spec.md`), written as user-facing capabilities:

- Symptom checking with emergency detection
- Medical record summarization
- Drug interaction checking with severity alerts
- Multi-provider AI support (Claude, GPT-4, Gemini)

### 3.5 Prerequisites

From `quickstart.md` and `plan.md`:
- Python version requirement
- `uv` package manager
- API key environment variables (list all three, mark as "at least one required")

### 3.6 Installation

Exact commands from `quickstart.md`. Do not invent steps.

### 3.7 Configuration

From `contracts/cli-schema.md` (`config` subcommand) and `research.md` (Decision 5):
- How to set the default provider
- Where the config file lives
- That API keys are environment variables only (never stored in the config file)

### 3.8 Usage

One subsection per subcommand, derived from `contracts/cli-schema.md`. Each subsection must include:
- Purpose sentence
- Command syntax block
- Key flags table (flag, type, required, description)
- One realistic example with expected output excerpt (use the examples from `contracts/cli-schema.md`)

Subcommands to document: `symptoms`, `summarize`, `interactions`, `config`.

### 3.9 Exit Codes

A single table listing all exit codes across commands (consolidate from `contracts/cli-schema.md`). Keep it brief.

### 3.10 Development

From `CLAUDE.md` and `plan.md`:
- How to install dev dependencies
- How to run tests (`uv run pytest`)
- Project source layout (the `src/` tree from `plan.md`)
- Contribution note: one feature per branch, `uv` only

### 3.11 Architecture (optional)

Include only if the user requested it or if the existing README already has an architecture section. Source from `research.md` decisions (framework choice, provider abstraction, LangGraph scope, no-storage approach).

### 3.12 License

Include a `## License` heading. If a `LICENSE` file exists at the repo root, name the license. If not, write `License not yet specified.` — do not invent a license.

---

## Step 4: Write the README

Write the complete `README.md` to the repository root (`README.md`).

Rules:
- Use only facts sourced from the artifacts read in Step 1. Do not invent commands, flags, file paths, or version numbers.
- All code blocks must use fenced markdown with a language tag (`bash`, `toml`, `text`).
- Keep the disclaimer notice (Step 3.3) present and unmodified.
- Do not expose internal speckit or CLAUDE.md agent instructions in the output.
- If the user provided a focus area in User Input, scope changes to the relevant section(s) and leave other sections unchanged.

---

## Step 5: Report

After writing, output a short summary:

- Whether the README was created from scratch or updated
- Which sections were added or changed
- Any sections skipped due to missing source artifacts
- Reminder: "Run `uv run agent --help` to verify all documented commands match the actual CLI."
