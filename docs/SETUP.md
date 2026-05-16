# Setup Guide

To use the full capabilities of the PDF Editing suite, you need to set up three main components: the Python environment, a local LLM, and the Stirling-PDF backend.

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
- `requests`: For communicating with the Stirling-PDF API.
- `python-dotenv`: For environment variable management.

## 2. Local LLM (Ollama)

The AI Agent uses **Gemma** running locally via Ollama.

1. Install [Ollama](https://ollama.com/).
2. Pull the model used in `agent.py`:
   ```bash
   ollama pull gemma4:e2b
   ```
   *(Note: Ensure the model name in `agent.py` matches what you have downloaded.)*

## 3. Stirling-PDF Backend

Stirling-PDF provides the orchestration layer for complex PDF operations.

1. Ensure you have Docker installed.
2. Run Stirling-PDF (Python AI Engine version):
   ```bash
   docker run -d \
     -p 5001:5001 \
     -e ANTHROPIC_API_KEY=your_key_here \
     stirlingtools/stirling-pdf:latest-ai
   ```
   *Note: While the agent uses local Gemma for logic, the Stirling backend itself may require an API key for its internal reasoning if you use its high-level endpoints.*

3. Verify it's running:
   ```bash
   curl http://localhost:5001/health
   ```

## 4. Configuration

Create a `.env` file in the root directory:

```env
# Optional: If you use cloud-based models in Stirling
ANTHROPIC_API_KEY=sk-...
```
