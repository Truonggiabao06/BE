"""
File Upload API controller for the Jewelry Auction System
"""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from api.middleware.auth_middleware import jwt_required, get_current_user
from datetime import datetime

# Create blueprint
upload_bp = Blueprint('upload', __name__, url_prefix='/api/v1/upload')

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt'}
}

# Max file sizes (in bytes)
MAX_FILE_SIZES = {
    'images': 5 * 1024 * 1024,  # 5MB
    'documents': 10 * 1024 * 1024  # 10MB
}

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def get_upload_path(file_type):
    """Get upload directory path"""
    base_path = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    upload_path = os.path.join(base_path, file_type)
    
    # Create directory if it doesn't exist
    os.makedirs(upload_path, exist_ok=True)
    
    return upload_path

@upload_bp.route('/images', methods=['POST'])
@jwt_required
def upload_image():
    """
    Upload jewelry images
    ---
    tags:
      - File Upload
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Image file to upload
      - in: formData
        name: description
        type: string
        description: Optional image description
    responses:
      200:
        description: Image uploaded successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                filename:
                  type: string
                url:
                  type: string
                size:
                  type: integer
      400:
        description: Invalid file or request
      401:
        description: Authentication required
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'code': 'NO_FILE'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'code': 'NO_FILE_SELECTED'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename, 'images'):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp',
                'code': 'INVALID_FILE_TYPE'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZES['images']:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZES["images"] // (1024*1024)}MB',
                'code': 'FILE_TOO_LARGE'
            }), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save file
        upload_path = get_upload_path('images')
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Get additional metadata
        description = request.form.get('description', '')
        user_id = get_current_user()
        
        # Generate URL (in production, this would be a CDN URL)
        file_url = f"/uploads/images/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'data': {
                'filename': unique_filename,
                'original_filename': secure_filename(file.filename),
                'url': file_url,
                'size': file_size,
                'description': description,
                'uploaded_by': user_id,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Image upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to upload image',
            'code': 'UPLOAD_ERROR'
        }), 500

@upload_bp.route('/documents', methods=['POST'])
@jwt_required
def upload_document():
    """
    Upload documents (certificates, appraisals, etc.)
    ---
    tags:
      - File Upload
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Document file to upload
      - in: formData
        name: document_type
        type: string
        description: Type of document (certificate, appraisal, etc.)
    responses:
      200:
        description: Document uploaded successfully
      400:
        description: Invalid file or request
      401:
        description: Authentication required
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'code': 'NO_FILE'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'code': 'NO_FILE_SELECTED'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename, 'documents'):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: pdf, doc, docx, txt',
                'code': 'INVALID_FILE_TYPE'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZES['documents']:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {MAX_FILE_SIZES["documents"] // (1024*1024)}MB',
                'code': 'FILE_TOO_LARGE'
            }), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save file
        upload_path = get_upload_path('documents')
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Get additional metadata
        document_type = request.form.get('document_type', 'general')
        user_id = get_current_user()
        
        # Generate URL
        file_url = f"/uploads/documents/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'data': {
                'filename': unique_filename,
                'original_filename': secure_filename(file.filename),
                'url': file_url,
                'size': file_size,
                'document_type': document_type,
                'uploaded_by': user_id,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Document upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to upload document',
            'code': 'UPLOAD_ERROR'
        }), 500

@upload_bp.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    """
    Serve uploaded files
    ---
    tags:
      - File Upload
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: Filename to serve
    responses:
      200:
        description: File served successfully
      404:
        description: File not found
    """
    try:
        # This is a basic implementation
        # In production, use nginx or a CDN to serve static files
        return jsonify({
            'message': 'File serving not implemented in development mode',
            'filename': filename,
            'note': 'In production, files would be served by nginx or CDN'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"File serve error: {str(e)}")
        return jsonify({
            'error': 'File not found'
        }), 404
