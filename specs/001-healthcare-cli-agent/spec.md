# Feature Specification: Healthcare CLI AI Agent

**Feature Branch**: `001-healthcare-cli-agent`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "Build a CLI-based healthcare AI agent that allows users to input symptoms, summarize medical records, and check drug interactions. The system should support multiple AI providers (Claude, GPT, Gemini) and follow strict safety rules including no storage of patient data, confirmation before critical actions, and clear medical disclaimers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Symptom Checker (Priority: P1)

A user launches the CLI, selects the symptom-checking mode, types a list of symptoms in plain language, and receives a structured response listing possible conditions, their likelihood, recommended next steps, and a clear medical disclaimer. The response cites its sources.

**Why this priority**: Symptom checking is the most common healthcare query and the primary entry point for the agent. Delivering this alone constitutes a viable MVP.

**Independent Test**: Can be fully tested by running `agent symptoms --input "fever, headache, fatigue"` and verifying a response with possible conditions, next-steps, and a disclaimer is printed to stdout — without any other features present.

**Acceptance Scenarios**:

1. **Given** the CLI is running and the user provides one or more symptoms, **When** the agent processes the input, **Then** it returns a list of possible conditions with likelihood indicators, recommended actions, cited sources, and the standard medical disclaimer.
2. **Given** the user provides symptoms that are ambiguous or very general, **When** the agent processes the input, **Then** it asks one clarifying follow-up question before generating the response.
3. **Given** the response suggests an urgent condition (e.g., heart attack symptoms), **When** the agent displays the result, **Then** it prominently surfaces an emergency-services prompt before the rest of the response.
4. **Given** any AI provider is unavailable, **When** the user runs a symptom query, **Then** the CLI displays a clear error and suggests switching providers.

---

### User Story 2 - Medical Record Summarization (Priority: P2)

A user provides a block of text (pasted inline or via a file path) representing a medical record, and the agent returns a concise, structured summary covering diagnoses, medications, allergies, and recommended follow-ups. No content is stored or logged after the session ends.

**Why this priority**: Summarization adds significant value for patients reviewing lengthy documents; it does not depend on symptom checking but is less universally needed as a first feature.

**Independent Test**: Can be fully tested by running `agent summarize --file record.txt` and verifying a structured summary is printed with diagnosis, medication, and allergy sections — without symptom or drug features present.

**Acceptance Scenarios**:

1. **Given** the user provides a medical record as text or a file path, **When** the agent summarizes it, **Then** it produces a structured output with sections for diagnoses, current medications, allergies, and follow-up recommendations.
2. **Given** the record is longer than a single context window, **When** the agent processes it, **Then** it chunks and merges the summaries without losing critical information.
3. **Given** the session ends (CLI exits), **When** any audit is performed, **Then** no patient data from the record is persisted to disk, logs, or any external service.
4. **Given** the file path provided does not exist, **When** the agent attempts to read it, **Then** it displays a clear error message and exits gracefully.

---

### User Story 3 - Drug Interaction Checker (Priority: P3)

A user inputs two or more drug names and the agent returns a structured report of known interactions, severity ratings, and recommended precautions, with a confirmation prompt before displaying results if high-severity interactions are detected.

**Why this priority**: Drug interaction checking is a safety-critical feature; it is a distinct workflow and can be developed and tested independently after the core AI pipeline is established.

**Independent Test**: Can be fully tested by running `agent interactions --drugs "warfarin, aspirin"` and verifying an interaction report with severity and precautions is returned — without other features present.

**Acceptance Scenarios**:

1. **Given** the user provides two or more drug names, **When** the agent checks interactions, **Then** it returns a report listing each interaction pair, severity level (none / mild / moderate / severe), and recommended precautions with cited sources.
2. **Given** a severe interaction is detected, **When** the agent is about to display results, **Then** it first prompts the user to confirm they wish to proceed and displays a disclaimer.
3. **Given** a drug name is unrecognised, **When** the agent processes the list, **Then** it flags the unrecognised name and continues checking the remaining drugs.
4. **Given** all drugs have no known interactions, **When** the agent returns results, **Then** it clearly states "No known interactions found" rather than an empty response.

---

### User Story 4 - AI Provider Selection (Priority: P4)

A user can specify which AI provider (Claude, GPT, or Gemini) to use for any query, either via a global configuration file or a per-command flag, and can switch providers at any time without restarting the CLI.

**Why this priority**: Multi-provider support is a differentiating capability but does not block core healthcare functionality; the agent can ship with a single default provider first.

**Independent Test**: Can be fully tested by running a symptom query with `--provider gemini` and confirming the response is generated via that provider's API, independently of other features.

**Acceptance Scenarios**:

1. **Given** the user specifies a provider via `--provider <name>`, **When** the agent runs a query, **Then** it routes the request to that provider exclusively.
2. **Given** no provider flag is set, **When** the agent runs a query, **Then** it uses the provider configured as default in the configuration file.
3. **Given** the specified provider's API key is missing or invalid, **When** the agent attempts to connect, **Then** it displays a descriptive error with instructions for setting the key and exits without making a request.

---

### Edge Cases

- What happens when the user submits an empty symptom list?
- How does the system handle non-English input (symptoms or drug names)?
- What happens if the AI provider returns a malformed or empty response?
- How does the system behave when the medical record file is binary or non-text?
- What happens when two drugs have the same common name but different formulations?
- How does the system handle network timeouts during an AI provider call?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a CLI entry point that accepts subcommands for symptom checking, record summarization, drug interaction checking, and provider configuration.
- **FR-002**: The system MUST support at least three AI providers (Claude, GPT-4, Gemini) and allow the user to select one per session or per command.
- **FR-003**: The system MUST display a standard medical disclaimer on every response: *"This information is not a substitute for professional medical advice, diagnosis, or treatment."*
- **FR-004**: The system MUST NOT persist, log, or transmit any patient-supplied data (symptoms, record content, drug lists) outside of the active session.
- **FR-005**: The system MUST require explicit user confirmation before executing any action classified as critical (displaying severe drug interactions, submitting data to an external API for the first time in a session).
- **FR-006**: The system MUST cite sources or state the basis of any medical information returned to the user.
- **FR-007**: The system MUST accept symptoms as free-form text input from stdin or a `--input` flag.
- **FR-008**: The system MUST accept medical records as inline text or via a `--file` flag pointing to a local file path.
- **FR-009**: The system MUST accept drug names as a comma-separated list via a `--drugs` flag.
- **FR-010**: The system MUST surface a high-visibility emergency prompt when symptom analysis suggests life-threatening conditions.
- **FR-011**: The system MUST allow the default AI provider to be configured via a local configuration file (not containing any patient data).
- **FR-012**: The system MUST handle provider API errors gracefully, displaying a human-readable error message and a suggested remediation step.

### Key Entities

- **Symptom Query**: A user-submitted list of symptoms along with any follow-up clarifications, valid only for the duration of a session.
- **Medical Record**: A block of text provided by the user for summarization; never stored beyond the active session.
- **Drug List**: An ordered set of drug names provided by the user for interaction analysis.
- **Interaction Report**: The structured output of a drug interaction check, including severity levels and precautions for each pair.
- **AI Provider**: A configured connection to an external language model service, identified by name and authenticated via an API key stored in the user's environment.
- **Session**: A single invocation of the CLI from launch to exit; no state is carried between sessions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can receive a symptom analysis response within 30 seconds of submitting their query under normal network conditions.
- **SC-002**: Users can complete a drug interaction check for up to 10 drugs in under 45 seconds.
- **SC-003**: 100% of responses include the required medical disclaimer — verifiable by automated output scanning.
- **SC-004**: No patient-supplied data appears in any log file, temporary file, or external service call payload after a session ends — verifiable by log audit.
- **SC-005**: Users can switch AI providers and successfully complete a query without restarting the CLI.
- **SC-006**: The CLI exits with a non-zero status code and a human-readable error message for all foreseeable error conditions (missing API key, network failure, unrecognised input).
- **SC-007**: 90% of first-time users can complete a symptom check without consulting documentation, as measured by usability testing.

## Assumptions

- Users run the CLI on a machine with Python 3.12+ and internet access to reach AI provider APIs.
- API keys for chosen providers are stored as environment variables by the user; the system does not manage key storage.
- The system is single-user and single-session; no multi-user or concurrent-session support is required for v1.
- Mobile and web interfaces are out of scope; CLI is the only delivery channel.
- Medical information quality is dependent on the underlying AI provider; the system does not independently validate clinical accuracy.
- The English language is the primary supported language for v1; non-English inputs may produce degraded results.
- Record summarization handles plain-text files only; PDF/DOCX parsing is out of scope for v1.
- Drug name recognition relies on the AI provider's knowledge; no local drug database is required for v1.
