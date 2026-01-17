# Auto_Blog (Multi-Tenant)

An automated, self-writing blog platform powered by **Anthropic Claude**, **Airtable**, and **FastAPI**.
Supports multiple blogs from a single deployment, with unique personas and content strategies.

## Architecture

This project follows a 3-Layer Agentic Architecture:

1.  **Directives (`directives/`)**:
    - Markdown files defining the SOPs (Standard Operating Procedures) for the AI.
    - Example: `generate_daily_post.md`.
    - Prompts: `directives/prompts/{blog_id}.md` contains the System Prompt (persona) for each blog.

2.  **Orchestration (The AI)**:
    - The AI agent reads directives and calls execution scripts.
    - **Trigger**: A CRON job or Webhook hits `POST /api/cron/generate`.
    - **Background Task**: The server spawns a background process running `execution/generate_post.py`.

3.  **Execution (`execution/`)**:
    - `server.py`: Multi-tenant FastAPI app. Routes traffic based on the `Host` header to the correct blog config.
    - `generate_post.py`: Generates content using Claude. Accepts `--blog-id` to target a specific blog's Airtable Base.

4.  **Configuration (`config/`)**:
    - `blogs.yaml`: Registry of all active blogs and their settings (Domain, ID, etc.).

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Copy `.env.example` to `.env`.
*   `ANTHROPIC_API_KEY`: Master API key for Claude.
*   `CRON_SECRET`: Secret token for securing the generation webhook.
*   `ADMIN_PASSWORD`: Password for the Dashboard (default: `admin`).
*   `AIRTABLE_BASE_ID`: (Optional) Default Base ID if not specified per blog.

### 3. Airtable Migration (Crucial for v1.1)
The data schema has been expanded. Run the helper script to see exactly which tables and fields to create:
```bash
python -m scripts.print_schema_instructions
```

### 4. Configure Blogs
Edit `config/blogs.yaml` to register your blogs:
```yaml
blogs:
  - id: "my_tech_blog"
    name: "My Tech Blog"
    domain: "tech.example.com"
    airtable:
      base_id_env: "TECH_BLOG_BASE_ID"
      table_name: "Posts"
    # v1.1 Enhancements
    primary_objective: "Authority"
```

### 5. Run Locally
```bash
uvicorn execution.server:app --reload
```
*   **Public Site**: `http://localhost:8000`
*   **Admin Dashboard**: `http://localhost:8000/admin/dashboard` (Navigation to Agencies, Authors, Voices, Settings)
*   **Sitemap**: `http://localhost:8000/sitemap.xml`

## Usage

### Triggering Content Generation
You can manually trigger a post generation via the API (or set this up as a Cron Job):

**Standard (v1.1)**
```bash
curl -X POST "http://localhost:8000/api/cron/generate?blog_id=example_blog&token=YOUR_CRON_SECRET"
```

**Search-Optimised (v2.0)**
To force the v2.0 contract (Rich content, Schema, QA Scoring):
```bash
# Via CLI:
python -m execution.generate_post --blog-id example_blog --force-v2
```

The server will respond immediately with `{"status": "queued"}`, and the generation script will run in the background.

### Viewing Logs
Check the terminal output where `uvicorn` is running to see the progress of the `generate_post.py` script.

## Roadmap & Specification
For a detailed technical breakdown and future plans, see [SPECIFICATION.md](SPECIFICATION.md).
