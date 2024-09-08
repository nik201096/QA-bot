from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from utils.file_utils import read_pdf, read_docx, read_txt, extract_text_from_image
from utils.RAG import rag_system, add_document
from main import process_files_from_source

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpeg', 'png', 'jpg'}
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save the uploaded file to the upload folder."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path
    return None

def process_links(input_links):
    """Process files from provided URLs."""
    links = input_links.split(',')
    output = ""

    for url in links:
        files = process_files_from_source(url.strip())
        if files:
            for file_bytes, file_name in files:
                if file_name.endswith('.pdf'):
                    output += read_pdf(file_bytes)
                elif file_name.endswith('.docx'):
                    output += read_docx(file_bytes)
                elif file_name.endswith('.txt'):
                    output += read_txt(file_bytes)
                elif file_name.endswith(('.jpeg', '.png', '.jpg')):
                    output += extract_text_from_image(file_bytes)
                output += "\n" + "-"*50 + "\n"
        else:
            return f"Failed to process files from {url}"

    add_document(text=output)
    return "Document added successfully. You can now ask questions related to the document."

def clean_upload_folder():
    """Remove all files from the upload folder."""
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/')
def index():
    """Render the file upload and link processing form."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """Handle file upload or link processing."""
    if 'file' in request.files and request.files['file']:
        file = request.files['file']
        if allowed_file(file.filename):
            saved_file_path = save_uploaded_file(file)
            if saved_file_path:
                result = process_links(saved_file_path)
                clean_upload_folder()  # Clean up the upload folder
                return render_template('result.html', result=result)
            else:
                flash('File not allowed')
        else:
            flash('Invalid file type')
    elif 'links' in request.form and request.form['links']:
        input_links = request.form['links']
        result = process_links(input_links)
        clean_upload_folder()  # Clean up the upload folder
        return render_template('result.html', result=result)
    else:
        flash('No file or links provided')
    
    return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def query():
    """Handle the user's query."""
    query = request.form['query']
    response = rag_system(query)
    return render_template('result.html', result=response)

if __name__ == '__main__':
    app.run(debug=True)
