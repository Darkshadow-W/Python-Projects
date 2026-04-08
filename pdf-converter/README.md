# PDF File Converter 

A modern file conversion platform that converts between PDF, Word, PowerPoint, and text files with a minimal UI and MySQL database backend.

## Features

✨ **File Conversion**
- PDF ↔ DOCX (Word)
- PDF ↔ PPTX (PowerPoint)
- TXT ↔ PDF
- PDF → Images (PNG)
- And more...

📊 **Conversion Tracking**
- Conversion history
- File statistics
- Error logging
- Database persistence

🎨 **Minimal UI**
- Clean, responsive design
- Drag-and-drop upload
- Real-time conversion status
- Live statistics

🔒 **User Management**
- Guest conversions
- Conversion history tracking
- File metadata storage

## Project Structure

```
pdf-converter/
├── app.py                 # Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── routes.py             # API endpoints
├── utils.py              # File conversion utilities
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   ├── index.html        # Main converter page
│   ├── 404.html          # Error page
│   └── 500.html          # Server error page
├── static/
│   ├── style.css         # Minimal styling
│   └── script.js         # Frontend logic
├── uploads/              # Temporary upload folder
└── converted/            # Converted files folder
```

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- LibreOffice (for file conversions)
- pip (Python package manager)

### 1. Set Up Python Environment

```bash
cd pdf-converter
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL Database

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE pdf_converter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional but recommended)
CREATE USER 'converter_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON pdf_converter_db.* TO 'converter_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your settings
# Update MYSQL credentials
```

### 5. Initialize Database

```bash
python app.py
# Database tables will be created automatically
```

## Running the Application

### Development Server

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
- `GET /api/health` - Check if API is running

### Supported Formats
- `GET /api/supported-formats` - Get all supported conversion formats

### File Conversion
- `POST /api/upload-and-convert` - Upload and convert file
  - Parameters:
    - `file` (multipart): File to convert
    - `target_format` (string): Target file format

### Download
- `GET /api/download/<conversion_id>` - Download converted file

### Statistics
- `GET /api/conversion-stats` - Get system statistics
  - Returns: total conversions, completed, failed, pending, total size

### History
- `GET /api/conversion-history/<user_id>` - Get user conversion history

### Delete
- `DELETE /api/delete/<conversion_id>` - Delete a conversion record

## Supported File Formats

### Input Formats
- PDF
- DOCX (Word)
- PPTX (PowerPoint)
- DOC
- PPT
- TXT
- ODT

### Output Formats
- PDF
- DOCX
- PPTX
- TXT
- Images (PNG)

## Database Schema

### Users Table
- `id` - Primary key
- `email` - User email
- `username` - Username
- `created_at` - Creation timestamp

### Conversions Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `original_filename` - Original file name
- `converted_filename` - Converted file name
- `original_format` - Input format
- `target_format` - Output format
- `file_size` - File size in bytes
- `status` - pending/completed/failed
- `error_message` - Error details if failed
- `original_file_path` - Path to original file
- `converted_file_path` - Path to converted file
- `created_at` - Creation timestamp
- `completed_at` - Completion timestamp

### FileMetadata Table
- `id` - Primary key
- `conversion_id` - Foreign key to conversions
- `pages` - Number of pages
- `width` - Document width
- `height` - Document height
- `duration` - Media duration
- `created_at` - Creation timestamp

## Configuration

Edit `config.py` to customize:

```python
# Database connection
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'password'
MYSQL_DATABASE = 'pdf_converter_db'

# Upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', ...}

# Output folders
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
```

## Frontend Features

- **Drag & Drop**: Easily upload files by dragging them
- **Format Selection**: Dynamic format selection based on input file
- **Real-time Status**: See conversion progress
- **Download Management**: Download converted files immediately
- **Live Statistics**: View system-wide conversion stats
- **Error Handling**: Clear error messages and recovery options

## Troubleshooting

### LibreOffice Not Found
- Install LibreOffice: `sudo apt-get install libreoffice` (Linux)
- Or download from libreoffice.org

### Database Connection Error
- Check MySQL is running
- Verify credentials in `.env`
- Ensure database exists

### File Upload Fails
- Check `uploads/` folder permissions
- Verify file is under 50MB
- Ensure file extension is supported

### PDF to Image Conversion Fails
- Install `pdf2image`: `pip install pdf2image`
- Install poppler: `sudo apt-get install poppler-utils` (Linux)

## Security Notes

⚠️ **For Production:**
1. Change `SECRET_KEY` in `.env`
2. Use strong MySQL password
3. Set `DEBUG = False`
4. Use HTTPS/SSL
5. Implement rate limiting
6. Add user authentication
7. Validate file uploads
8. Clean up old files regularly

## Performance Tips

- Set up a task queue (Celery) for background conversions
- Use CDN for static files
- Implement file compression
- Add caching for conversion results
- Use connection pooling
- Monitor database performance

## License

MIT License - Feel free to use for personal or commercial projects

## Support

For issues or questions, please check:
1. Requirements are installed: `pip list`
2. MySQL database is running
3. `.env` file is properly configured
4. Folders have write permissions
5. LibreOffice is installed

Happy converting! 🎉
