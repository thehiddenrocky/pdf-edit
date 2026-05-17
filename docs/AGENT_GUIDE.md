# PDF Agent: Implementation & Troubleshooting Guide

This document summarizes the development journey of the PDF Editing Agent, the challenges faced, and instructions for use.

## Technical Issues & Troubleshooting

### 1. SDK Migration (Gemini -> Ollama -> llama-cpp-python)
- **Issue**: The project moved from cloud-based Gemini to local Ollama, and finally to `llama-cpp-python` for deeper integration and easier packaging in macOS apps.
- **Resolution**: Implemented the agent using `llama-cpp-python` with Apple Metal support.
    - **Amnesia Loop Fix**: Because the default `chatml-function-calling` template in `llama-cpp-python` ignores `role: tool`, we now append tool observations as `role: user` with a structured `OBSERVATION/THOUGHT` prefix to maintain the agent's memory.
    - **GPU Offloading**: Set `n_gpu_layers=-1` to ensure the model runs entirely on the Mac's GPU (M-series chips).

### 2. Migration to Native PDF Tools (Eliminating Stirling-PDF)
- **Issue**: Stirling-PDF required Docker, which is a heavy dependency for a desktop app.
- **Resolution**: Replaced the Stirling-PDF backend with native **PyMuPDF (fitz)** implementations for all operations. The engine is now 100% Python/C++ and runs entirely in-process.

### 3. Finalized API Interface
- **Issue**: To support the FastAPI sidecar and Tauri frontend, the agent needed a stable, structured return value.
- **Resolution**: The `run_agent` function in `agent.py` now returns a **Dictionary** instead of a string:
    ```json
    {
      "status": "success | error",
      "message": "The assistant's response or error details",
      "output_file": "path/to/modified.pdf | null"
    }
    ```

### 4. Ghost Text & Replacement Logic
- **Issue**: Standard PDF editing tools often "layer" new text on top of old text, leaving "ghost" artifacts visible underneath.
- **Resolution**: Created a custom `replace_text_in_pdf` tool using **PyMuPDF (fitz)**.
    - It searches for text matches.
    - It creates a redaction rectangle with a **2-pixel padding** to ensure anti-aliased edges of the original text are fully covered.
    - It applies the redaction (white fill) and then draws the new text at the same baseline.

### 5. Efficient Context Passing
- **Issue**: The agent would often enter a loop of asking "what is in the PDF?" because it didn't have the text content immediately.
- **Resolution**: Integrated `get_pdf_metadata` tool that extracts the first 500 characters and page count automatically. The agent is instructed to call this tool first.

## How to Use the Agent

### Prerequisites
1. **Metal Support**: Designed for macOS (Apple Silicon).
2. **Environment**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Model**: The model is automatically downloaded from HuggingFace on first run via `model_downloader.py`.

### Running Commands
The agent is invoked via `main.py`. It takes two arguments: the **instruction** and the **input file path**.

**Example:**
```bash
python main.py "change the name from Himanshu to Akshenndra" "original.pdf"
```

### Output
The modified files are saved in the `new/` directory. The CLI will output a structured summary including the path to the result.

## Safe Zones (GEMINI.md)
Always remember that the "BILL TO" section (Zenn Agents AI Oy) is protected by coordinate-based filters in the underlying tools to prevent accidental modification of critical business data.
