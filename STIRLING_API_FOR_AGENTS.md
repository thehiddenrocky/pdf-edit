# Stirling-PDF AI Engine: External Agent Integration Guide

This guide provides the necessary information for an AI agent to interface with the **Stirling-PDF Python AI Engine**.

## 1. Connection Details

- **Base URL**: `http://localhost:5001`
- **Interactive Documentation (Swagger UI)**: `http://localhost:5001/docs`
- **Raw OpenAPI Spec**: `http://localhost:5001/openapi.json`

## 2. Core Concept
The Python Engine is a **reasoning service**. It plans workflows and interprets user intent but does **not** execute the actual PDF operations (that is handled by the Java backend). An agent should call the Engine to get a "plan" or "answer," and then potentially pass that plan back to a system that can execute Java-based tools.

## 3. Key Endpoints

### A. Orchestrator (`POST /api/v1/orchestrator`)
The main entry point for general PDF tasks. Use this for complex requests involving multiple steps.

**Request Schema (`OrchestratorRequest`):**
```json
{
  "user_message": "string",
  "files": [
    {
      "id": "uuid-string",
      "name": "filename.pdf",
      "page_count": 0
    }
  ],
  "conversation_history": [],
  "enabled_endpoints": []
}
```

### B. PDF Questions (`POST /api/v1/pdf-questions`)
Specialized endpoint for "Chat with PDF" functionality.

**Request Schema (`PdfQuestionRequest`):**
```json
{
  "question": "What is the summary of this document?",
  "files": [...]
}
```

### C. PDF Edit (`POST /api/v1/pdf-edit`)
For requests specifically about modifying a PDF (merging, splitting, rotating, etc.).

## 4. Environment Requirements
The Python Engine requires access to an LLM to function. Ensure the following are set in the environment where the server is running:
- `ANTHROPIC_API_KEY` (Recommended)
- `OPENAI_API_KEY` (Alternative)

## 5. Usage for External Agents
If you are an agent trying to use these tools:
1. **Health Check**: Run `curl http://localhost:5001/health` to ensure the service is up.
2. **Consult Docs**: Fetch the full tool definitions from `http://localhost:5001/openapi.json`.
3. **Execute**: Send the user's natural language request to `/api/v1/orchestrator` along with metadata about the files being processed.
