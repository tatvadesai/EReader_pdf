# E-Reader Lite

A lightweight PDF reader for the browser with local AI-powered OCR for scanned documents.

## Features

- Page-by-page PDF rendering via pdf.js
- Text extraction from PDF text layer (layout-aware, handles columns)
- Local OCR for scanned PDFs using GLM-OCR via Ollama
- Display settings: font size, line spacing, margins, font family, alignment
- Themes: light, sepia, dark
- Highlight and annotation support
- Settings persisted in localStorage

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080

### For scanned PDF support

Install [Ollama](https://ollama.com) and pull the OCR model:

```bash
ollama pull glm-ocr
ollama serve
```

The upload page shows a green dot when OCR is ready.

## Dependencies

- Python: `Flask`, `requests`
- OCR: [Ollama](https://ollama.com) + `glm-ocr` (0.9B params, ~1.6GB)
- Frontend: pdf.js (CDN)

## Configuration

| Env var | Default | Description |
|---|---|---|
| `PORT` | `8080` | Server port |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API URL |
| `OCR_MODEL` | `glm-ocr` | Ollama model for OCR |
