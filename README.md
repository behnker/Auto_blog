# Auto_Blog (Multi-Tenant)

An automated, self-writing blog platform powered by **Anthropic Claude**, **Airtable**, and **FastAPI**.
Supports multiple blogs from a single deployment.

## Architecture

This project follows a 3-Layer Agentic Architecture:

1.  **Directives (`directives/`)**:
    - Markdown files defining the SOPs (Standard Operating Procedures) for the AI.
    - Example: `generate_daily_post.md`.

2.  **Orchestration (The AI)**:
    - The AI agent reads directives and calls execution scripts.

3.  **Execution (`execution/`)**:
    - `server.py`: Multi-tenant FastAPI app. Routes traffic based on the `Host` header to the correct blog config.
    - `generate_post.py`: Generates content. Accepts `--blog-id` to target a specific blog's Airtable Base.

4.  **Configuration (`config/`)**:
    - `blogs.yaml`: Registry of all active blogs and their settings.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Copy `.env.example` to `.env`.
    - `ANTHROPIC_API_KEY`: Master API key.
    - `CRON_SECRET`: Master webhook secret.
    - API keys for individual blogs can be defined here or referenced in `blogs.yaml`.

3.  **Configure Blogs**:
    Edit `config/blogs.yaml` to add your blogs.

4.  **Run Locally**:
    ```bash
    uvicorn execution.server:app --reload
    ```
    *Note: To test multi-tenancy locally, mapping in hosts file might be needed, or use localhost with different paths if configured.*

## Deployment (Railway)

- Connect your GitHub repo.
- configure necessary environment variables.
