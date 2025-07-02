from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify
import os
import google.generativeai as genai
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SECRET_KEY'] = os.urandom(24) # Used for session management

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    api_key_set = 'gemini_api_key' in session
    models = []
    if api_key_set:
        try:
            genai.configure(api_key=session.get('gemini_api_key'))
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
        except Exception as e:
            print(f"Error listing models: {e}")
            # If there's an error, clear the API key to prompt user to re-enter
            session.pop('gemini_api_key', None)
            api_key_set = False

    selected_model = session.get('gemini_model', 'gemini-pro-vision')
    return render_template('index.html', api_key_set=api_key_set, models=models, selected_model=selected_model)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check for optional API key
    api_key = request.form.get('api_key')
    if api_key:
        session['gemini_api_key'] = api_key
        # Always use the vision model when a key is provided
        session['gemini_model'] = 'gemini-pro-vision'
    else:
        # Clear any old key if the user is doing a standard upload
        session.pop('gemini_api_key', None)
        session.pop('gemini_model', None)

    # Standard file handling
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
    # Pass API key and model to the client-side. 
    # The template handles cases where these are not set in the session.
    return render_template('reader.html', 
                           filename=filename, 
                           gemini_api_key=session.get('gemini_api_key'),
                           gemini_model=session.get('gemini_model'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(f"[DEBUG] Attempting to serve file: {filename} from {app.config['UPLOAD_FOLDER']}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/ocr_image', methods=['POST'])
def ocr_image():
    gemini_api_key = session.get('gemini_api_key')
    gemini_model_name = session.get('gemini_model')
    if not gemini_api_key or not gemini_model_name:
        return jsonify({'error': 'Gemini API Key or Model not set.'}), 400

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(gemini_model_name)

    data = request.get_json()
    image_data_base64 = data.get('image_data')
    prompt = data.get('prompt')

    if not image_data_base64 or not prompt:
        return jsonify({'error': 'Missing image_data or prompt.'}), 400

    try:
        image_bytes = base64.b64decode(image_data_base64)
        image_part = {
            'mime_type': 'image/jpeg',
            'data': image_bytes
        }
        
        response = model.generate_content([image_part, prompt])
        return jsonify({'processed_text': response.text}), 200
    except Exception as e:
        print(f"Error processing image with Gemini: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=True)