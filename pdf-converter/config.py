import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = False
    
    # Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'pdf_converter_db')
    MYSQL_PORT = os.getenv('MYSQL_PORT', 3306)
    
    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    CONVERTED_FOLDER = os.getenv('CONVERTED_FOLDER', 'converted')
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Allowed File Extensions
    ALLOWED_INPUT_EXTENSIONS = {'pdf', 'docx', 'pptx', 'doc', 'ppt', 'txt', 'odt'}
    ALLOWED_OUTPUT_FORMATS = {'pdf', 'docx', 'pptx', 'txt', 'images'}
    
    # Create upload directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
