# Deployment Guide for AttendanceHub

## Quick Start (Development)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create demo users:
```bash
python setup.py
```

4. Run development server:
```bash
python manage.py runserver
```

5. Access the application:
- Main App: http://localhost:8000/
- Login with: `hr_admin` / `admin123` or `employee1` / `emp123`

## Production Deployment

### 1. Environment Setup

Create a `.env` file:
```bash
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Database Configuration (PostgreSQL)

Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

Update `core/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'attendance_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Static Files

Collect static files:
```bash
python manage.py collectstatic --noinput
```

### 4. Using Gunicorn

Install Gunicorn (already in requirements.txt):
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 5. Using Nginx (Recommended)

Create Nginx configuration (`/etc/nginx/sites-available/attendancehub`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/your/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/attendancehub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Systemd Service

Create service file (`/etc/systemd/system/attendancehub.service`):
```ini
[Unit]
Description=AttendanceHub Gunicorn daemon
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          core.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl start attendancehub
sudo systemctl enable attendancehub
sudo systemctl status attendancehub
```

### 7. SSL Certificate (Let's Encrypt)

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

Get certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 8. Security Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use HTTPS (SSL certificate)
- [ ] Set up database backups
- [ ] Configure firewall (UFW)
- [ ] Set up monitoring and logging
- [ ] Regular security updates

## Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=attendance_db
      - POSTGRES_USER=attendance_user
      - POSTGRES_PASSWORD=secure_password

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

Build and run:
```bash
docker-compose up -d
```

## Monitoring

### Setup Logging

Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/attendancehub/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Backup Strategy

### Database Backup

Create backup script (`backup.sh`):
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/attendancehub"
mkdir -p $BACKUP_DIR

# SQLite backup
cp /path/to/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# PostgreSQL backup
# pg_dump -U attendance_user attendance_db > $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database connection errors
- Check database credentials
- Ensure database service is running
- Verify network connectivity

### Permission errors
```bash
sudo chown -R www-data:www-data /path/to/project
sudo chmod -R 755 /path/to/project
```

## Performance Optimization

1. Enable caching:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

2. Use CDN for static files
3. Enable database query optimization
4. Set up load balancing for high traffic

## Support

For issues and questions:
- Check logs: `/var/log/attendancehub/`
- Review Django debug page (if DEBUG=True)
- Contact support team
