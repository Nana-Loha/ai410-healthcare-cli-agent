\# AI410 — Healthcare CLI Agent Project



\## Project Overview

A CLI-based AI agent for healthcare domain tasks including symptom checking,

medical record summarization, and drug interaction checking.



\## Tech Stack

\- Python 3.12+

\- uv (package manager)

\- anthropic (Claude API)

\- openai (GPT API)

\- google-generativeai (Gemini API)

\- langgraph (agent workflows)

\- llama-index (document indexing)



\## Development Conventions

\- Use `uv` only — never pip

\- Tests go in /tests directory

\- Use pytest for all tests

\- One feature per branch



\## Agent Behavior Guidelines

\- Always ask for confirmation before taking irreversible actions

\- Never store or log patient data

\- Always cite sources for medical information

\- Include disclaimer: "Not a substitute for professional medical advice"


<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/001-healthcare-cli-agent/plan.md
<!-- SPECKIT END -->
