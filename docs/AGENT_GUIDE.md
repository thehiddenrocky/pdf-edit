# PDF Agent: Implementation & Troubleshooting Guide

This document summarizes the development journey of the PDF Editing Agent, the challenges faced, and instructions for use.

## Technical Issues & Troubleshooting

### 1. SDK Migration (Gemini to local Gemma via Ollama)
- **Issue**: The project originally used the `google-genai` SDK, which required a cloud API key and internet connectivity.
- **Resolution**: Migrated to the `ollama` Python library to run the agent using a local **Gemma** model. This involved:
    - Implementing a manual ReAct loop to handle tool calling (which Gemini's SDK handled internally).
    - Mapping tool definitions to the JSON format expected by Ollama's `chat` API.
    - Setting the `MODEL_NAME` to `gemma` in `agent.py`.

### 2. Migration to Native PDF Tools (Eliminating Stirling-PDF)
- **Issue**: Stirling-PDF required Docker and had complex API requirements, making it difficult for local deployment and 1-click app packaging.
- **Resolution**: Replaced the Stirling-PDF backend with native **PyMuPDF (fitz)** implementations for all operations:
    - **Merge**: `merge_pdfs` (Native)
    - **Split**: `split_pdf` (Native)
    - **Rotate/Remove**: `rotate_pdf_pages`, `remove_pdf_pages` (Native)
    - **OCR**: `ocr_pdf` (Native via Tesseract integration)
- **Benefit**: No more Docker dependency. The entire engine is now pure Python.

### 4. Ghost Text & Replacement Logic
- **Issue**: Standard PDF editing tools often "layer" new text on top of old text, leaving "ghost" artifacts visible underneath.
- **Troubleshooting**: PDF text isn't stored in a flow; it's positioned at coordinates. To replace it, you must "erase" the area first.
- **Resolution**: Created a custom `replace_text_in_pdf` tool using **PyMuPDF (fitz)**.
    - It searches for text matches.
    - It creates a redaction rectangle with a **2-pixel padding** to ensure anti-aliased edges of the original text are fully covered.
    - It applies the redaction (white fill) and then draws the new text at the same baseline.

### 5. Efficient Context Passing
- **Issue**: The agent would often enter a loop of asking "what is in the PDF?" because it didn't have the text content immediately.
- **Resolution**: Integrated `get_pdf_metadata` tool that extracts the first 500 characters and page count automatically. The agent is instructed to call this tool first.

## How to Use the Agent

### Prerequisites
1. **Ollama**: Ensure Ollama is installed and running locally.
   - Pull the model: `ollama pull gemma4:e2b`
2. **Environment**: Use the provided virtual environment.
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
