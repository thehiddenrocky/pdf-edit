# PDF Agent: Implementation & Troubleshooting Guide

This document summarizes the development journey of the PDF Editing Agent, the challenges faced, and instructions for use.

## Technical Issues & Troubleshooting

### 1. SDK Migration (google-generativeai to google-genai)
- **Issue**: The original project used the older `google-generativeai` package, which had compatibility issues with the latest Python environment and lacked some modern feature support.
- **Troubleshooting**: Identified that `google-genai` is the official modern SDK. 
- **Resolution**: Updated `requirements.txt` and refactored `agent.py` to use the `genai.Client` and `client.chats.create` methods. This improved tool-calling reliability and state management.

### 2. Stirling-PDF API Schema Fixes (422 Errors)
- **Issue**: Calls to the Stirling-PDF Orchestrator returned `422 Unprocessable Entity`.
- **Troubleshooting**: Inspected the Pydantic error logs. Discovered Stirling's API rejects the `pageCount` field inside the `files` array when sent as input, despite their own metadata tools returning it.
- **Resolution**: Modified `tools.py` to explicitly strip `pageCount` from the file metadata before sending the payload.

### 3. Stirling-PDF "Outcome: cannot_do"
- **Issue**: The agent API would return success but with a `cannot_do` outcome, indicating it didn't know how to proceed.
- **Troubleshooting**: Realized the `enabledEndpoints` list was empty. The Stirling orchestrator requires a whitelist of tools it is allowed to invoke.
- **Resolution**: Hardcoded a set of valid Stirling endpoints (e.g., `add-text`, `add-image`, `set-metadata`) in the request payload.

### 4. Ghost Text & Replacement Logic
- **Issue**: Standard PDF editing tools often "layer" new text on top of old text, leaving "ghost" artifacts visible underneath. Additionally, Stirling's native API lacked a robust "search and replace" function.
- **Troubleshooting**: PDF text isn't stored in a flow; it's positioned at coordinates. To replace it, you must "erase" the area first.
- **Resolution**: Created a custom `replace_text_in_pdf` tool using **PyMuPDF (fitz)**.
    - It searches for text matches.
    - It creates a redaction rectangle with a **2-pixel padding** to ensure anti-aliased edges of the original text are fully covered.
    - It applies the redaction (white fill) and then draws the new text at the same baseline.

### 5. Efficient Context Passing (Artifacts)
- **Issue**: The agent would often enter a loop of asking "what is in the PDF?" because it didn't have the text content immediately.
- **Troubleshooting**: Stirling supports an `artifacts` field in the payload to provide pre-extracted data.
- **Resolution**: Integrated PyMuPDF text extraction directly into the `apply_pdf_edits` tool. Every request now sends the PDF's text content as an "extracted_text" artifact, allowing the LLM to make decisions in a single turn.

## How to Use the Agent

### Prerequisites
1. **API Key**: Ensure you have a `.env` file in the root directory with:
   ```env
   GEMINI_API_KEY=your_google_ai_studio_key_here
   ```
2. **Stirling-PDF**: Ensure Stirling-PDF is running locally (default: `http://localhost:5001`).
3. **Environment**: Use the provided virtual environment.
   ```bash
   source ./venv/bin/activate
   pip install -r requirements.txt
   ```

### Running Commands
The agent is invoked via `main.py`. It takes two arguments: the **instruction** and the **input file path**.

**Example: Change a name**
```bash
python main.py "change the name from Himanshu to Akshenndra everywhere" "original/20 Feb-Himanshu.pdf"
```

**Example: Change a date**
```bash
python main.py "change the invoice date to August 2026" "original/20 Feb-Himanshu.pdf"
```

### Output
The modified files are saved in the `new/` directory, maintaining the original filename.

## Safe Zones (GEMINI.md)
Always remember that the "BILL TO" section (Zenn Agents AI Oy) is protected by coordinate-based filters in the underlying tools to prevent accidental modification of critical business data.
