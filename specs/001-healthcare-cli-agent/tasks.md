# Tasks: Healthcare CLI AI Agent

**Input**: Design documents from `/specs/001-healthcare-cli-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-schema.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Exact file paths are included in every description

## Path Conventions

Single project layout per plan.md:

```
src/cli/, src/providers/, src/services/, src/models/
tests/unit/, tests/integration/, tests/contract/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure and dependency configuration

- [ ] T001 Run `uv init` and configure pyproject.toml with all dependencies: anthropic>=0.30, openai>=1.30, google-generativeai>=0.7, click, rich>=13.0, pydantic>=2.0, langgraph, llama-index, pytest>=8.0, pytest-mock>=3.14; add `[project.scripts] agent = "src.cli.main:cli"` entry point
- [ ] T002 Create source and test directory structure with empty `__init__.py` files: src/cli/, src/providers/, src/services/, src/models/, tests/unit/, tests/integration/, tests/contract/
- [ ] T003 [P] Create .gitignore covering .venv/, __pycache__/, *.pyc, .env, *.egg-info/, dist/, .pytest_cache/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Define `AIProvider` protocol with `query(prompt: str, system: str) -> str` abstract method and `name: str` attribute in src/providers/base.py; define `ProviderError` exception class for API errors
- [ ] T005 [P] Implement `ClaudeProvider(AIProvider)` using the anthropic SDK (`claude-sonnet-4-6` model default); read API key from `ANTHROPIC_API_KEY` env var; raise `ProviderError` with remediation hint if key is missing or API call fails in src/providers/claude.py
- [ ] T006 [P] Implement `GPTProvider(AIProvider)` using the openai SDK (`gpt-4o` model default); read API key from `OPENAI_API_KEY` env var; raise `ProviderError` with remediation hint on missing key or API failure in src/providers/gpt.py
- [ ] T007 [P] Implement `GeminiProvider(AIProvider)` using the google-generativeai SDK (`gemini-2.0-flash` model default); read API key from `GOOGLE_API_KEY` env var; raise `ProviderError` with remediation hint on missing key or API failure in src/providers/gemini.py
- [ ] T008 Implement `ProviderFactory` with `get(name: str) -> AIProvider` class method mapping `"claude"`, `"openai"`, `"gemini"` to provider instances; raise `ProviderError` with valid names listed if name is unknown in src/providers/__init__.py
- [ ] T009 Implement config loading: `load_config() -> Config` reads `~/.config/healthcare-agent/config.toml` (creates with default `claude` if absent), returns `Config(default_provider: str)`; implement `Session` dataclass with `active_provider: str` and `first_call_confirmed: bool = False` in src/config.py
- [ ] T010 Implement rich output helpers: `print_disclaimer()`, `print_emergency(message)`, `print_section(title, items)`, `print_error(msg, stderr=True)`; define `DISCLAIMER = "This information is not a substitute for professional medical advice, diagnosis, or treatment."` in src/cli/output.py
- [ ] T011 Create click CLI app group `cli` with `--provider` option (overrides config default); resolve active provider via ProviderFactory + Session at command invocation; register entry point `agent` in src/cli/main.py; verify `uv run agent --help` works
- [ ] T012 [P] Define `Severity` enum (`none`, `mild`, `moderate`, `severe`) and `Likelihood` enum (`low`, `moderate`, `high`) in src/models/__init__.py

**Checkpoint**: Foundation ready — `uv run agent --help` lists all subcommands; provider adapters instantiate without error when keys are set

---

## Phase 3: User Story 1 — Symptom Checker (Priority: P1) 🎯 MVP

**Goal**: Users can submit symptoms and receive a structured analysis with conditions, likelihoods, next steps, sources, and a medical disclaimer. Emergency conditions are prominently highlighted. Ambiguous inputs trigger one clarifying question.

**Independent Test**: `uv run agent symptoms --input "fever, headache, fatigue"` prints possible conditions with likelihood indicators, next steps, cited sources, and the disclaimer — verifiable without any other feature present

- [ ] T013 [P] [US1] Define `SymptomQuery(BaseModel)` with fields `symptoms: list[str]`, `clarification: str | None`, `provider: str`; define `Condition(BaseModel)` with `name`, `likelihood: Likelihood`, `description`; define `SymptomAnalysis(BaseModel)` with `conditions: list[Condition]`, `next_steps: list[str]`, `emergency: bool`, `sources: list[str]`, `disclaimer: str` in src/models/symptoms.py
- [ ] T014 [US1] Implement `emergency_classifier(symptoms: list[str], provider: AIProvider) -> bool` that sends a short structured prompt asking the provider to return JSON `{"emergency": true/false}` and parses the result in src/services/symptoms.py
- [ ] T015 [US1] Implement `ambiguity_check(symptoms: list[str], provider: AIProvider) -> tuple[bool, str | None]` that asks the provider if symptoms are ambiguous; returns `(True, follow_up_question)` or `(False, None)` in src/services/symptoms.py
- [ ] T016 [US1] Implement `analyze_symptoms(query: SymptomQuery, provider: AIProvider) -> SymptomAnalysis` using a LangGraph 2-node graph: node 1 runs emergency_classifier + ambiguity_check, node 2 runs full analysis prompt returning structured conditions/next_steps/sources; always sets `disclaimer = DISCLAIMER` in src/services/symptoms.py
- [ ] T017 [US1] Implement `symptoms` click subcommand in src/cli/main.py: accept `--input TEXT` (reads stdin if omitted on TTY); call analyze_symptoms; if `emergency=True` call `print_emergency()` first; print conditions table, next steps, sources via `print_section()`; always call `print_disclaimer()`; exit code 1 on empty input, 2 on ProviderError, 3 on user abort
- [ ] T018 [P] [US1] Write unit tests for `emergency_classifier`, `ambiguity_check`, `analyze_symptoms` using pytest-mock to mock `AIProvider.query`; cover: normal flow, emergency flow, ambiguous + clarification flow, empty symptoms ValueError in tests/unit/test_symptoms.py
- [ ] T019 [P] [US1] Write CLI contract test using click's `CliRunner`: invoke `agent symptoms --input "headache"` with stub provider; assert stdout contains condition name, "disclaimer" text, "Sources:" label; assert stderr is empty in tests/contract/test_cli_contract.py
- [ ] T020 [US1] Write integration test with a `StubProvider` that returns a canned response; run full `analyze_symptoms` end-to-end; assert `SymptomAnalysis` fields are populated and disclaimer is present in tests/integration/test_symptom_flow.py

**Checkpoint**: `uv run agent symptoms --input "severe chest pain, shortness of breath"` prints `⚠️ EMERGENCY` panel, conditions, and disclaimer

---

## Phase 4: User Story 2 — Medical Record Summarization (Priority: P2)

**Goal**: Users can pass a plain-text medical record (inline or via file) and receive a structured summary with diagnoses, medications, allergies, and follow-up recommendations. Long records are chunked without data leakage.

**Independent Test**: `uv run agent summarize --file record.txt` prints a summary with diagnoses, medications, allergies, and follow-up sections plus the disclaimer — verifiable without symptom or drug features present

- [ ] T021 [P] [US2] Define `MedicalRecord(BaseModel)` with `content: str`, `source_label: str | None`, `provider: str`; define `RecordSummary(BaseModel)` with `diagnoses: list[str]`, `medications: list[str]`, `allergies: list[str]`, `follow_ups: list[str]`, `disclaimer: str` in src/models/records.py
- [ ] T022 [US2] Implement `chunk_record(text: str, max_tokens: int = 3000) -> list[str]` using LlamaIndex `SimpleNodeParser` with sentence-window splitting; return list of plain-text chunk strings; never write chunks to disk in src/services/summarizer.py
- [ ] T023 [US2] Implement `summarize_record(record: MedicalRecord, provider: AIProvider) -> RecordSummary` using map-reduce: summarize each chunk from `chunk_record()` then merge into final `RecordSummary`; always sets `disclaimer = DISCLAIMER` in src/services/summarizer.py
- [ ] T024 [US2] Implement `summarize` click subcommand in src/cli/main.py: accept mutually exclusive `--file PATH` and `--input TEXT`; read file into memory (do not retain path); call `summarize_record()`; print structured output with labelled sections; always call `print_disclaimer()`; exit codes: 1 neither/both provided, 2 file not found, 3 ProviderError, 4 user abort
- [ ] T025 [P] [US2] Write unit tests for `chunk_record` (verify no disk writes, chunk boundaries, token size) and `summarize_record` (mocked provider, single-chunk and multi-chunk cases) in tests/unit/test_summarizer.py
- [ ] T026 [P] [US2] Write CLI contract test using `CliRunner`: invoke `agent summarize --input "Patient diagnosed with..."` with stub provider; assert stdout sections include "Diagnoses", "Medications", "Allergies", "Follow-up", disclaimer in tests/contract/test_cli_contract.py
- [ ] T027 [US2] Write no-data-leakage integration test: run `summarize_record` with stub provider and a fixture record; capture logging output; assert no fixture patient text appears in any log record in tests/integration/test_no_data_leakage.py

**Checkpoint**: `uv run agent summarize --file tests/fixtures/sample_record.txt` prints all four summary sections and disclaimer; no patient text in logs

---

## Phase 5: User Story 3 — Drug Interaction Checker (Priority: P3)

**Goal**: Users can provide 2+ drug names and receive a structured interaction report with severity levels and precautions. Severe interactions require confirmation before display. Unrecognised drugs are flagged.

**Independent Test**: `uv run agent interactions --drugs "warfarin, aspirin"` returns an interaction report with severity and precautions plus disclaimer — verifiable without other features present

- [ ] T028 [P] [US3] Define `DrugList(BaseModel)` with `drugs: list[str]` (min 2), `provider: str`; define `InteractionPair(BaseModel)` with `drug_a`, `drug_b`, `severity: Severity`, `description`, `precautions: list[str]`, `sources: list[str]`; define `InteractionReport(BaseModel)` with `pairs: list[InteractionPair]`, `unrecognised: list[str]`, `max_severity: Severity`, `disclaimer: str` in src/models/interactions.py
- [ ] T029 [US3] Implement `check_interactions(drug_list: DrugList, provider: AIProvider) -> InteractionReport`: send structured prompt requesting JSON interaction pairs with severity; parse response into `InteractionReport`; compute `max_severity` from all pairs; always sets `disclaimer = DISCLAIMER` in src/services/interactions.py
- [ ] T030 [US3] Implement unrecognised drug detection within `check_interactions`: if provider flags a drug as unknown in response JSON, add to `InteractionReport.unrecognised`; print warning via `print_error()` for each unrecognised name in src/services/interactions.py
- [ ] T031 [US3] Implement `interactions` click subcommand in src/cli/main.py: accept `--drugs TEXT` (comma-split, strip whitespace, validate ≥2 names); call `check_interactions()`; if `max_severity == severe` call `click.confirm()` before printing report; print pairs table with severity/precautions/sources; always call `print_disclaimer()`; exit codes: 1 fewer than 2 drugs, 2 ProviderError, 3 user abort
- [ ] T032 [P] [US3] Write unit tests for `check_interactions`: cover no-interaction case ("No known interactions"), mild/moderate/severe cases, unrecognised drug flag, fewer-than-2 drugs ValueError; all with mocked provider in tests/unit/test_interactions.py
- [ ] T033 [P] [US3] Write CLI contract test using `CliRunner`: invoke `agent interactions --drugs "drug_a, drug_b"` with stub provider returning severe severity; assert confirmation prompt fires and, on confirmation, output contains severity label, precautions, disclaimer in tests/contract/test_cli_contract.py
- [ ] T034 [US3] Write integration test with `StubProvider` for complete interaction flow: stub returns one severe pair; assert `InteractionReport` is correctly populated and `max_severity == severe` in tests/integration/test_interactions_flow.py

**Checkpoint**: `uv run agent interactions --drugs "warfarin, aspirin"` prompts confirmation for severe interaction, then prints full report with disclaimer

---

## Phase 6: User Story 4 — AI Provider Selection (Priority: P4)

**Goal**: Users can select an AI provider per command via `--provider` flag or set a persistent default via `agent config --set-provider`; missing or invalid keys yield a descriptive error with a fix hint.

**Independent Test**: Run `uv run agent symptoms --input "headache" --provider gemini` and confirm the response is generated via Gemini's API — verifiable independently of other features

- [ ] T035 [US4] Implement `config` click subcommand in src/cli/main.py: `--set-provider TEXT` validates name against `{"claude","openai","gemini"}`, writes to `~/.config/healthcare-agent/config.toml`, prints confirmation; `--show` reads and prints current config and file path; exit code 1 on invalid provider name
- [ ] T036 [US4] Wire per-command `--provider` override: in each subcommand (`symptoms`, `summarize`, `interactions`) resolve active provider as: CLI flag → config default; pass resolved provider name to `ProviderFactory.get()` before service call in src/cli/main.py and src/config.py
- [ ] T037 [US4] Implement descriptive error message in each provider adapter (`claude.py`, `gpt.py`, `gemini.py`) when API key env var is absent: raise `ProviderError` with message `"<KEY_VAR> not set. Export it with: export <KEY_VAR>=your-key"` in src/providers/
- [ ] T038 [P] [US4] Write unit tests for config loading (missing file → default created, valid/invalid provider names) and `ProviderFactory.get()` (valid names, unknown name error) in tests/unit/test_config.py
- [ ] T039 [P] [US4] Write integration test confirming provider switch: instantiate two stub providers with different `name` attributes; call a service with each; assert `AIProvider.query` was called on the correct stub each time in tests/integration/test_provider_routing.py

**Checkpoint**: `uv run agent config --set-provider gemini` persists config; subsequent `uv run agent symptoms --input "test"` uses Gemini; `--provider claude` flag overrides to Claude

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Safety gates, error handling, and edge cases that apply across all user stories

- [ ] T040 Implement first-API-call confirmation gate in src/cli/main.py: before the first `ProviderFactory.get()` call per session, if `session.first_call_confirmed == False`, call `click.confirm("This will send data to an external AI service. Continue?")` and set flag; raise `click.Abort` on denial (exit code 3)
- [ ] T041 [P] Add graceful handling for malformed or empty AI provider responses in src/providers/base.py: if `query()` returns an empty string or unparseable JSON, raise `ProviderError("Malformed response from provider")`
- [ ] T042 [P] Add network timeout (30s default) and retry-once logic to all three provider adapters; on `TimeoutError` raise `ProviderError` with message suggesting retry or provider switch in src/providers/claude.py, src/providers/gpt.py, src/providers/gemini.py
- [ ] T043 Audit all click subcommands to ensure every foreseeable error condition exits with the correct non-zero code per contracts/cli-schema.md; add `sys.exit()` calls or `ctx.exit()` where missing in src/cli/main.py
- [ ] T044 [P] Add edge-case input guards: empty `--input` → exit 1 with "No symptoms provided"; non-text/binary `--file` → exit 2 with "File must be plain text"; `--drugs` with only one name → exit 1 with "Provide at least 2 drug names" in src/cli/main.py and src/services/
- [ ] T045 Validate all quickstart.md scenarios end-to-end with a real provider API key; fix any discrepancies between documented command syntax and actual CLI behaviour

**Checkpoint**: All success criteria SC-001 through SC-007 verifiable; `uv run pytest` passes; `uv run agent --help` is accurate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **blocks all user stories**
- **User Stories (Phases 3–6)**: All depend on Phase 2 completion; stories can proceed in parallel if staffed
- **Polish (Phase 7)**: Depends on all desired user story phases being complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no dependency on other stories
- **US2 (P2)**: Starts after Phase 2 — no dependency on other stories
- **US3 (P3)**: Starts after Phase 2 — no dependency on other stories
- **US4 (P4)**: Starts after Phase 2 — provider infrastructure already in Phase 2; US4 adds config subcommand and wiring only

### Within Each User Story

- Models (T0XX [P]) before services
- Services before CLI subcommand
- CLI subcommand before integration tests
- Story complete before moving to next priority

---

## Parallel Execution Examples

### Phase 2 Parallel Batch

```
T005 Implement ClaudeProvider         ← parallel
T006 Implement GPTProvider            ← parallel
T007 Implement GeminiProvider         ← parallel
T012 Define Severity/Likelihood enums ← parallel
```

### Phase 3 (US1) Parallel Batch

```
T013 Define symptom models            ← parallel (different file from T014–T016)
T018 Write symptom unit tests         ← parallel (after T014–T016 complete)
T019 Write symptom contract test      ← parallel (after T017 complete)
```

### Phase 4 (US2) Parallel Batch

```
T021 Define record models             ← parallel (different file from T022–T024)
T025 Write summarizer unit tests      ← parallel (after T022–T023 complete)
T026 Write summarize contract test    ← parallel (after T024 complete)
```

### Phase 5 (US3) Parallel Batch

```
T028 Define interaction models        ← parallel (different file from T029–T031)
T032 Write interaction unit tests     ← parallel (after T029–T030 complete)
T033 Write interaction contract test  ← parallel (after T031 complete)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (Symptom Checker)
4. **STOP and VALIDATE**: Run `uv run agent symptoms --input "fever, headache"` end-to-end
5. Ship/demo MVP

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. US1 → test independently → **MVP demo**
3. US2 → test independently → summarization added
4. US3 → test independently → drug interactions added
5. US4 → test independently → full multi-provider support
6. Polish → production-ready

### Parallel Team Strategy

Once Phase 2 completes:

- Developer A: US1 (Symptom Checker)
- Developer B: US2 (Medical Record Summarization)
- Developer C: US3 + US4 (Drug Interactions + Provider Config)

---

## Notes

- `[P]` tasks operate on different files with no dependency on incomplete sibling tasks
- Each user story phase is a complete, independently testable increment
- No patient data must appear in any log: `pytest` run for T027 verifies this programmatically
- `uv` only — never `pip` per CLAUDE.md
- All tests go in `/tests` per CLAUDE.md
