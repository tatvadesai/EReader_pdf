# E-Reader Lite

A lightweight Flask web app for reading PDFs in the browser with customizable display settings and local OCR for scanned documents via Ollama + GLM-OCR.

## Quick Start

```bash
pip install -r requirements.txt
ollama pull glm-ocr        # for scanned PDF support
ollama serve               # start Ollama in another terminal
python app.py              # runs on http://localhost:8080
```

## Architecture

- **Backend**: Flask (`app.py`) - PDF upload, file serving, OCR endpoint
- **Frontend**: Jinja2 templates + vanilla JS with pdf.js for rendering
- **OCR**: GLM-OCR (0.9B) via Ollama for scanned PDFs

## Key Routes

| Route | Purpose |
|---|---|
| `GET /` | Upload page |
| `POST /upload` | Save PDF, redirect to reader |
| `GET /read/<filename>` | Reader view |
| `GET /uploads/<filename>` | Serve PDF files to pdf.js |
| `POST /api/ocr` | OCR endpoint (accepts base64 JPEG, returns text) |
| `GET /api/status` | Ollama/model health check |

## Project Structure

```
app.py              # Flask app (~70 lines)
templates/
  index.html        # Upload page
  reader.html       # PDF reader (pdf.js, display settings, annotations)
static/
  style.css         # All styling (themes: light, sepia, dark)
uploads/            # Uploaded PDFs (gitignored)
requirements.txt    # Flask, requests
```

## Dependencies

- `Flask` - web framework
- `requests` - Ollama HTTP client
- `Ollama` + `glm-ocr` - local OCR (optional, only needed for scanned PDFs)

## How OCR Works

1. pdf.js tries to extract text from the PDF text layer
2. If no text layer (scanned page), the page canvas is captured as JPEG
3. Image is sent to `/api/ocr` which forwards to GLM-OCR via Ollama
4. Extracted text is displayed in the reader

## Dev Notes

- `SECRET_KEY` is generated with `os.urandom(24)` on each restart
- Uploaded files are saved with spaces replaced by underscores
- The app binds to `0.0.0.0:8080` (or `$PORT`)
- OCR model is configurable via `OCR_MODEL` env var
