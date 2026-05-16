# PDF Edit Documentation

Welcome to the PDF Edit project documentation. This project provides a suite of tools for both automated and AI-driven PDF editing, specifically focused on invoices and resumes.

## Documentation Index

### 1. [Getting Started](SETUP.md)
Learn how to set up your environment, including local LLMs (Ollama) and the Stirling-PDF backend.

### 2. [Scripts Overview](SCRIPTS.md)
A comprehensive guide to every script in the repository, explaining when to use batch processing vs. the AI agent.

### 3. [Redaction & Editing Strategy](REDACTION_STRATEGY.md)
Deep dive into the "Wipe-then-Print" methodology, coordinate targeting, and font management.

### 4. [AI Agent Guide](AGENT_GUIDE.md)
Detailed information about the ReAct agent loop, tool definitions, and troubleshooting common LLM issues.

### 5. [Stirling-PDF Integration](../STIRLING_API_FOR_AGENTS.md)
Reference for connecting to the Stirling-PDF AI Engine.

---

## Quick Start (AI Agent)
```bash
python main.py "change the name to Mary Garg" "original/invoice.pdf"
```

## Quick Start (Batch Processing)
```bash
python edit_pdfs.py
```
