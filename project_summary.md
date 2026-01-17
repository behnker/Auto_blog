# Auto_Blog Project Summary

This document summarizes the changes made during the "Multi-Agency & SEO" upgrade (Phases 1-3).

## 🌟 New Capabilities

### 1. Multi-Agency Architecture
*   **Tenancy**: Supports multiple agencies/blogs from one codebase.
*   **Admin Dashboard**: `/admin` interface to view blog status.
*   **Session Auth**: Simple password-based protection for admin routes.

### 2. Search-Optimised Content Engine (v2.0)
*   **Dual-Contract System**:
    *   **v1.1**: Standard posts (Objective-aware).
    *   **v2.0**: SEO Heavy (Schema, FAQ, TL;DR, Entities).
*   **Automated QA**: Every v2.0 post is scored (0-100) on "GEO/AEO Readiness" before publishing.
*   **Structured Output**: Claude now returns strict JSON for robust parsing.

### 3. SEO Suite
*   **Sitemap & RSS**: Auto-generated endpoints at `/sitemap.xml` and `/rss.xml`.
*   **Metadata**: Full control over Meta Titles, Descriptions, and Canonical URLs.

## 📂 Key Files Added/Modified

*   **`execution/models_v2.py`**: Pydantic models & Scoring Logic.
*   **`execution/generate_post.py`**: The "Brain" - handles prompting, routing, and Airtable storage.
*   **`scripts/print_schema_instructions.py`**: Helper to manage the Airtable Schema.
*   **`templates/admin/`**: UI for the Dashboard.

## 🚀 Getting Started (Post-Handoff)

1.  **Update Airtable**: Run `python -m scripts.print_schema_instructions` and create the fields.
2.  **Configure Blog**: Set `primary_objective` in `blogs.yaml`.
3.  **Run Server**: `uvicorn execution.server:app --reload`.
4.  **Generate**: Try `python -m execution.generate_post --blog-id example_blog --force-v2`.

## 🔮 Future Roadmap ideas
See `ROADMAP.md` for the detailed Phase 4 Plan (Agency Workbench), including:
*   **Brand Voice Profiles**: Authenticity at scale.
*   **Content Brief Objects**: Research-first workflow.
*   **Performance Loops**: Auto-refreshing decaying content.
