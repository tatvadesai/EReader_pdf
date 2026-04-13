from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import base64
import requests as http_requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SECRET_KEY'] = os.urandom(24)

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OCR_MODEL = os.getenv('OCR_MODEL', 'glm-ocr')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def ocr_page(image_b64):
    """Send page image to GLM-OCR for text extraction."""
    prompt = (
        "Extract all text from this book page image. "
        "Preserve the original layout, paragraph breaks, and formatting. "
        "If this is an index or table of contents, maintain the entry and page number alignment. "
        "If this is a preface or introduction, maintain paragraph structure. "
        "Output only the extracted text."
    )
    resp = http_requests.post(
        f'{OLLAMA_URL}/api/generate',
        json={
            'model': OCR_MODEL,
            'prompt': prompt,
            'images': [image_b64],
            'stream': False
        },
        timeout=120
    )
    if resp.status_code == 200:
        return resp.json().get('response', '')
    raise Exception(f"OCR model returned {resp.status_code}")


# --- Routes ---

@app.route('/')
def index():
    ocr_ready = False
    try:
        r = http_requests.get(f'{OLLAMA_URL}/api/tags', timeout=2)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            ocr_ready = any(OCR_MODEL.split(':')[0] in m for m in models)
    except Exception:
        pass
    return render_template('index.html', ocr_ready=ocr_ready, ocr_model=OCR_MODEL)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename.replace(' ', '_')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('read_pdf', filename=filename))
    return 'Invalid file type'


@app.route('/read/<filename>')
def read_pdf(filename):
    return render_template('reader.html', filename=filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/ocr', methods=['POST'])
def ocr():
    """OCR endpoint using GLM-OCR."""
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify({'error': 'No image data'}), 400

    try:
        text = ocr_page(data['image_data'])
        return jsonify({'text': text or 'No text detected on this page.'})
    except Exception as e:
        print(f"OCR error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def status():
    ocr_ready = False
    try:
        r = http_requests.get(f'{OLLAMA_URL}/api/tags', timeout=2)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            ocr_ready = any(OCR_MODEL.split(':')[0] in m for m in models)
    except Exception:
        pass
    return jsonify({'ocr_ready': ocr_ready, 'ocr_model': OCR_MODEL})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 8080), debug=True)
