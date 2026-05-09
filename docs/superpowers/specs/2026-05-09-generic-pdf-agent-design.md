# PDF Editing Agent Backend Design

## Overview
A lightweight Python backend for an AI agent capable of editing PDFs generically. The agent uses the Gemini API as its core reasoning engine and executes edits by calling tools that interface with the local Stirling-PDF AI Engine backend.

## Architecture
- **Brain / LLM**: Custom ReAct loop using the raw Google GenAI SDK (Gemini).
- **Tool Execution**: Python functions mapped as LLM tools, which execute HTTP REST requests to the Stirling-PDF backend.
- **Data Flow**:
  1. User inputs a prompt and PDF file path.
  2. The custom loop queries Gemini with the prompt and available tools.
  3. Gemini returns a tool call (if needed).
  4. The script executes the tool (e.g., calling Stirling API) and feeds the result back to Gemini.
  5. Gemini formulates the final response for the user.

## Tools (MVP)
1. `get_pdf_metadata(filepath)`: Inspects the PDF (page count, text) to understand context before editing.
2. `apply_pdf_edits(filepath, edit_instructions)`: Submits edit commands (e.g., text replacements) to the Stirling backend to generate the modified PDF.

## Error Handling
Tool failures (e.g., Stirling server unreachable) are caught and returned as natural language strings to the LLM. This allows the LLM to gracefully inform the user or self-correct, preventing script crashes.

## Modularity & Future-Proofing
To support the eventual transition to a Desktop app using a local Gemma model:
- `tools.py`: Stirling API wrappers.
- `agent.py`: LLM core loop logic (easily swappable to Gemma API later).
- `main.py`: CLI entry point.
