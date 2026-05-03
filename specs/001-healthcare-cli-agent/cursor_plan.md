# Cursor Plan - Medical Record Summarization

## Overview
Implement medical record summarization per SPEC.md 
User Story 2 and FR-004: LlamaIndex-based in-memory 
chunking (no index/vector store), map-reduce 
summarization via the existing AI provider abstraction.

## 4 To-dos
1. Add src/ package layout, pyproject scripts + deps
2. Implement src/models/records.py and 
   src/services/summarizer.py (LlamaIndex in-memory 
   chunking, map-reduce, JSON parse to RecordSummary)
3. Wire summarize: --file/--input, --provider, 
   UTF-8 read + errors, exit codes; no disk persistence
4. Add tests