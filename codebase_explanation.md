# E-Reader Lite Codebase Explanation

Okay, let's break down the E-Reader Lite codebase. It's a classic example of a web application using a backend (Python/Flask) to serve content and handle logic, and a frontend (HTML/CSS/JavaScript) to display it and interact with the user.

### Project Structure

```
/Users/tatvadesai/Desktop/EReaderLite/
├───.gitignore          # Tells Git which files/folders to ignore (e.g., 'uploads/', '__pycache__/')
├───.replit             # Configuration file for Replit (if you're using that platform)
├───app.py              # The heart of your Python backend (Flask application)
├───requirements.txt    # Lists Python libraries your project depends on
├───static/             # Contains static files served directly to the browser
│   └───style.css       # Your application's styling
├───templates/          # Contains HTML files rendered by Flask
│   ├───index.html      # The main page for uploading PDFs
│   └───reader.html     # The PDF reading interface
└───uploads/            # Directory where uploaded PDF files are stored (created if it doesn't exist)
```

---

### 1. `app.py` (Python Backend - Flask)

This is your server-side application, built with the Flask web framework. It handles requests from the browser, processes data, and sends back responses.

*   **`from flask import ...`**: Imports necessary components from the Flask library.
*   **`import os`**: Used for interacting with the operating system, like managing file paths (`os.path.join`) and creating directories (`os.makedirs`).
*   **`import google.generativeai as genai`**: This is the library for interacting with Google's Gemini AI models.
*   **`import base64`**: Used for encoding/decoding binary data (like images) into text format for transmission over the web.

**Key Sections in `app.py`:**

*   **App Configuration (`app = Flask(__name__)`, `app.config[...]`)**:
    *   Sets up the Flask application.
    *   `UPLOAD_FOLDER`: Defines where uploaded PDFs will be saved.
    *   `ALLOWED_EXTENSIONS`: Specifies that only PDF files are allowed.
    *   `SECRET_KEY`: Used by Flask for secure session management (e.g., storing the API key).
*   **`allowed_file(filename)` function**: A helper function to check if an uploaded file has a permitted extension.
*   **Routes (`@app.route(...)`)**: These are functions that run when a specific URL is accessed by the browser.

    *   **`/` (Home Page)**:
        ```python
        @app.route('/')
        def index():
            # ... logic to check for API key and list Gemini models ...
            return render_template('index.html', ...)
        ```
        *   When you visit `http://127.0.0.1:5000/`, this function runs.
        *   It checks if a Gemini API key is set in the user's `session` (a way to store user-specific data across requests).
        *   It then renders (`render_template`) the `index.html` file, passing some data (like `api_key_set`, `models`, `selected_model`) to it.
    *   **`/upload` (File Upload)**:
        ```python
        @app.route('/upload', methods=['POST'])
        def upload_file():
            # ... handles API key from form ...
            # ... handles file upload ...
            file.save(filepath)
            return redirect(url_for('read_pdf', filename=filename))
        ```
        *   This route handles the form submission from `index.html` (when you click "Start Reading").
        *   `methods=['POST']` means it only responds to POST requests (used for sending data).
        *   It retrieves the uploaded file and the optional API key.
        *   It saves the PDF file to the `uploads/` directory.
        *   Finally, it redirects the browser to the `/read/<filename>` URL, passing the name of the uploaded file.
    *   **`/read/<filename>` (PDF Reader Page)**:
        ```python
        @app.route('/read/<filename>')
        def read_pdf(filename):
            return render_template('reader.html', filename=filename, ...)
        ```
        *   This route displays the PDF reader. The `<filename>` part is a dynamic segment, meaning whatever is in that part of the URL (e.g., `my_document.pdf`) will be passed as the `filename` argument to the function.
        *   It renders `reader.html`, passing the `filename` and any stored Gemini API key/model from the session.
    *   **`/uploads/<filename>` (Serving Uploaded Files)**:
        ```python
        @app.route('/uploads/<filename>')
        def uploaded_file(filename):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        ```
        *   This route is crucial for `pdf.js` on the frontend. When `pdf.js` needs to load the PDF file, it makes a request to this URL.
        *   `send_from_directory` securely serves the requested file from your `uploads` folder.
    *   **`/api/ocr_image` (Gemini OCR API Endpoint)**:
        ```python
        @app.route('/api/ocr_image', methods=['POST'])
        def ocr_image():
            # ... retrieves image data and prompt from frontend ...
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(gemini_model_name)
            response = model.generate_content([image_part, prompt])
            return jsonify({'processed_text': response.text})
        ```
        *   This is your backend API endpoint for OCR.
        *   It receives `POST` requests containing base64-encoded image data (a "screenshot" of a PDF page) and a text `prompt` from the frontend.
        *   It uses the `google.generativeai` library to send this image and prompt to the Gemini AI model.
        *   The response from Gemini (the OCR'd text) is then sent back to the frontend as JSON.
*   **`if __name__ == '__main__':`**: This block ensures that `app.run()` (which starts the Flask development server) only executes when `app.py` is run directly (e.g., `python app.py`), not when it's imported as a module.

---

### 2. `templates/` (HTML Frontend - Jinja2)

These are your web pages. Flask uses a templating engine called Jinja2, which allows you to embed Python-like logic directly into your HTML.

*   **`{{ variable_name }}`**: This is how you display data passed from your Flask routes (e.g., `{{ filename }}`).
*   **`{% ... %}`**: This is for control flow, like `if` statements or `for` loops (though not heavily used in your current templates).
*   **`url_for('function_name', ...)`**: A Jinja2 function that generates URLs for your Flask routes. This is good practice because if you change a route's URL, `url_for` will automatically update the links in your HTML.

**`index.html`:**
*   A simple HTML form (`<form action="/upload" method="post" enctype="multipart/form-data">`) for selecting a PDF file.
*   Includes a field for the optional Gemini API key.
*   Uses basic JavaScript to show/hide the API key input and update the file selection text.

**`reader.html`:**
This is the most complex part of the frontend.

*   **`pdf.js` Integration**:
    ```html
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"></script>
    ```
    *   These lines load the `pdf.js` library. `pdf.min.js` is the main library, and `pdf.worker.min.js` runs in a separate thread (a "web worker") to handle heavy PDF processing without freezing the browser.
    *   The JavaScript in `reader.html` then uses the `pdf.js` API to:
        *   Load the PDF file (fetched from your `/uploads/<filename>` route).
        *   Render each page onto an HTML `<canvas>` element.
        *   Attempt to extract text from the PDF's text layer.
*   **Text Display (`<div id="extracted-text-display">`)**: This is where the extracted text (either directly from the PDF or via Gemini OCR) is shown to the user.
*   **Display Settings**: JavaScript code handles changing font size, line height, margins, font family, text alignment, and themes. These settings are often saved in `localStorage` so they persist across sessions.
*   **Annotation Features**: Basic highlight and note functionality, also managed by JavaScript and `localStorage`.
*   **OCR Logic (JavaScript in `reader.html`)**:
    *   If `pdf.js` can't extract text from a page, the JavaScript captures the content of the `<canvas>` as an image (`canvas.toDataURL('image/jpeg', 0.9)`).
    *   This image data is then sent via a `fetch` request (a modern way to make HTTP requests in JavaScript) to your `/api/ocr_image` endpoint on the backend.
    *   The response (the OCR'd text) is then put into the `extracted-text-display` div.

---

### 3. `static/` (CSS)

*   **`style.css`**: Contains all the CSS rules that define the look and feel of your application (colors, fonts, layout, etc.). Flask serves these files directly.

---

### 4. `uploads/`

*   This directory is empty initially but will store all the PDF files that users upload through your application.

---

### 5. `requirements.txt`

This file lists the Python packages your Flask application needs to run.
*   `Flask`: The web framework.
*   `google-generativeai`: For interacting with the Gemini AI.

---

### How it all connects:

1.  You run `python app.py`.
2.  Your browser requests `http://127.0.0.1:5000/`.
3.  Flask's `index()` function runs, renders `index.html`, and sends it to your browser.
4.  You upload a PDF. Your browser sends a `POST` request to `/upload`.
5.  Flask's `upload_file()` function runs, saves the PDF, and tells your browser to go to `/read/your_file.pdf`.
6.  Your browser requests `/read/your_file.pdf`.
7.  Flask's `read_pdf()` function runs, renders `reader.html`, and sends it to your browser.
8.  `reader.html` loads in your browser. Its JavaScript (including `pdf.js`) starts running.
9.  `pdf.js` requests the actual PDF file from `/uploads/your_file.pdf`.
10. Flask's `uploaded_file()` function serves the PDF to `pdf.js`.
11. `pdf.js` renders the PDF pages. If it can't extract text, its JavaScript sends an image of the page to `/api/ocr_image`.
12. Flask's `ocr_image()` function receives the image, sends it to Gemini, gets the text, and sends it back to the browser.
13. The JavaScript in `reader.html` receives the OCR'd text and displays it.

This architecture separates concerns: Python handles the server-side logic and API calls, while JavaScript handles the interactive user interface and PDF rendering in the browser.
