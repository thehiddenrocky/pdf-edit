# macOS Desktop App Transition Plan

## Overview
This document outlines the step-by-step technical plan to transition the existing CLI-based PDF Editor into a standalone, 1-click installable macOS desktop application (`.dmg`).

The core goal is to eliminate all external system requirements (Docker, Ollama background daemons, Python environments) so that the end-user simply downloads the app and runs it, leveraging Apple Silicon (Metal) for fast, local AI inference.

---

## Target Architecture

*   **Frontend (UI):** Tauri + React (or Vue/Vanilla JS). Lightweight, native macOS window.
*   **Backend (Sidecar):** A local FastAPI server compiled into a single executable via PyInstaller.
*   **AI Engine:** `llama-cpp-python` compiled with Apple Metal support, embedded directly inside the Python sidecar.
*   **Model Management:** Dynamic `.gguf` file downloading on first launch (to keep the `.dmg` size small).
*   **PDF Engine:** Pure `PyMuPDF` (fitz) running inside the Python backend.

---

## Refactoring & Implementation Phases

### Phase 1: AI Engine Refactor (Moving away from Ollama)
**Goal:** Remove the dependency on the `ollama` daemon and run the LLM in-process.
1.  **Replace SDK:** Remove `ollama` from `requirements.txt`. Add `llama-cpp-python` and `huggingface-hub`.
2.  **Model Downloader:** Write a script to dynamically download a Gemma GGUF file (e.g., `gemma-2-2b-it-Q4_K_M.gguf`) from HuggingFace to `~/.pdf-edit-app/models/` if it doesn't already exist.
3.  **Agent Update:** Modify `agent.py` to instantiate `Llama()` with `n_gpu_layers=-1` (for full Metal offloading). Replace `ollama.chat()` with `llm.create_chat_completion()`. 
4.  *Test:* Verify the CLI script still works natively without Ollama running.

> **Technical Note: Resolving the Tool "Amnesia Loop"**
> During implementation, an infinite loop was discovered where the model repeatedly calls the same tool.
> * **Root Cause:** The `chatml-function-calling` chat template built into `llama-cpp-python` explicitly ignores messages with `role: "tool"`. The LLM never sees the tool output, assumes the tool hasn't been executed, and therefore requests the same tool call again indefinitely.
> * **Proposed Solutions:**
>   1. **Fake the Role (Recommended/Easiest):** Append the tool's output as a `role: "user"` message (e.g., `{"role": "user", "content": "Tool Response: {...}"}`) so the existing template successfully renders it into the LLM's context window.
>   2. **Monkey-Patch the Template:** Inject a custom Jinja template via `llama_chat_format.Jinja2ChatFormatter` during the `Llama` initialization that properly handles `{% if message.role == 'tool' %}`.
>   3. **Change Chat Format:** Evaluate if a different built-in template natively supports tool roles for Gemma 2.

### Phase 2: PDF Engine Refactor (Moving away from Stirling-PDF)
**Goal:** Eliminate the need for Docker and the Stirling-PDF backend.
1.  **Audit Tools:** Review `apply_pdf_edits` in `tools.py`.
2.  **Native Implementation:** Rewrite any high-level operations (merge, split, OCR) currently sent to `http://localhost:5001` to use native `PyMuPDF` or other pure-Python libraries.
3.  *Test:* Verify that `tools.py` can execute all required PDF edits entirely locally.

### Phase 3: The API Sidecar (FastAPI)
**Goal:** Wrap the Python logic into a local web server that the UI can communicate with.
1.  **Setup FastAPI:** Create `api.py` using FastAPI.
2.  **Endpoints:**
    *   `GET /status`: Returns model download progress or readiness state.
    *   `POST /download`: Triggers the GGUF model download.
    *   `POST /edit`: Accepts a PDF file path and a user prompt, runs the ReAct loop (`agent.py`), and returns the edited PDF path.
3.  *Test:* Run the Uvicorn server locally and hit the endpoints using `curl` or Postman to successfully edit a PDF.

### Phase 4: Frontend Development (Tauri)
**Goal:** Build the native macOS user interface.
1.  **Initialize:** Run `npm create tauri-app@latest` in a new `/ui` directory.
2.  **Design UI:** Create a simple interface:
    *   First launch screen: "Downloading AI Core..." (hooks into `/status`).
    *   Main screen: Drag-and-drop zone for PDF, text input for instructions, and "Process" button.
3.  **Sidecar Configuration:** Configure `tauri.conf.json` to define the Python backend as a "sidecar" executable. Tauri will manage starting and killing this process automatically.

### Phase 5: Packaging & CI/CD (The Final Build)
**Goal:** Produce the distributable `.dmg` file.
1.  **Freeze Python:** Use `PyInstaller` on a Mac to compile the FastAPI server into a single binary. Ensure `CMAKE_ARGS="-DGGML_METAL=on"` is used during the pip install of `llama-cpp-python` before freezing, so the Metal GPU bindings are packaged.
2.  **Tauri Build:** Run `tauri build`. This will wrap the React UI and the PyInstaller binary into `PDF Editor.app` and `PDF Editor.dmg`.
3.  *(Optional)* **GitHub Actions:** Create a `.yml` workflow to automate this build process on a `macos-latest` cloud runner whenever code is pushed.

---

## Known Risks & Mitigations
*   **App Size:** Embedding Python and C++ libraries via PyInstaller will make the sidecar ~100MB-200MB. *Mitigation:* Ensure we do not package the 2GB+ AI model; always download the `.gguf` dynamically on first launch.
*   **macOS Gatekeeper:** Unsigned apps will show a warning on Mac. *Mitigation:* Document how users can right-click -> Open, or eventually sign the app with an Apple Developer account (`codesign` / `notarytool`).
*   **Context Limit:** The GGUF model will be loaded into the user's unified memory. *Mitigation:* Start with a 2B parameter model (requires ~2-3GB of RAM) to ensure it runs comfortably on base M1/M2/M3 Macs with 8GB RAM.