# Setup Guide

To use the full capabilities of the PDF Editing suite, you need to set up two main components: the Python environment and a local LLM.

## 1. Python Environment

It is recommended to use a virtual environment.

```bash
# Create and activate venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Key Dependencies:**
- `PyMuPDF (fitz)`: For low-level PDF manipulation.
- `ollama`: For local LLM orchestration.
- `python-dotenv`: For environment variable management.

*(Optional)* **OCR Support:**
To use the `ocr_pdf` tool, you must have Tesseract-OCR installed on your system.
- **macOS**: `brew install tesseract`
- **Ubuntu**: `sudo apt install tesseract-ocr`

## 2. Local LLM (Ollama)

The AI Agent uses **Gemma** running locally via Ollama.

1. Install [Ollama](https://ollama.com/).
2. Pull the model used in `agent.py`:
   ```bash
   ollama pull gemma4:e2b
   ```
   *(Note: Ensure the model name in `agent.py` matches what you have downloaded.)*

