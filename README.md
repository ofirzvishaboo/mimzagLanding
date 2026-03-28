# ממזג — Production Deployment

## Prerequisites

- Ubuntu server with Docker + Docker Compose installed
- Domain `mimzag.com` DNS A record pointing to the server's public IP
- Port 80 and 443 open in the server firewall

---

## First-Time Setup

### 1. Copy project to server

```bash
scp -r . user@your-server-ip:/opt/mimzag
ssh user@your-server-ip
cd /opt/mimzag
```

### 2. Create `.env` on the server

```bash
cat > .env << 'EOF'
GMAIL_USER=mimzag1@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
EOF
```

### 3. Start Nginx on HTTP only (needed for Certbot challenge)

```bash
docker compose up -d nginx
```

### 4. Issue the SSL certificate (one-time)

```bash
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d mimzag.com -d www.mimzag.com \
  --email mimzag1@gmail.com \
  --agree-tos --no-eff-email
```

### 5. Download recommended SSL options from Let's Encrypt

```bash
docker compose exec nginx sh -c "\
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
  > /etc/letsencrypt/options-ssl-nginx.conf && \
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
  > /etc/letsencrypt/ssl-dhparams.pem"
```

### 6. Start everything

```bash
docker compose up -d
```

Visit **https://mimzag.com** — HTTPS with a valid certificate.

---

## Auto-renewal

The `certbot` container already runs `certbot renew` every 12 hours automatically.  
Reload nginx after renewal by adding this to the server's crontab (`crontab -e`):

```cron
0 3 * * * docker compose -f /opt/mimzag/docker-compose.yml exec nginx nginx -s reload
```

---

## Updating the app

```bash
cd /opt/mimzag
git pull          # or scp new files
docker compose up -d --build app
```

---

## Useful commands

| Command | Description |
|---|---|
| `docker compose logs -f app` | Live FastAPI logs |
| `docker compose logs -f nginx` | Live Nginx logs |
| `docker compose restart nginx` | Reload Nginx config |
| `docker compose down` | Stop everything |
| `docker compose ps` | Check service status |
