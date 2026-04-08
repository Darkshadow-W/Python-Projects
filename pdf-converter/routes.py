from flask import Blueprint, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import mimetypes

from models import db, User, Conversion, FileMetadata
from utils import FileConverter
from config import Config

api = Blueprint('api', __name__, url_prefix='/api')

# Allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'doc', 'ppt', 'txt', 'odt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_user(email=None, username=None):
    """Get or create user"""
    if not email:
        email = f"guest_{datetime.now().timestamp()}@converter.local"
    if not username:
        username = f"guest_{datetime.now().timestamp()}"
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(email=email, username=username)
        db.session.add(user)
        db.session.commit()
    
    return user

@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

@api.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get all supported conversion formats"""
    return jsonify(FileConverter.SUPPORTED_FORMATS), 200

@api.route('/upload-and-convert', methods=['POST'])
def upload_and_convert():
    """Upload file and convert to target format"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        target_format = request.form.get('target_format')
        
        if not target_format:
            return jsonify({'error': 'Target format not specified'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(input_path)
        
        # Get file info
        input_format = FileConverter.get_file_extension(filename)
        file_size = os.path.getsize(input_path)
        
        # Check if conversion is supported
        if not FileConverter.is_valid_conversion(input_format, target_format):
            os.remove(input_path)
            return jsonify({
                'error': f'Conversion from {input_format} to {target_format} is not supported'
            }), 400
        
        # Create user
        user = get_or_create_user()
        
        # Create conversion record
        conversion = Conversion(
            user_id=user.id,
            original_filename=filename,
            converted_filename=f"{os.path.splitext(filename)[0]}.{target_format}",
            original_format=input_format,
            target_format=target_format,
            file_size=file_size,
            original_file_path=input_path,
            status='pending'
        )
        db.session.add(conversion)
        db.session.commit()
        
        try:
            # Perform conversion
            output_path = os.path.join(
                Config.CONVERTED_FOLDER,
                conversion.converted_filename
            )
            
            # Use FileConverter
            converted_path = FileConverter.convert(input_path, target_format)
            
            if converted_path and os.path.exists(converted_path):
                # Move to converted folder
                os.makedirs(Config.CONVERTED_FOLDER, exist_ok=True)
                os.rename(converted_path, output_path)
                
                conversion.converted_file_path = output_path
                conversion.status = 'completed'
                conversion.completed_at = datetime.utcnow()
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'conversion_id': conversion.id,
                    'filename': conversion.converted_filename,
                    'download_url': f'/api/download/{conversion.id}',
                    'message': f'Successfully converted {input_format.upper()} to {target_format.upper()}'
                }), 200
            else:
                conversion.status = 'failed'
                conversion.error_message = 'Conversion process failed'
                db.session.commit()
                
                return jsonify({
                    'error': 'Conversion failed. Please check file format and try again.'
                }), 400
        
        except Exception as e:
            conversion.status = 'failed'
            conversion.error_message = str(e)
            db.session.commit()
            
            return jsonify({'error': f'Conversion error: {str(e)}'}), 400
        
        finally:
            # Clean up original file
            if os.path.exists(input_path):
                os.remove(input_path)
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@api.route('/download/<int:conversion_id>', methods=['GET'])
def download_file(conversion_id):
    """Download converted file"""
    try:
        conversion = Conversion.query.get(conversion_id)
        
        if not conversion:
            return jsonify({'error': 'Conversion record not found'}), 404
        
        if conversion.status != 'completed' or not conversion.converted_file_path:
            return jsonify({'error': 'File not ready for download'}), 400
        
        if not os.path.exists(conversion.converted_file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        return send_file(
            conversion.converted_file_path,
            as_attachment=True,
            download_name=conversion.converted_filename,
            mimetype=mimetypes.guess_type(conversion.converted_file_path)[0] or 'application/octet-stream'
        )
    
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@api.route('/conversion-history/<int:user_id>', methods=['GET'])
def get_conversion_history(user_id):
    """Get conversion history for user"""
    try:
        conversions = Conversion.query.filter_by(user_id=user_id).order_by(
            Conversion.created_at.desc()
        ).all()
        
        history = [{
            'id': c.id,
            'original_filename': c.original_filename,
            'converted_filename': c.converted_filename,
            'original_format': c.original_format,
            'target_format': c.target_format,
            'status': c.status,
            'created_at': c.created_at.isoformat(),
            'completed_at': c.completed_at.isoformat() if c.completed_at else None
        } for c in conversions]
        
        return jsonify({'history': history}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/conversion-stats', methods=['GET'])
def get_conversion_stats():
    """Get conversion statistics"""
    try:
        total_conversions = Conversion.query.count()
        completed = Conversion.query.filter_by(status='completed').count()
        failed = Conversion.query.filter_by(status='failed').count()
        pending = Conversion.query.filter_by(status='pending').count()
        
        total_size = db.session.query(
            db.func.sum(Conversion.file_size)
        ).scalar() or 0
        
        return jsonify({
            'total_conversions': total_conversions,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/delete/<int:conversion_id>', methods=['DELETE'])
def delete_conversion(conversion_id):
    """Delete a conversion record and its files"""
    try:
        conversion = Conversion.query.get(conversion_id)
        
        if not conversion:
            return jsonify({'error': 'Conversion not found'}), 404
        
        # Delete files
        if conversion.converted_file_path and os.path.exists(conversion.converted_file_path):
            os.remove(conversion.converted_file_path)
        
        if conversion.original_file_path and os.path.exists(conversion.original_file_path):
            os.remove(conversion.original_file_path)
        
        # Delete metadata
        FileMetadata.query.filter_by(conversion_id=conversion_id).delete()
        
        # Delete conversion record
        db.session.delete(conversion)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Conversion deleted'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
