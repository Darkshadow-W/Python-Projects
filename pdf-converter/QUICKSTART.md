# Quick Start Guide - PDF File Converter

Get your PDF converter up and running in 5 minutes!

## Prerequisites Check
- [ ] Python 3.8+ installed
- [ ] MySQL 5.7+ running
- [ ] pip package manager available

## Step 1: Navigate to Project
```bash
cd pdf-converter
```

## Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Configure Database

### Option A: Use Default Settings (Easiest)
```bash
# Just run the init script (requires MySQL running with default root user)
python init_db.py
```

### Option B: Custom Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your MySQL credentials:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=pdf_converter_db
   ```

3. Run initialization:
   ```bash
   python init_db.py
   ```

## Step 5: Start the Server
```bash
python app.py
```

You should see:
```
* Serving Flask app 'app'
* Running on http://127.0.0.1:5000
```

## Step 6: Open in Browser
Visit: **http://localhost:5000**

## What You'll See

A clean interface with:
- ✨ Drag-and-drop file upload
- 📊 Real-time conversion status
- 📈 System statistics
- 🎨 Minimal, responsive design

## Supported Conversions

### Upload any of these:
- PDF
- DOCX (Word)
- PPTX (PowerPoint)  
- PPTX
- TXT
- ODT

### Convert to any of these:
- PDF
- DOCX
- PPTX
- TXT
- Images (PNG)

## Troubleshooting

### MySQL Connection Failed
```
Error: Cannot connect to MySQL server
```
**Solution**: Start MySQL service
- Windows: Use MySQL Installer
- Mac: `brew services start mysql`
- Linux: `sudo systemctl start mysql`

### ModuleNotFoundError
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Ensure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Port 5000 Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### File Upload Not Working
Check folder permissions:
```bash
mkdir -p uploads converted
chmod 755 uploads converted
```

## Next Steps

1. **Customize Styling**: Edit `static/style.css`
2. **Add Authentication**: Update `models.py` and `routes.py`
3. **Deploy**: Use Gunicorn + Nginx
4. **Scale**: Add task queue (Celery) for large files

## Need Help?

Check the full [README.md](README.md) for:
- Detailed API documentation
- Database schema explanation
- Production deployment guide
- Security best practices
- Performance optimization tips

## Development Tips

### Auto-reload on Changes
Flask auto-reloads when `DEBUG=True` in config

### View Database
```bash
mysql -u root -p pdf_converter_db
SHOW TABLES;
SELECT * FROM conversions;
```

### Monitor Conversions
The stats dashboard shows:
- Total conversions
- Successful conversions
- Failed conversions
- Total data processed

## Production Checklist

- [ ] Update `SECRET_KEY` in `.env`
- [ ] Set `DEBUG = False`
- [ ] Use strong MySQL password
- [ ] Set up firewall rules
- [ ] Use HTTPS/SSL certificate
- [ ] Set up log rotation
- [ ] Schedule old file cleanup
- [ ] Test backup/restore process

---

**Happy Converting!** 🚀

For detailed documentation, see [README.md](README.md)
