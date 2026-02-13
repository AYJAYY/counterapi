# Counter API — Deployment Guide

Follows the same pattern as the Inclusiv deployment (nginx custom ports, Let's Encrypt, Cloudflare DNS-only, systemd).

## 1. Server Setup

```bash
# Clone or copy project to server
cd /home/python
git clone <repo-url> counterapi
cd counterapi

# Create virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Cloudflare DNS

Add an **A record** (DNS-only / gray cloud):

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | counter | YOUR_VPS_IP | DNS only |

This creates `counter.inclusiv.click`.

## 3. Firewall

```bash
sudo ufw allow 8732
sudo ufw allow 8733
```

## 4. SSL Certificate

```bash
# Temporarily allow port 80 for certbot
sudo ufw allow 80
sudo certbot certonly --standalone -d counter.inclusiv.click
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
curl http://counter.inclusiv.click:8732/api/health
curl https://counter.inclusiv.click:8733/api/health

# Create and hit a counter
curl -X POST https://counter.inclusiv.click:8733/api/counters \
  -H 'Content-Type: application/json' -d '{"name":"test"}'
curl -X POST https://counter.inclusiv.click:8733/api/counters/test/hit
curl https://counter.inclusiv.click:8733/api/counters/test
```

## 8. SSL Auto-Renewal

Add a cron job:

```bash
sudo crontab -e
# Add:
0 3 1 * * certbot renew --quiet && systemctl reload nginx
```

## Useful Commands

```bash
sudo systemctl status counterapi    # Check status
sudo journalctl -u counterapi -f    # Follow logs
sudo systemctl restart counterapi   # Restart
```
