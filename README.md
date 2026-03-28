# ממזג — Production Deployment

## Prerequisites

- Ubuntu server with Docker + Docker Compose installed
- Domain `mimzag.com` DNS A record pointing to the server's public IP
- Port 80 and 443 open in the server firewall

---

## Setup (shares Caddy with the existing server project)

HTTPS is handled automatically by the **existing Caddy instance** on the server —
no Nginx, no Certbot needed for this project.

### 1. Copy project to server

```bash
scp -r . user@your-server-ip:/opt/mimzag
ssh user@your-server-ip
cd /opt/mimzag
```

### 2. Create the shared Docker network (once, if it doesn't exist yet)

```bash
docker network create caddy_net
```

> If the other project already created `caddy_net`, this command will fail with
> "already exists" — that's fine, skip it.

### 3. Make sure the existing Caddy container is on `caddy_net`

In the **other project's** `docker-compose.yml`, the Caddy service must have:

```yaml
networks:
  - caddy_net

networks:
  caddy_net:
    external: true
```

Then reload it: `docker compose up -d caddy`

### 4. Update the Caddyfile on the server

Copy the updated `Caddyfile` from this repo (it already includes the `mimzag.com` block)
to the other project's directory, then reload Caddy:

```bash
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### 5. Create `.env` on the server

```bash
cat > /opt/mimzag/.env << 'EOF'
GMAIL_USER=mimzag1@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
EOF
```

### 6. Start the app

```bash
cd /opt/mimzag
docker compose up -d --build
```

Point `mimzag.com` DNS A record → server IP.
Caddy will automatically issue and renew the Let's Encrypt certificate.

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
