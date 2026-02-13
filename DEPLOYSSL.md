# Inclusiv - Direct SSL Deployment Guide

This guide documents the **proven working solution** for deploying Inclusiv with SSL using custom ports on a multi-application server.

## 📋 The Working Solution

This approach uses **Cloudflare DNS-only** (gray cloud) with **Let's Encrypt SSL certificates** and **custom ports** to avoid conflicts with other applications on the same server.

### Why This Solution Works

1. **Custom Ports**: Avoids conflicts with other web applications (8090/8453 instead of 80/443)
2. **Direct Connection**: Bypasses Cloudflare proxy limitations with custom ports
3. **Trusted SSL**: Let's Encrypt provides browser-trusted certificates
4. **Simple Configuration**: Minimal nginx config reduces complexity
5. **Multi-App Friendly**: Each application can use its own port range

---

## Step-by-Step Implementation

### Step 1: Cloudflare DNS Configuration

1. **Go to Cloudflare DNS Dashboard**
2. **Set A Record to DNS-Only**:
   - Type: `A`
   - Name: `@` (for bullock.app root domain)
   - IPv4 address: Your VPS IP address
   - Proxy status: **DNS only** (gray cloud) ⚫
   - TTL: Auto

3. **Add www CNAME** (optional):
   - Type: `CNAME`
   - Name: `www`
   - Target: `bullock.app`
   - Proxy status: **DNS only** (gray cloud) ⚫

### Step 2: VPS Firewall Configuration

```bash
# Allow custom HTTP and HTTPS ports for Inclusiv
sudo ufw allow 8090
sudo ufw allow 8453

# Check firewall status
sudo ufw status

# Should show:
# 8090                       ALLOW       Anywhere
# 8453                       ALLOW       Anywhere
```

### Step 3: Install Let's Encrypt SSL Certificate

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily (if running)
sudo systemctl stop nginx

# Get SSL certificate for your domain
sudo certbot certonly --standalone -d bullock.app -d www.bullock.app

# For Inclusiv subdomain (optional):
# sudo certbot certonly --standalone -d inclusiv.bullock.app

# Start nginx
sudo systemctl start nginx
```

### Step 4: Nginx Configuration

Create the nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/inclusiv
```

Add this **proven working configuration**:

```nginx
# HTTP server - redirects to HTTPS on custom port
server {
    listen 8090;
    server_name bullock.app www.bullock.app;
    return 301 https://bullock.app:8453$request_uri;
}

# HTTPS server - main application
server {
    listen 8453 ssl http2;
    server_name bullock.app www.bullock.app;

    # Let's Encrypt SSL Configuration
    ssl_certificate /etc/letsencrypt/live/bullock.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bullock.app/privkey.pem;
    
    # Simple SSL settings (let nginx handle defaults)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Application proxy
    location / {
        proxy_pass http://127.0.0.1:5000;  # Inclusiv runs on port 5000 by default
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Additional headers for Flask applications
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
    }

    # Static files
    location /static {
        alias /home/python/Inclusiv/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers for Inclusiv
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
}
```

### Step 5: Enable and Test Configuration

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/inclusiv /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Verify ports are listening
sudo netstat -tlnp | grep -E ':(8090|8453)'
```

### Step 6: Configure Inclusiv Application

#### Option A: Using Systemd Service (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/inclusiv.service
```

Add this configuration:

```ini
[Unit]
Description=Inclusiv - GLTHS Accessibility Fix Tracker
After=network.target

[Service]
Type=simple
User=python
WorkingDirectory=/home/python/Inclusiv
Environment=PATH=/home/python/Inclusiv/venv/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
ExecStart=/home/python/Inclusiv/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable inclusiv
sudo systemctl start inclusiv

# Check status
sudo systemctl status inclusiv
```

#### Option B: Using Supervisor

Install supervisor:

```bash
sudo apt install supervisor -y
```

Create supervisor configuration:

```bash
sudo nano /etc/supervisor/conf.d/inclusiv.conf
```

Add this configuration:

```ini
[program:inclusiv]
command=/home/python/Inclusiv/venv/bin/python app.py
directory=/home/python/Inclusiv
user=python
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/inclusiv.log
environment=FLASK_ENV=production
```

Start the service:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start inclusiv
```

### Step 7: Test the Deployment

```bash
# Test HTTP redirect
curl -I http://bullock.app:8090

# Test HTTPS connection
curl -I https://bullock.app:8453

# Test SSL certificate
openssl s_client -connect bullock.app:8453 -servername bullock.app

# Test Inclusiv login page
curl -I https://bullock.app:8453/login
```

---

## SSL Certificate Management

### Automatic Renewal Setup

Let's Encrypt certificates expire every 90 days. Set up automatic renewal:

```bash
# Test renewal process
sudo certbot renew --dry-run

# Set up automatic renewal (add to crontab)
sudo crontab -e

# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

### Manual Renewal

```bash
# Renew certificates manually
sudo certbot renew

# Reload nginx after renewal
sudo systemctl reload nginx
```

---

## Environment Configuration

### Production Environment Variables

Create a production `.env` file:

```bash
cd /home/python/Inclusiv
cp .env.example .env
nano .env
```

Configure for production:

```env
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production

# Authentication Settings
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-very-secure-password

# SSL Configuration (disable since nginx handles SSL)
SSL_ENABLED=false
HTTP_PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///instance/accessibility_tracker.db

# Security Settings
SESSION_TIMEOUT=3600
```

**Important**: Use strong, unique passwords and secret keys in production!

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Nginx Configuration Test Fails

```bash
# Check syntax
sudo nginx -t

# Common issues:
# - Missing semicolons
# - Incorrect file paths
# - SSL certificate not found
# - Wrong proxy_pass port (should be 5000 for Inclusiv)
```

#### 2. Certificate Not Found Error

```bash
# Verify certificate exists
sudo ls -la /etc/letsencrypt/live/bullock.app/

# Should show:
# fullchain.pem
# privkey.pem
```

#### 3. Inclusiv Application Not Responding

```bash
# Check if Inclusiv is running on port 5000
sudo netstat -tlnp | grep :5000

# Check systemd service status
sudo systemctl status inclusiv

# Check logs
sudo journalctl -u inclusiv -f

# Or if using supervisor:
sudo supervisorctl status
sudo tail -f /var/log/inclusiv.log

# Restart if needed
sudo systemctl restart inclusiv
# Or: sudo supervisorctl restart inclusiv
```

#### 4. Database Issues

```bash
# Check if database exists
ls -la /home/python/Inclusiv/instance/

# Initialize database if needed
cd /home/python/Inclusiv
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 5. Permission Issues

```bash
# Fix ownership of Inclusiv directory
sudo chown -R python:python /home/python/Inclusiv

# Ensure database directory is writable
chmod 755 /home/python/Inclusiv/instance
```

#### 6. Firewall Blocking Connections

```bash
# Check firewall rules
sudo ufw status

# Ensure ports are allowed
sudo ufw allow 8090
sudo ufw allow 8453
```

---

## Security Considerations

### 1. Firewall Configuration

```bash
# Only allow necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8090  # Inclusiv HTTP
sudo ufw allow 8453  # Inclusiv HTTPS
sudo ufw enable
```

### 2. Inclusiv Security Features

Inclusiv includes built-in security features:

- **Password Hashing**: bcrypt with automatic salt generation
- **Brute Force Protection**: IP-based lockout (5 attempts, 15-minute cooldown)
- **Security Logging**: Comprehensive authentication event logging
- **Session Management**: 1-hour timeout with secure cookies
- **CSRF Protection**: All forms protected with CSRF tokens

### 3. Additional Security Headers

The nginx configuration already includes security headers. Monitor the security log:

```bash
# Monitor Inclusiv security log
tail -f /home/python/Inclusiv/security.log
```

### 4. Regular Updates

```bash
# Keep system updated
sudo apt update && sudo apt upgrade -y

# Update Inclusiv
cd ~/Inclusiv
git pull origin master
sudo systemctl restart inclusiv
```

---

## Multi-Application Server Setup

### Adding Additional Applications

This setup allows you to run multiple applications on the same server using different port ranges:

| Application | HTTP Port | HTTPS Port | App Port |
|-------------|-----------|------------|----------|
| Inclusiv    | 8090      | 8453       | 5000     |
| App 2       | 8091      | 8454       | 5001     |
| App 3       | 8092      | 8455       | 5002     |

### Example Additional App Configuration

```nginx
# Application 2: Another Flask app (ports 8091/8454)
server {
    listen 8091;
    server_name app2.yourdomain.com;
    return 301 https://app2.yourdomain.com:8454$request_uri;
}

server {
    listen 8454 ssl http2;
    server_name app2.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/app2.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app2.yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    location / {
        proxy_pass http://127.0.0.1:5001;  # Different app port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Monitoring and Maintenance

### Log Locations

```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Inclusiv application logs
sudo journalctl -u inclusiv -f
# Or: sudo tail -f /var/log/inclusiv.log (if using supervisor)

# Inclusiv security logs
tail -f /home/python/Inclusiv/security.log

# SSL certificate logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Health Checks

```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status inclusiv
sudo ufw status

# Test application endpoints
curl -I https://bullock.app:8453
curl -I https://bullock.app:8453/login
curl -I https://bullock.app:8453/fixes

# Check database
cd /home/python/Inclusiv
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); print('Database tables:', db.engine.table_names())"
```

### Backup Strategy

```bash
# Backup Inclusiv database
cd /home/python/Inclusiv
cp instance/accessibility_tracker.db backups/accessibility_tracker_$(date +%Y%m%d_%H%M%S).db

# Create full application backup
tar -czf inclusiv_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    /home/python/Inclusiv \
    --exclude=/home/python/Inclusiv/venv \
    --exclude=/home/python/Inclusiv/.git
```

---

## Performance Optimization

### 1. Nginx Optimization

Add to `/etc/nginx/nginx.conf` in the http block:

```nginx
# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

# Connection optimization
keepalive_timeout 65;
keepalive_requests 100;
```

### 2. Flask Application Optimization

For production, consider using Gunicorn:

```bash
# Install Gunicorn
cd /home/python/Inclusiv
source venv/bin/activate
pip install gunicorn

# Update systemd service to use Gunicorn
sudo nano /etc/systemd/system/inclusiv.service
```

Update the ExecStart line:

```ini
ExecStart=/home/python/Inclusiv/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 app:app
```

---

## Summary

This deployment solution provides:

✅ **SSL encryption** with Let's Encrypt certificates  
✅ **Custom ports** to avoid conflicts with other applications  
✅ **Direct connection** for better performance  
✅ **Browser-trusted certificates** with no security warnings  
✅ **Automatic certificate renewal**  
✅ **Production-ready Flask deployment**  
✅ **Built-in Inclusiv security features**  
✅ **Multi-application support** on the same server  

The key insight is using **custom ports with Let's Encrypt** provides the most reliable SSL solution for direct connections while maintaining Inclusiv's built-in security features.

---

## Quick Reference Commands

```bash
# Test SSL connection
curl -I https://bullock.app:8453

# Check certificate expiry
sudo certbot certificates

# Renew certificates
sudo certbot renew && sudo systemctl reload nginx

# Restart Inclusiv
sudo systemctl restart inclusiv

# Check Inclusiv logs
sudo journalctl -u inclusiv -f

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check Inclusiv security log
tail -f /home/python/Inclusiv/security.log

# Database backup
cd /home/python/Inclusiv && cp instance/accessibility_tracker.db backups/backup_$(date +%Y%m%d).db
```