# Deployment Guide

This guide covers various deployment options for the AI Medical Diagnosis System, from development to production environments.

## Table of Contents

1. [Environment Preparation](#environment-preparation)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Environment Preparation

### Security Considerations

Before deployment, ensure you've addressed these security concerns:

1. **Change Default Secrets**
   ```env
   SECRET_KEY=generate-a-strong-random-key-here
   DATABASE_URL=use-secure-connection-string
   ```

2. **Enable HTTPS**
   - Obtain SSL certificates
   - Configure reverse proxy with HTTPS
   - Update CORS settings for HTTPS

3. **Environment Variables**
   - Never commit `.env` files
   - Use platform-specific environment variable management
   - Rotate secrets regularly

### Production Configuration

Update backend configuration for production:

```env
# backend/.env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_ORIGINS=["https://yourdomain.com"]
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/var/uploads
```

Update frontend configuration:

```env
# frontend/.env
VITE_API_URL=https://api.yourdomain.com
```

## Backend Deployment

### Option 1: Render (Recommended)

Render provides a simple deployment platform for Python applications.

1. **Prepare Repository**
   - Ensure all code is pushed to GitHub
   - Add `requirements.txt` and `Procfile`

2. **Create Procfile**
   ```procfile
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy to Render**
   - Sign up at [Render](https://render.com)
   - Connect your GitHub repository
   - Create a new Web Service
   - Configure:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Instance Type: Start with Free, then upgrade as needed

4. **Environment Variables**
   Add all necessary environment variables in Render dashboard

### Option 2: AWS EC2

For more control, deploy on AWS EC2.

1. **Launch EC2 Instance**
   ```bash
   # Choose appropriate instance (e.g., t3.medium for development, g4dn.xlarge for production)
   # Use Ubuntu 20.04 LTS
   # Configure security groups (ports 22, 80, 443)
   ```

2. **Server Setup**
   ```bash
   # SSH into instance
   ssh -i your-key.pem ubuntu@your-instance-ip

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv nginx postgresql -y

   # Clone repository
   git clone https://github.com/your-username/ai-medical-diagnosis.git
   cd ai-medical-diagnosis/backend

   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Configure PostgreSQL
   sudo -u postgres createdb medical_diagnosis
   sudo -u postgres createuser diagnosis_user
   sudo -u postgres psql -c "ALTER USER diagnosis_user PASSWORD 'strong_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE medical_diagnosis TO diagnosis_user;"
   ```

4. **Systemd Service**
   Create `/etc/systemd/system/medical-diagnosis.service`:
   ```ini
   [Unit]
   Description=Medical Diagnosis API
   After=network.target

   [Service]
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/home/ubuntu/ai-medical-diagnosis/backend
   Environment=PATH=/home/ubuntu/ai-medical-diagnosis/backend/venv/bin
   ExecStart=/home/ubuntu/ai-medical-diagnosis/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Enable and start service
   sudo systemctl enable medical-diagnosis
   sudo systemctl start medical-diagnosis
   sudo systemctl status medical-diagnosis
   ```

5. **Nginx Reverse Proxy**
   Create `/etc/nginx/sites-available/medical-diagnosis`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/medical-diagnosis /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from heroku.com
   # Or use npm
   npm install -g heroku
   ```

2. **Prepare App**
   ```bash
   # Add runtime.txt
   echo "python-3.9.13" > runtime.txt

   # Update requirements.txt
   pip freeze > requirements.txt

   # Add Procfile
   echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set DEBUG=False
   git push heroku main
   ```

## Frontend Deployment

### Option 1: Vercel (Recommended)

Vercel provides excellent React deployment with automatic optimizations.

1. **Prepare Repository**
   - Ensure frontend code is in a subdirectory or separate repo
   - Add `vercel.json` configuration

2. **Vercel Configuration**
   Create `frontend/vercel.json`:
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "installCommand": "npm install",
     "framework": "vite",
     "env": {
       "VITE_API_URL": "@api-url"
     }
   }
   ```

3. **Deploy to Vercel**
   - Sign up at [Vercel](https://vercel.com)
   - Connect your GitHub repository
   - Configure root directory: `frontend`
   - Add environment variables
   - Deploy

### Option 2: Netlify

1. **Build Configuration**
   Create `frontend/netlify.toml`:
   ```toml
   [build]
     publish = "dist"
     command = "npm run build"

   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200

   [build.environment]
     VITE_API_URL = "https://api.yourdomain.com"
   ```

2. **Deploy**
   - Sign up at [Netlify](https://netlify.com)
   - Connect repository
   - Configure build settings
   - Deploy

### Option 3: AWS S3 + CloudFront

1. **Build and Upload**
   ```bash
   cd frontend
   npm run build

   # Install AWS CLI
   aws configure

   # Upload to S3
   aws s3 sync dist/ s3://your-bucket-name --delete
   ```

2. **CloudFront Distribution**
   - Create CloudFront distribution
   - Set origin to S3 bucket
   - Configure error pages for SPA routing
   - Set up SSL certificate

## Docker Deployment

### 1. Create Dockerfiles

**Backend Dockerfile**:
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/medical_diagnosis
    volumes:
      - ./models:/app/models
      - ./uploads:/app/uploads
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=medical_diagnosis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Cloud Deployment

### Google Cloud Platform

1. **Cloud Run (Backend)**
   ```bash
   # Build and push to Google Container Registry
   gcloud builds submit --tag gcr.io/PROJECT-ID/medical-diagnosis-api

   # Deploy to Cloud Run
   gcloud run deploy medical-diagnosis-api --image gcr.io/PROJECT-ID/medical-diagnosis-api --platform managed
   ```

2. **Firebase Hosting (Frontend)**
   ```bash
   # Install Firebase CLI
   npm install -g firebase-tools

   # Initialize Firebase
   firebase init hosting

   # Deploy
   firebase deploy --only hosting
   ```

### Microsoft Azure

1. **Azure App Service (Backend)**
   - Create App Service with Python runtime
   - Configure deployment from GitHub
   - Set environment variables in App Service settings

2. **Azure Static Web Apps (Frontend)**
   - Create Static Web App
   - Connect GitHub repository
   - Configure build settings

## Monitoring and Maintenance

### Logging

1. **Backend Logging**
   - Configure structured logging
   - Use log aggregation services (ELK, Datadog)
   - Set up log rotation

2. **Frontend Monitoring**
   - Implement error tracking (Sentry)
   - Use performance monitoring
   - Set up user analytics

### Health Checks

1. **Backend Health Endpoint**
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "timestamp": datetime.now()}
   ```

2. **Monitoring Services**
   - Set up uptime monitoring
   - Configure alerting for failures
   - Monitor resource usage

### Backup and Recovery

1. **Database Backups**
   ```bash
   # Automated backups
   pg_dump medical_diagnosis > backup_$(date +%Y%m%d_%H%M%S).sql

   # Restore
   psql medical_diagnosis < backup_file.sql
   ```

2. **Model Backups**
   - Store model files in cloud storage
   - Version control model artifacts
   - Document model performance metrics

### Scaling

1. **Horizontal Scaling**
   - Load balance multiple backend instances
   - Use container orchestration (Kubernetes)
   - Implement caching (Redis)

2. **Vertical Scaling**
   - Monitor resource usage
   - Upgrade instance sizes as needed
   - Optimize database queries

### Security Updates

1. **Regular Updates**
   - Update dependencies regularly
   - Monitor security advisories
   - Apply security patches promptly

2. **Security Scanning**
   - Use dependency scanning tools
   - Perform regular security audits
   - Implement WAF for production

---

This deployment guide covers the most common deployment scenarios. Choose the option that best fits your requirements and infrastructure preferences.
