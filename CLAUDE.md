# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A visitor counter API service. Users create named counters, embed SVG badges on their sites, and track unique visitors by IP address. Built with FastAPI + aiosqlite, deployed behind nginx on bullock.app.

## Commands

```bash
# Install dependencies
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Run the dev server
uvicorn app.main:app --reload --port 8001

# No test suite or linter is configured
```

## Architecture

- **`app/main.py`** — FastAPI app setup, CORS middleware, lifespan (DB init), serves `index.html` at `/`
- **`app/routes.py`** — All API routes under `/api` prefix: CRUD counters, hit endpoint (increments by unique IP), SVG badge endpoint
- **`app/db.py`** — aiosqlite database layer. Two tables: `counters` (name, count, created_at) and `hits` (counter_name, ip — used for unique visitor dedup). DB file is `counter.db` in the working directory
- **`app/badge.py`** — Generates shields.io-style SVG badges with optional embedded GLTH icon (base64 PNG)
- **`app/static/index.html`** — Single-page dashboard (vanilla JS) for managing counters and getting embed snippets

## Key Behaviors

- Counter names are validated against `^[a-zA-Z0-9_-]+$`
- `POST /api/counters/{name}/hit` auto-creates the counter if it doesn't exist
- Unique visitors are tracked by IP via the `hits` table (composite PK on counter_name + ip)
- The badge endpoint (`/api/counters/{name}/badge.svg`) accepts `?hit=true` to count and render in one request, plus `?icon=true`, `?label=`, `?color=` params
- IP is extracted from `X-Forwarded-For` header (set by nginx), falling back to `request.client.host`

## Deployment

Production runs on bullock.app:8733 (HTTPS) via systemd + nginx reverse proxy. Config files are in `deploy/`. See `DEPLOY.md` for full setup steps.
