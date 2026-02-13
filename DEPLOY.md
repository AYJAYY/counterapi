# Counter API — Deployment Guide

Follows the same pattern as the Inclusiv deployment (nginx custom ports, Let's Encrypt SSL, systemd).

## Port Allocation

| Application | HTTP Port | HTTPS Port | App Port |
|-------------|-----------|------------|----------|
| Inclusiv    | 8090      | 8453       | 5000     |
| Counter API | 8732      | 8733       | 8001     |

## 1. Server Setup

```bash
# Clone project to server
cd /home/python
git clone https://github.com/AYJAYY/counterapi.git
cd counterapi

# Create virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. DNS

Add an **A record** for the subdomain pointing to your VPS IP:

| Type | Name | Content |
|------|------|---------|
| A | counter | YOUR_VPS_IP |

This creates `counter.bullock.app`.

## 3. Firewall

```bash
sudo ufw allow 8732
sudo ufw allow 8733
```

## 4. SSL Certificate

```bash
# Temporarily allow port 80 for certbot
sudo ufw allow 80
sudo systemctl stop nginx

sudo certbot certonly --standalone -d counter.bullock.app

sudo systemctl start nginx
sudo ufw delete allow 80
```

## 5. nginx

```bash
sudo cp deploy/counterapi.nginx /etc/nginx/sites-available/counterapi
sudo ln -s /etc/nginx/sites-available/counterapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. systemd Service

```bash
sudo cp deploy/counterapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable counterapi
sudo systemctl start counterapi
```

## 7. Verify

```bash
# Health check
curl -I http://counter.bullock.app:8732/api/health
curl -I https://counter.bullock.app:8733/api/health

# Create and hit a counter
curl -X POST https://counter.bullock.app:8733/api/counters \
  -H 'Content-Type: application/json' -d '{"name":"test"}'
curl -X POST https://counter.bullock.app:8733/api/counters/test/hit
curl https://counter.bullock.app:8733/api/counters/test

# Test SSL certificate
openssl s_client -connect counter.bullock.app:8733 -servername counter.bullock.app
```

## 8. SSL Auto-Renewal

```bash
sudo crontab -e
# Add:
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## Useful Commands

```bash
sudo systemctl status counterapi    # Check status
sudo journalctl -u counterapi -f    # Follow logs
sudo systemctl restart counterapi   # Restart
```
