# Production Deployment Guide

Complete guide for deploying the PDF Converter to production.

## Deployment Options

### Option 1: Docker Deployment (Recommended)

```bash
# Clone/download the project
cd pdf-converter

# Create .env file with production settings
cp .env.example .env
# Edit .env with production credentials

# Start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f flask_app
```

### Option 2: Traditional Server Setup

#### Requirements
- Ubuntu 20.04+ or similar
- Python 3.8+
- MySQL 5.7+
- Nginx or Apache
- Supervisor (for process management)

#### Setup Steps

1. **Install System Dependencies**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.10 python3-pip python3-venv \
    mysql-server mysql-client \
    libreoffice libreoffice-writer \
    poppler-utils \
    nginx supervisor
```

2. **Create Application User**
```bash
sudo useradd -m -s /bin/bash converter
sudo -u converter mkdir -p /home/converter/pdf-converter
```

3. **Setup Application**
```bash
cd /home/converter/pdf-converter
git clone <repo-url> .

# Setup virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Setup environment
cp .env.example .env
# Edit .env with production settings
```

4. **Initialize Database**
```bash
python init_db.py
```

5. **Create Supervisor Config**

Create `/etc/supervisor/conf.d/pdf-converter.conf`:
```ini
[program:pdf-converter]
directory=/home/converter/pdf-converter
command=/home/converter/pdf-converter/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
user=converter
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/pdf-converter.log
```

Start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start pdf-converter
```

6. **Configure Nginx**

Create `/etc/nginx/sites-available/pdf-converter`:
```nginx
upstream pdf_converter {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    client_max_body_size 50M;

    location / {
        proxy_pass http://pdf_converter;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /home/converter/pdf-converter/static/;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/pdf-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Set Up SSL with Let's Encrypt**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

## Security Configuration

### 1. Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use strong values
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
MYSQL_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
```

### 2. MySQL Security
```sql
-- Disable root remote login
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Create application user with limited privileges
CREATE USER 'converter'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON pdf_converter_db.* TO 'converter'@'localhost';
FLUSH PRIVILEGES;

-- Enable MySQL firewall
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 3306
```

### 3. File Upload Security
```python
# In config.py, add:
UPLOAD_FOLDER_PROTECTED = '/var/uploads'  # Outside web root
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt', 'odt'}
```

### 4. Firewall Rules
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Monitoring and Maintenance

### 1. Log Management
```bash
# View application logs
tail -f /var/log/pdf-converter.log

# Rotate logs
sudo vim /etc/logrotate.d/pdf-converter
```

Create `/etc/logrotate.d/pdf-converter`:
```
/var/log/pdf-converter.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        supervisorctl restart pdf-converter > /dev/null
    endscript
}
```

### 2. Database Backup
```bash
# Daily backup script
sudo crontab -e

# Add:
0 2 * * * mysqldump -u root -p[password] pdf_converter_db > /backups/pdf_converter_$(date +\%Y\%m\%d).sql
```

### 3. Cleanup Old Files
```python
# Add to scheduled task
import os
import time

DAYS = 7
CUTOFF = time.time() - (DAYS * 86400)

for folder in ['uploads', 'converted']:
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.getmtime(path) < CUTOFF:
            os.remove(path)
```

### 4. Monitor Service Health
```bash
# Check status
sudo supervisorctl status pdf-converter

# View resource usage
ps aux | grep gunicorn

# Check database connections
mysql -u root -e "SHOW PROCESSLIST;"
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_conversion_status ON conversions(status);
CREATE INDEX idx_user_conversions ON conversions(user_id, created_at);

-- Optimize tables
OPTIMIZE TABLE users;
OPTIMIZE TABLE conversions;
OPTIMIZE TABLE file_metadata;
```

### 2. Caching
```python
# Add Redis caching
pip install redis flask-caching

# In config.py:
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

### 3. Async Processing
```python
# Use Celery for file conversions
pip install celery

# Process large files asynchronously
from celery import shared_task

@shared_task
def convert_file_async(input_path, output_format):
    return FileConverter.convert(input_path, output_format)
```

### 4. Database Connection Pooling
```python
# In app.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

## Scaling Checklist

- [ ] Load balancer (Nginx upstream blocks)
- [ ] Multiple application instances
- [ ] Database read replicas
- [ ] Redis caching layer
- [ ] CDN for static files
- [ ] Async task queue (Celery)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Centralized logging (ELK stack)
- [ ] Alert system (PagerDuty, Opsgenie)

## Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo tail -f /var/log/pdf-converter.log

# Test database connection
python -c "from models import db; from app import create_app; app = create_app(); print('DB OK')"

# Check Python path
which python
```

### High Memory Usage
```bash
# Check process memory
ps aux | grep gunicorn | grep -v grep

# Reduce worker count in supervisor config
command=/path/to/gunicorn --workers 2
```

### Database Connection Issues
```bash
# Check MySQL is running
sudo systemctl status mysql

# Check connection
mysql -u converter -p -h 127.0.0.1 pdf_converter_db

# Check active connections
mysql > SHOW PROCESSLIST;
```

## Support & Documentation

- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Gunicorn: https://gunicorn.org/

---

**Successfully deployed!** 🎉 Monitor your application and enjoy!
