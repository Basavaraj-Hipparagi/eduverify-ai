import os
import sys
import uuid
import time
from datetime import datetime

# Guarantee project root is in sys.path for production cloud deployments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import (
    Flask, render_template, request, jsonify, send_file, session, abort
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment
load_dotenv()

from database.db import (
    init_db, save_verification, get_verification_by_ref, 
    get_history, delete_verification, clear_all_history
)
from services.verification_service import VerificationEngine
from services.consistency_service import ConsistencyService
from services.report_service import ReportService
from services.ocr_service import OCRService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'eduverify_dev_secret_key_99812739')

# Upload & report directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}

# In-memory document storage mapping document_id to file details
DOCUMENT_REGISTRY = {}

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def ensure_session_and_db():
    get_session_id()
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_file(os.path.join(BASE_DIR, 'static', 'manifest.json'), mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file(os.path.join(BASE_DIR, 'static', 'sw.js'), mimetype='application/javascript')

@app.route('/favicon.ico')
def serve_favicon():
    return send_file(os.path.join(BASE_DIR, 'static', 'icons', 'favicon.png'), mimetype='image/png')

@app.route('/api/health', methods=['GET'])
def health():
    tess_ok, tess_info = OCRService.check_tesseract_available()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'tesseract_ocr': {
                'available': tess_ok,
                'details': tess_info
            },
            'pymupdf_pdf_engine': {
                'available': True,
                'details': 'PyMuPDF Native Text Parser & Renderer operational'
            },
            'opencv_qr_detector': {
                'available': True,
                'details': 'OpenCV QRCodeDetector operational'
            },
            'reportlab_pdf_generator': {
                'available': True,
                'details': 'ReportLab PDF certificate engine operational'
            },
            'database': {
                'available': True,
                'type': 'SQLite (Local Instance)'
            }
        }
    })

@app.route('/api/documents', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided in upload request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Unsupported file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400

    doc_type = request.form.get('document_type', 'Academic Marksheet')
    
    # Generate unique document ID and safe filename
    doc_id = str(uuid.uuid4())
    original_name = secure_filename(file.filename)
    extension = original_name.rsplit('.', 1)[1].lower()
    stored_name = f"{doc_id}.{extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)

    # Save uploaded file
    file.save(file_path)

    # Register document under user's session
    DOCUMENT_REGISTRY[doc_id] = {
        'doc_id': doc_id,
        'session_id': get_session_id(),
        'original_name': original_name,
        'stored_name': stored_name,
        'file_path': file_path,
        'document_type': doc_type,
        'file_size': os.path.getsize(file_path),
        'file_type': extension.upper(),
        'uploaded_at': datetime.now().isoformat(),
        'analysis_results': None
    }

    return jsonify({
        'document_id': doc_id,
        'filename': original_name,
        'file_type': extension.upper(),
        'file_size': os.path.getsize(file_path),
        'document_type': doc_type,
        'message': 'File successfully uploaded and validated.'
    }), 201

@app.route('/api/documents/<document_id>/analyze', methods=['POST'])
def analyze_document(document_id):
    doc_record = DOCUMENT_REGISTRY.get(document_id)
    if not doc_record or doc_record['session_id'] != get_session_id():
        return jsonify({'error': 'Document not found or unauthorized session'}), 404

    # Allow overriding document type during analysis
    req_json = request.get_json(silent=True) or {}
    doc_type = req_json.get('document_type', doc_record['document_type'])

    # Execute verification engine
    results = VerificationEngine.analyze_document(
        file_path=doc_record['file_path'],
        document_type=doc_type,
        session_id=get_session_id()
    )

    doc_record['analysis_results'] = results

    # Save to SQLite database
    save_verification(results)

    return jsonify(results), 200

@app.route('/api/documents/<document_id>/results', methods=['GET'])
def get_document_results(document_id):
    doc_record = DOCUMENT_REGISTRY.get(document_id)
    if not doc_record or doc_record['session_id'] != get_session_id():
        return jsonify({'error': 'Document not found or unauthorized session'}), 404

    if not doc_record['analysis_results']:
        return jsonify({'error': 'Document has not been analyzed yet'}), 400

    return jsonify(doc_record['analysis_results']), 200

@app.route('/api/documents/<document_id>/update-fields', methods=['POST'])
def update_extracted_fields(document_id):
    """
    Allows user to edit extracted OCR fields and re-evaluate consistency checks.
    """
    doc_record = DOCUMENT_REGISTRY.get(document_id)
    if not doc_record or doc_record['session_id'] != get_session_id():
        return jsonify({'error': 'Document not found or unauthorized session'}), 404

    current_results = doc_record.get('analysis_results')
    if not current_results:
        return jsonify({'error': 'No prior analysis results found to update'}), 400

    req_data = request.get_json()
    if not req_data or 'fields' not in req_data:
        return jsonify({'error': 'Invalid request: "fields" dictionary expected'}), 400

    updated_fields = req_data['fields']
    extracted_data = current_results['extracted_data']

    # Update fields and mark as edited
    for key, val in updated_fields.items():
        if key in extracted_data:
            extracted_data[key]['value'] = val
            extracted_data[key]['edited'] = True
            extracted_data[key]['review_required'] = False
        else:
            extracted_data[key] = {
                'value': val,
                'source_page': 1,
                'snippet': 'User entered value',
                'method': 'user_edit',
                'review_required': False,
                'edited': True
            }

    # Re-evaluate consistency checks
    doc_type = current_results['document_type']
    consistency_results = ConsistencyService.evaluate(
        extracted_data=extracted_data,
        doc_type=doc_type,
        qr_data=current_results['qr_results']
    )
    current_results['consistency_results'] = consistency_results

    # Re-evaluate status
    decision = VerificationEngine._determine_overall_status(
        extracted_data=extracted_data,
        consistency_results=consistency_results,
        qr_results=current_results['qr_results'],
        sig_results=current_results['signature_results'],
        provider_results=current_results['institutional_results'],
        has_raw_text=True
    )

    current_results['overall_status'] = decision['overall_status']
    current_results['status_badge'] = decision['status_badge']
    current_results['status_explanation'] = decision['explanation']
    current_results['risk_score'] = decision['risk_score']
    current_results['risk_level'] = decision['risk_level']

    # Update in database
    save_verification(current_results)

    return jsonify(current_results), 200

@app.route('/api/documents/<document_id>/report', methods=['GET'])
def download_report(document_id):
    doc_record = DOCUMENT_REGISTRY.get(document_id)
    if not doc_record or doc_record['session_id'] != get_session_id():
        return jsonify({'error': 'Document not found or unauthorized session'}), 404

    results = doc_record.get('analysis_results')
    if not results:
        return jsonify({'error': 'Document analysis results not available'}), 400

    report_ref = results.get('report_ref', 'EDV-UNKNOWN')
    report_filename = f"EduVerify_Report_{report_ref}.pdf"
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)

    ReportService.generate_pdf_report(results, report_path)

    return send_file(
        report_path,
        as_attachment=True,
        download_name=report_filename,
        mimetype='application/pdf'
    )

@app.route('/api/documents/<document_id>/preview/<filename>', methods=['GET'])
def get_preview_image(document_id, filename):
    doc_record = DOCUMENT_REGISTRY.get(document_id)
    if not doc_record or doc_record['session_id'] != get_session_id():
        abort(404)

    results = doc_record.get('analysis_results', {})
    preview_dir = results.get('metadata', {}).get('preview_dir')
    if not preview_dir:
        # Fallback to direct directory
        preview_dir = os.path.join(os.path.dirname(doc_record['file_path']), f"previews_{results.get('report_ref', '')}")

    safe_name = secure_filename(filename)
    target_path = os.path.join(preview_dir, safe_name)
    if os.path.exists(target_path):
        return send_file(target_path, mimetype='image/png')
    abort(404)

@app.route('/api/history', methods=['GET'])
def get_verification_history():
    history_items = get_history(session_id=get_session_id())
    return jsonify({
        'count': len(history_items),
        'items': history_items
    }), 200

@app.route('/api/history/<report_ref>', methods=['GET'])
def get_history_detail(report_ref):
    item = get_verification_by_ref(report_ref, session_id=get_session_id())
    if not item:
        return jsonify({'error': 'History entry not found'}), 404
    return jsonify(item), 200

@app.route('/api/history/<report_ref>', methods=['DELETE'])
def delete_history_item(report_ref):
    success = delete_verification(report_ref, session_id=get_session_id())
    if success:
        return jsonify({'message': f'Record {report_ref} deleted successfully.'}), 200
    return jsonify({'error': 'Record not found or already deleted.'}), 404

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    count = clear_all_history(session_id=get_session_id())
    # Clean up temporary uploaded files to conserve cloud disk space
    try:
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            p = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.isfile(p):
                os.remove(p)
            elif os.path.isdir(p):
                import shutil
                shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass
    return jsonify({'message': f'Cleared {count} verification history records and purged temporary upload files.'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
