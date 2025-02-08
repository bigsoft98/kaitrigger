from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from services.ai_services import talk_2_ai
 
app = Flask(__name__,
    static_folder='static',   
    template_folder='templates'
)
CORS(app)
 
# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
 
# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 

documents = []  # Store document submissions
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def index():
    return render_template('index.html')
 

@app.route('/api/upload-text', methods=['POST'])
def upload_text_file():
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file part"
        }), 400
   
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No selected file"
        }), 400
       
    if file and file.filename.endswith('.txt'):
        try:
            content = file.read().decode('utf-8')
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
               
            return jsonify({
                "status": "success",
                "filename": filename,
                "content": content,
                "message": "File uploaded and read successfully"
            })
        except UnicodeDecodeError:
            return jsonify({
                "status": "error",
                "message": "File must be a valid text file with UTF-8 encoding"
            }), 400
    else:
        return jsonify({
            "status": "error",
            "message": "Only .txt files are allowed for text reading"
        }), 400
 
@app.route('/api/submit-request', methods=['POST'])
def submit_document():
    data = request.form.to_dict()
   
    # Handle file if present
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename.endswith('.txt'):
            try:
                transcript_content = file.read().decode('utf-8')
                data['transcript_content'] = transcript_content
                # data['filename'] = secure_filename(file.filename)
 
            except UnicodeDecodeError:
                return jsonify({
                    "status": "error",
                    "message": "File must be a valid text file with UTF-8 encoding"
                }), 400
   
    # Store the submission
    document_id = len(documents) + 1
    data['id'] = document_id
    data['timestamp'] = datetime.now().isoformat()
    ai_response = talk_2_ai(transcript=transcript_content,contact_evaluate_question=data['question'],contact_evaluate_question_instruction=data['instruction'])
    data['ai_response'] = ai_response
    documents.append(data)
   
    response_data = {}
    response_data['ai_response'] = ai_response
 

    return jsonify({
        "status": "success",
        "question": data['question'],
        "instruction": data['instruction'],
        "AI_answer": response_data
    }), 201



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404
 
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
 
if __name__ == '__main__':
    app.run(debug=True)