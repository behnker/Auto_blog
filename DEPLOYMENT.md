# Deployment Guide

This guide outlines the steps to prepare and deploy the Auto_Blog platform to a production environment (e.g., VPS, DigitalOcean, AWS EC2, or Railway/Render).

## 1. Prerequisites

Ensure the following are ready:

-   **Server**: Linux (Ubuntu 20.04/22.04 LTS recommended) or a PaaS container.
-   **Python**: Version 3.10 or higher.
-   **Domain**: A generic domain pointing to the server IP (e.g., `admin.yoursite.com`).

## 2. Environment Variables

In production, **do not** use `.env` files if possible. Inject these variables directly into your environment configuration.

| Variable | Description | Required | Example |
| :--- | :--- | :--- | :--- |
| `ANTHROPIC_API_KEY` | Your Claude API Key | Yes | `sk-ant-...` |
| `ADMIN_PASSWORD` | Password for Admin UI | Yes | `SecureP@ssw0rd!` |
| `CRON_SECRET` | Secret token for API triggers | Yes | `random-uuid-string` |
| `AIRTABLE_API_KEY` | Airtable Personal Access Token | Yes | `pat...` |
| `BLOG_1_BASE_ID` | Base ID for Blog 1 | No | `app...` |

## 3. Production Dependencies

Ensure `gunicorn` is installed for production process management (Uvicorn sits behind it).

```bash
pip install gunicorn
```

## 4. Startup Command

For production, run with Gunicorn using Uvicorn workers:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker execution.server:app --bind 0.0.0.0:8000
```

-   `-w 4`: Number of worker processes (usually 2 x CPU cores + 1).
-   `--bind 0.0.0.0:8000`: Expose on port 8000.

## 5. Reverse Proxy (Nginx)

It is highly recommended to put Nginx in front of Gunicorn to handle SSL and header forwarding.

### Example Nginx Config

```nginx
server {
    listen 80;
    server_name admin.yoursite.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. Verification Checklist

-   [ ] **Static Files**: Ensure local directory `static/` is mounted/accessible if running in Docker.
-   [ ] **Airtable**: Verify the server IP is not blocked by Airtable (rare, but possible).
-   [ ] **SSL**: Use Certbot to enable HTTPS: `sudo certbot --nginx`.
-   [ ] **Cron Jobs**: Set up external cron triggers (e.g., GitHub Actions, Cron-job.org) to hit `https://your-domain.com/api/cron/generate?token=YOUR_CRON_SECRET`.
