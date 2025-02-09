from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename
from services.form_json_services import load_questions_from_json

app = Flask(__name__, 
    static_folder='static',    
    template_folder='templates'
)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_evaluation_form_schema(data):
    """Validate the AWS Connect evaluation form schema"""
    required_fields = {'Items'}
    
    if not all(field in data for field in required_fields):
        return False, "Missing required fields in evaluation form"
        
    sections = data.get('Items', [])
    if not sections or not isinstance(sections, list):
        return False, "Items must be a non-empty list"
        
    for section in sections:
        print(section)
        if 'Section' not in section :
            return False, "Each section must have Items"
            
        items = section.get('Items', [])
        if not isinstance(items, list):
            return False, "items must be a list"
            
        for question in items:
            if 'Title' not in question:
                return False, "Each question must have Title"
                
    return True, "Valid schema"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload-questions', methods=['POST'])
def upload_questions():
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
        
    if file and file.filename.endswith('.json'):
        try:
            # Read and parse JSON content
            content = json.loads(file.read().decode('utf-8'))
            print(content)
            question_detail_content = load_questions_from_json(content)
                
            return jsonify({
                "status": "success",
                # "filename": filename,
                "content": question_detail_content,
                "message": "Evaluation form loaded successfully"
            })
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON file format"
            }), 400
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    else:
        return jsonify({
            "status": "error",
            "message": "Only .json files are allowed for evaluation forms"
        }), 400

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

@app.route('/api/submit-evaluation', methods=['POST'])
def submit_evaluation():
    data = request.form.to_dict()
    transcript_content = None
    
    # Handle transcript file if present
    if 'transcript' in request.files:
        file = request.files['transcript']
        if file and file.filename.endswith('.txt'):
            try:
                transcript_content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                return jsonify({
                    "status": "error",
                    "message": "Transcript must be a valid text file with UTF-8 encoding"
                }), 400
    
    # Process the evaluation data
    evaluation_data = {
        'timestamp': datetime.now().isoformat(),
        'transcript': transcript_content,
        'evaluationAnswers': {
            'sections': []
        }
    }
    
    # Process sections and questions
    current_section = None
    section_questions = []
    
    for key, value in sorted(data.items()):
        if key.startswith('section_'):
            if current_section and section_questions:
                evaluation_data['evaluationAnswers']['sections'].append({
                    'sectionName': current_section,
                    'questions': section_questions
                })
                section_questions = []
            current_section = value
        elif key.startswith('question_'):
            section_questions.append({
                'questionText': data.get(f'questionText_{key.split("_")[1]}'),
                'answer': value
            })
    
    # Add the last section
    if current_section and section_questions:
        evaluation_data['evaluationAnswers']['sections'].append({
            'sectionName': current_section,
            'questions': section_questions
        })
    
    return jsonify({
        "status": "success",
        "data": evaluation_data,
        "message": "Evaluation submitted successfully"
    }), 201


@app.route('/api/ask-ai', methods=['POST'])
def submit_ask_ai():
    data = request.form.to_dict()
    data['question']

    return jsonify({
        "status": "success",
        "data": data['question'],
        "message": "Evaluation submitted successfully"
    }), 201
if __name__ == '__main__':
    app.run(debug=True)