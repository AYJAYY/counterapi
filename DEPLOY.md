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

## 2. Firewall

```bash
sudo ufw allow 8732
sudo ufw allow 8733
```

## 3. SSL Certificate

The existing Let's Encrypt certificate for `bullock.app` is reused (already set up for Inclusiv). No additional cert needed.

## 4. nginx

```bash
sudo cp deploy/counterapi.nginx /etc/nginx/sites-available/counterapi
sudo ln -s /etc/nginx/sites-available/counterapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 5. systemd Service

```bash
sudo cp deploy/counterapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable counterapi
sudo systemctl start counterapi
```

## 6. Verify

```bash
# Health check
curl -I http://bullock.app:8732/api/health
curl -I https://bullock.app:8733/api/health

# Create and hit a counter
curl -X POST https://bullock.app:8733/api/counters \
  -H 'Content-Type: application/json' -d '{"name":"test"}'
curl -X POST https://bullock.app:8733/api/counters/test/hit
curl https://bullock.app:8733/api/counters/test

# Test SSL certificate
openssl s_client -connect bullock.app:8733 -servername bullock.app
```

## 7. SSL Auto-Renewal

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
