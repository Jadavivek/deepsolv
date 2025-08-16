# Deployment Guide

This guide covers different deployment options for the Shopify Insights Fetcher application.

## Local Development Deployment

### Prerequisites
- Python 3.13+
- MySQL 8.0+
- Git

### Setup Steps

1. **Clone the repository:**
\`\`\`bash
git clone <repository-url>
cd shopify-insights-fetcher
\`\`\`

2. **Create virtual environment:**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Setup environment variables:**
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

5. **Initialize database:**
\`\`\`bash
python scripts/init_database.py
\`\`\`

6. **Seed sample data (optional):**
\`\`\`bash
python scripts/seed_database.py
\`\`\`

7. **Run the application:**
\`\`\`bash
python main.py
# Or alternatively:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
\`\`\`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone and navigate to project:**
\`\`\`bash
git clone <repository-url>
cd shopify-insights-fetcher
\`\`\`

2. **Start services:**
\`\`\`bash
docker-compose up --build
\`\`\`

This will start both the application and MySQL database.

### Using Docker Only

1. **Build the image:**
\`\`\`bash
docker build -t shopify-insights-fetcher .
\`\`\`

2. **Run with external MySQL:**
\`\`\`bash
docker run -p 8000:8000 \
  -e MYSQL_HOST=your-mysql-host \
  -e MYSQL_USER=your-mysql-user \
  -e MYSQL_PASSWORD=your-mysql-password \
  -e MYSQL_DATABASE=shopify_insights \
  shopify-insights-fetcher
\`\`\`

## Production Deployment

### Using Gunicorn

1. **Install Gunicorn:**
\`\`\`bash
pip install gunicorn
\`\`\`

2. **Create Gunicorn configuration:**
\`\`\`python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
\`\`\`

3. **Run with Gunicorn:**
\`\`\`bash
gunicorn main:app -c gunicorn.conf.py
\`\`\`

### Environment Variables for Production

\`\`\`bash
# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
MYSQL_HOST=your-production-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=shopify_insights

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key-here
\`\`\`

### Nginx Configuration

\`\`\`nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
\`\`\`

## Cloud Deployment

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 20.04 LTS recommended)
2. **Install dependencies:**
\`\`\`bash
sudo apt update
sudo apt install python3.13 python3-pip mysql-server nginx
\`\`\`

3. **Setup MySQL:**
\`\`\`bash
sudo mysql_secure_installation
sudo mysql -u root -p
CREATE DATABASE shopify_insights;
CREATE USER 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;
\`\`\`

4. **Deploy application** following the production deployment steps above

### Google Cloud Platform

1. **Create Compute Engine instance**
2. **Setup Cloud SQL for MySQL**
3. **Deploy application** using the production deployment guide
4. **Configure Load Balancer** if needed

### Heroku

1. **Create Heroku app:**
\`\`\`bash
heroku create your-app-name
\`\`\`

2. **Add MySQL addon:**
\`\`\`bash
heroku addons:create cleardb:ignite
\`\`\`

3. **Set environment variables:**
\`\`\`bash
heroku config:set DEBUG=false
heroku config:set OPENAI_API_KEY=your-key
\`\`\`

4. **Deploy:**
\`\`\`bash
git push heroku main
\`\`\`

## Monitoring and Maintenance

### Health Checks

The application provides a health check endpoint:
\`\`\`
GET /api/v1/health
\`\`\`

### Database Maintenance

\`\`\`bash
# Get database statistics
python scripts/database_utils.py stats

# Clean up old data
python scripts/database_utils.py cleanup

# Create backup
python scripts/database_utils.py backup
\`\`\`

### Logging

Logs are written to stdout by default. In production, configure log rotation:

\`\`\`bash
# Using logrotate
sudo nano /etc/logrotate.d/shopify-insights
\`\`\`

### Performance Tuning

1. **Database optimization:**
   - Add indexes for frequently queried fields
   - Configure MySQL for your workload
   - Use connection pooling

2. **Application optimization:**
   - Adjust worker count based on CPU cores
   - Configure request timeouts
   - Implement caching for frequently accessed data

3. **System optimization:**
   - Configure firewall rules
   - Set up SSL/TLS certificates
   - Monitor resource usage

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check MySQL service status
   - Verify connection credentials
   - Ensure database exists

2. **Import errors:**
   - Verify Python version (3.13+)
   - Check virtual environment activation
   - Reinstall dependencies

3. **Permission errors:**
   - Check file permissions
   - Verify user privileges
   - Check SELinux/AppArmor settings

### Getting Help

- Check application logs
- Review error messages
- Consult the README.md file
- Check GitHub issues
\`\`\`
