# Production Deployment Guide
# Physician AI Assistant

## Prerequisites

### Required Software
- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** and **Node.js 18+**
- **PostgreSQL 15+** (for production database)
- **OpenAI API Key** (for AI features)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

---

## Deployment Option 1: Docker Compose (Recommended)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-

# Create environment file
cp backend/.env.production backend/.env
```

### Step 2: Update Environment Variables

Edit `backend/.env` and set:

```bash
# CRITICAL: Change these for production!
SECRET_KEY=your-secure-random-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key

# Database (Docker Compose will use PostgreSQL)
DATABASE_URL=postgresql://physician_user:secure_password@db:5432/physician_ai

# CORS - Add your production domain
CORS_ORIGINS=https://yourapp.com,https://www.yourapp.com
```

### Step 3: Generate Secret Key

```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OR OpenSSL method
openssl rand -base64 32
```

### Step 4: Build and Start Services

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check detailed health
curl http://localhost:8000/health/detailed

# Access API documentation
# Open: http://localhost:8000/docs

# Access frontend
# Open: http://localhost:3000
```

### Managing the Application

```bash
# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes data!)
docker-compose down -v

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

---

## Deployment Option 2: Manual Installation

### Backend Setup

#### Step 1: Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure Environment

```bash
# Create .env file
cp .env.production .env

# Edit .env and set all required values
notepad .env  # Windows
nano .env     # Linux/Mac
```

#### Step 3: Setup Database

**For PostgreSQL:**
```bash
# Create database
createdb physician_ai

# Or use psql
psql -U postgres
CREATE DATABASE physician_ai;
CREATE USER physician_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE physician_ai TO physician_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://physician_user:secure_password@localhost:5432/physician_ai
```

**For SQLite (development only):**
```bash
DATABASE_URL=sqlite:///./physician_ai.db
```

#### Step 4: Run Database Migrations

```bash
# Initialize database
python -c "from app.database import init_db; init_db()"

# Or use Alembic (if configured)
alembic upgrade head
```

#### Step 5: Start Backend Server

```bash
# Development
python run.py

# Production (with Gunicorn)
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Setup

#### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

#### Step 2: Configure Environment

```bash
# Create production env file
cp .env.production .env.production.local

# Edit and set your API URL
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### Step 3: Build and Serve

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Serve with a production server
npm install -g serve
serve -s dist -p 3000
```

---

## Production Server Setup (Linux)

### Using Systemd Service Files

#### Backend Service

Create `/etc/systemd/system/physician-ai-backend.service`:

```ini
[Unit]
Description=Physician AI Backend Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/physician-ai/backend
Environment="PATH=/var/www/physician-ai/backend/venv/bin"
ExecStart=/var/www/physician-ai/backend/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/physician-ai/access.log \
    --error-logfile /var/log/physician-ai/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Service (with Nginx)

Install Nginx:
```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/physician-ai`:

```nginx
server {
    listen 80;
    server_name yourapp.com www.yourapp.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourapp.com www.yourapp.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourapp.com/privkey.pem;
    
    # Frontend
    root /var/www/physician-ai/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Enable and start services:
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/physician-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Enable and start backend service
sudo systemctl daemon-reload
sudo systemctl enable physician-ai-backend
sudo systemctl start physician-ai-backend

# Check status
sudo systemctl status physician-ai-backend
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourapp.com -d www.yourapp.com

# Auto-renewal (already configured by Certbot)
sudo certbot renew --dry-run
```

---

## Environment-Specific Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./physician_ai.db
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
RATE_LIMIT_ENABLED=False
```

### Staging
```bash
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/physician_ai_staging
CORS_ORIGINS=https://staging.yourapp.com
RATE_LIMIT_ENABLED=True
```

### Production
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/physician_ai
CORS_ORIGINS=https://yourapp.com,https://www.yourapp.com
RATE_LIMIT_ENABLED=True
ENABLE_METRICS=True
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# Basic health
curl https://yourapp.com/health

# Detailed health
curl https://yourapp.com/health/detailed

# Dependencies check
curl https://yourapp.com/health/dependencies

# Metrics
curl https://yourapp.com/metrics
```

### Log Locations

**Docker:**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

**Manual Installation:**
```bash
# Backend logs
tail -f backend/logs/physician_ai.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Systemd service logs
sudo journalctl -u physician-ai-backend -f
```

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U physician_user physician_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL restore
psql -U physician_user physician_ai < backup_20250101_120000.sql

# Docker PostgreSQL backup
docker-compose exec db pg_dump -U physician_user physician_ai > backup.sql

# Docker PostgreSQL restore
docker-compose exec -T db psql -U physician_user physician_ai < backup.sql
```

---

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Check configuration
python -c "from app.core.config import settings; settings.validate()"

# Test database connection
python -c "from app.database import get_db; next(get_db())"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U physician_user -d physician_ai -h localhost

# Check DATABASE_URL format
echo $DATABASE_URL
```

### OpenAI API Issues

```bash
# Test API key
python -c "import openai; openai.api_key='sk-...'; print(openai.Model.list())"

# Check rate limits and usage
# Visit: https://platform.openai.com/usage
```

### High Memory Usage

```bash
# Check memory
free -h

# Check container memory
docker stats

# Adjust worker count (in production)
gunicorn app.main:app --workers 2  # Reduce workers
```

---

## Security Checklist

- [ ] Changed SECRET_KEY from default
- [ ] Set DEBUG=False in production
- [ ] Configured HTTPS/SSL
- [ ] Updated CORS_ORIGINS to production domains
- [ ] Enabled rate limiting
- [ ] Set up database backups
- [ ] Configured firewall rules
- [ ] Updated all default passwords
- [ ] Enabled monitoring/alerting
- [ ] Reviewed and limited file upload sizes
- [ ] Set up log rotation
- [ ] Configured security headers
- [ ] Enabled HSTS
- [ ] Regular security updates

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/drkvvk2015/Natpudan-/issues
- Documentation: See README.md
- API Docs: https://yourapp.com/docs

---

**Version**: 1.0.0  
**Last Updated**: November 2025
