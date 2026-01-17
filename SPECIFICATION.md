# Auto_Blog Specification

## 1. Executive Summary
Auto_Blog is a multi-tenant, automated blogging platform that leverages AI (Anthropic Claude) to generate and publish content. It uses a single FastAPI deployment to serve multiple distinct blogs, identified by their domain names. Content is managed and stored in Airtable, acting as a Headless CMS.

## 2. System Architecture (v1.1 Consolidated)

### 2.1 Multi-Tenancy & Hybrid Workflow
*   **Tenancy**: Shared Airtable Base. Records scoped by `Agency`.
*   **Workflow**: AI Draft -> QA Check (AEO Score) -> Human Review -> Redraft Loop -> Approval -> Publish.
*   **Contracts**:
    *   **v1.1**: Basic Post (Objective-aware).
    *   **v2.0**: Search-Optimised Package (SEO + GEO/AEO + LLM Extraction).
*   **Objective Inheritance**:
    *   **PrimaryObjective**: Defined at **Blog** level (Airtable-only). Inherited by **Posts** (Read-only Lookup).
    *   **SecondaryObjective**: Optional per-post override (Editable in App).
    *   **PostIntentNote**: Free-text nuance per post.

### 2.2 Core Components
*   **Web Server (FastAPI)**:
    *   **Public Blog Routes**: Domain-based routing, Cached Responses, Sanitized HTML.
    *   **Admin Dashboard**: Workflow-centric (Review Studio vs CRUD).
    *   **SEO Engine**: Auto-generates Sitemaps, RSS, and Meta Tags.
*   **Content Engine (Python/Claude)**:
    *   **Contract v1.1**: JSON-based Structured Output (Basic).
    *   **Contract v2.0**: Enhanced Package (Body + TLDR + FAQ + Schema + QA Report).
    *   **Safety**: Output validation via Pydantic (Warn-only for v2.0 Schema).
*   **Reliability Layer**:
    *   **Queue**: (Roadmap) Redis/Celery for job persistence.
    *   **Current State**: BackgroundTasks with "Processing" state tracking and Idempotency logic.
    *   **Caching**: In-memory cache for Published Posts (TTL 60s).

### 2.3 Security & Authentication
*   **Admin Access**: Session-based Auth.
*   **Isolation**: Strict filtering by `BlogID`.
*   **Rate Limiting**: Limit generation requests per tenant.

## 3. Data Schema (Expanded for v1.1)

### 3.1 Enums
*   **ObjectiveEnum**: `Traffic`, `Leads`, `Authority`, `Distribution`, `Revenue`, `AffiliateRevenue`.
*   **MetricEnum**: `Traffic`, `LeadsGenerated`, `Authority`, `Distribution`, `Revenue`, `AffiliateRevenue`.
*   **IntentEnum**: `Educate`, `Persuade`, `Convert`, `Compare`, `Explain`.
*   **StatusEnum**: `Draft`, `InReview`, `ChangesRequested`, `RedraftGenerated`, `Approved`, `Scheduled`, `Published`, `Archived`.

### 3.2 Key Tables

#### 1. Agencies
*   **Name**, **Administrator**, **Blogs** (Link), **Authors** (Link).

#### 2. Blogs
*   **Agency** (Link): Tenant Key.
*   **Name**, **Domain**.
*   **GenerationContractDefault** (Single Select): `v1.1` or `v2.0`.
*   **PrimaryObjective** (Single Select -> **ObjectiveEnum**): **Authoritative Source**.
*   **DefaultMetricFocus** (MetricEnum), **DefaultIntent** (IntentEnum).
*   **VoiceAndStyle**, **HardRules** (Long Text).
*   **Authors** (Link), **Knowledge_Base** (Link).

#### 3. Posts
*   **Agency** (Link), **Blog** (Link), **Author** (Link).
*   **Title**, **Slug**, **Content**, **PublishedDate**.
*   **Status** (StatusEnum).
*   **PrimaryObjective** (Lookup), **SecondaryObjective**, **PostIntentNote**.
*   **v2.0 Content Fields**: `TLDR`, `FAQ_JSON`, `HowTo_JSON`, `Tables_JSON`, `Glossary_JSON`.
*   **v2.0 Metadata**: `MetaTitle`, `MetaDescription`, `CanonicalUrl`, `Tags`, `Entities_JSON`.
*   **v2.0 Distribution**: `LLM_SnippetPack_JSON`, `Schema_JSONLD`, `Citations_JSON`.
*   **QA & Audit**: `ContractVersion`, `QA_Score_GEO_AEO` (0-100), `QA_Report_JSON`, `GeneratorInput_JSON`, `GeneratorOutput_JSON`.

## 4. Generation Contracts

### 4.1 v1.1 (Basic)
*   **Input/Output**: Standard fields + Objectives.

### 4.2 v2.0 (Search-Optimised)
*   **Input Adds**: `search_targets`, `content_requirements`, `knowledge_injection`.
*   **Output Adds**:
    *   **Content Package**: TLDR, FAQ, HowTo, Tables, Glossary.
    *   **Metadata Pack**: SEO tags + Entities.
    *   **LLM Pack**: Summary, Takeaways, Q&A snippets.
    *   **QA Report**: Automated scoring for AEO readiness.

## 5. GEO/AEO Readiness Scoring (0-100)

Automated grader runs on every v2.0 generation.
*   **A) AEO Packaging (25pts)**: TLDR, FAQ, Clear Structure.
*   **B) Entity Coverage (20pts)**: Entities list, Glossary, Body usage.
*   **C) Structured Data (20pts)**: Valid JSON-LD (Warn-only).
*   **D) Trust (15pts)**: Citations (if enabled).
*   **E) Metadata (10pts)**: Titles, Descriptions, Canonical.
*   **F) LLM Extraction (10pts)**: Snippet pack existence.

## 5. Web Application UX (Agency Owner)

### 5.1 Blog Catalog
*   Graphic tiles layout.
*   Shows **PrimaryObjective** (Locked/Read-only).
*   **SEO Status**: Indicators for Sitemap/RSS health.

### 5.2 Post Dashboard
*   Filter by Status (Draft, NeedsReview, Published).
*   **QA Status**: Warn if `QA_Passed` is false.

### 5.3 Review Studio (Hybrid Loop)
*   **Workflow**: "Generate Now" button with streaming logs.
*   **Review**: Diff view, Metadata editor (SEO tags).
*   **Action**: Approve (Publish) or Request Changes (Redraft).

## 6. Reliability & Performance Improvements
1.  **Structured Generation**: No more regex parsing. Claude returns valid JSON.
2.  **QA Pipeline**: Automated checks (Link validity, Heading structure) before "Draft" -> "NeedsReview".
3.  **Caching**: `lru_cache` for Airtable configs; Short TTL cache for public post lists.
4.  **Security**: HTML Sanitization of all Markdown output.

## 6. Implementation & Deployment
(See `implementation_plan.md` for execution steps)

## 3. Deployment Strategy

### 3.1 Infrastructure
*   **Platform**: Railway (Recommended) or Render/Heroku.
*   **Service**: Single Service (Dokerized Python App).
*   **Storage**: Ephemeral file system (Templates/Static assets); Persistence in Airtable.

### 3.2 Deployment Pipeline
1.  **Build**: Docker build installs dependencies.
2.  **Environment**: Inject `ANTHROPIC_API_KEY`, `AIRTABLE_API_KEY`, `CRON_SECRET`, `SESSION_SECRET`.
3.  **Run**: `uvicorn execution.server:app --host 0.0.0.0 --port $PORT`.

### 3.3 Domain Management
*   **Public Blogs**: CNAME records point to the App's domain. App uses `Host` header to route.
*   **Admin Dashboard**: Accessible via the main App domain (e.g., `app.autoblog.com/admin`).

## 3. Functional Requirements

### 3.1 Content Serving
*   **Home Page**: List partially or fully all "Published" posts, sorted by date.
*   **Post Page**: Display a single post content by slug.
*   **404 Handling**: Gracefully handle unknown domains or missing posts.

### 3.2 Content Generation
*   **Automated Writing**: Generate coherent, formatted (Markdown) blog posts.
*   **Customization**: Support unique "voices" and instructions per blog via System Prompts.
*   **Media**: (Roadmap) Integration for generating or selecting header images.

### 3.3 Operations
*   **Scalability**: Add new blogs via config change without code deployment (mostly).
*   **Reliability**: Background tasks ensure webhooks don't time out during generation.

## 4. Technical Roadmap & Improvements

### 4.1 Short Term (Refinement)
*   [ ] **Robust Parsing**: Improve the parsing of Claude's output (Title vs Body) to be more reliable than simple string splitting.
*   [ ] **Error Handling**: Better fallback if Airtable or Claude APIs are down.
*   [ ] **Logging**: simple print statements -> structured logging.

### 4.2 Medium Term (Features)
*   [ ] **Deep Well / Knowledge Injection**: Fetch relevant rows from a "Knowledge" table in Airtable to ground the AI's writing.
*   [ ] **Image Generation**: Integrate DALL-E or Midjourney API for post thumbnails.
*   [ ] **SEO Optimization**: Auto-generate meta descriptions and keywords.

### 4.3 Long Term (Platform)
*   [ ] **Admin UI**: A simple dashboard to view generation status and force-trigger builds without using CLI/curl.
*   [ ] **RSS Feeds**: Auto-generate RSS for each blog.

# Phase 2: Enterprise Multi-Agency Architecture

## 5. Expanded Data Schema (Airtable)

To support the multi-agency, multi-blog, and multi-author requirements, the data model has been formalized.
See **[AIRTABLE_SCHEMA_V2.md](AIRTABLE_SCHEMA_V2.md)** for the complete field list.

### 5.1 Tables Summary

#### 1. Agencies
Represents the top-level tenant (e.g., a Marketing Agency).
*   **Name** (Single Line Text): Agency Name.
*   **Administrator** (User): The Airtable user managing this agency.
*   **Blogs** (Link -> Blogs): 1-to-Many relationship with Blogs.
*   **Authors** (Link -> Author_Profile): Many-to-Many relationship with Authors (Authors can work for multiple agencies).

#### 2. Blogs (Automation Configurations)
Represents a specific blog deployment.
*   **Name** (Single Line Text): Blog Name (e.g., "Tech Daily").
*   **Domain** (Single Line Text): The domain serving this blog (e.g., `tech.example.com`).
*   **Agency** (Link -> Agencies): The parent Agency.
*   **Knowledge_Base** (Link -> Knowledge): The specific knowledge bank for this blog.
*   **Authors** (Link -> Author_Profile): Authors authorized to write for this blog.
*   **Posts** (Link -> Posts): All posts generated for this blog.

#### 3. Author_Profile
Represents a writer persona or real author.
*   **Name** (Single Line Text): Author Name.
*   **Bio** (Long Text): Public-facing biography.
*   **Writing_Style** (Long Text): Directives for Voice/Tone (e.g., "Witty, professional, uses analogies").
*   **Agencies** (Link -> Agencies): Agencies this author is associated with.
*   **Blogs** (Link -> Blogs): Specific blogs this author writes for.

#### 4. Knowledge
Defines the "Brain" of the blog.
*   **Name** (Single Line Text): Identifier.
*   **Identity**: (Deprecated/Merged into Author_Style).
*   **Core_Subject** (Single Line Text): Primary topic.
*   **Detailed_Instructions** (Long Text): Specific facts, policies, or expertise to include.
*   **Blog** (Link -> Blogs): The blog this knowledge belongs to.

#### 5. Posts
*   **...Existing Fields...**
*   **Blog** (Link -> Blogs): *Critical for filtering in a shared base.*
*   **Author** (Link -> Author_Profile): The writer of this specific post.

---

## 6. Application Logic (The "Coherence Expression")

The content generation engine will need to synthesize a **System Prompt** dynamically at runtime by combining:
1.  **Author Persona**: Taken from `Author_Profile.Writing_Style` & `Author_Profile.Bio`.
2.  **Domain Expertise**: Taken from `Knowledge.Detailed_Instructions` linked to the Blog.
3.  **Blog Context**: Taken from `Blogs.Name` and domain.

`Prompt = [Author Persona] + [Blog Context] + [Domain Expertise]`

This ensures that "Author X" writing on "Blog Y" sounds like Author X but knows about Y's topics.

## 7. Management Interface (Web Frontend)

For detailed UI/UX and technical design of the Admin Dashboard, see **[FRONTEND_DESIGN.md](FRONTEND_DESIGN.md)**.

### 7.1 Key Features
*   **Agency Management**: Create and manage agencies.
*   **Blog Configuration**: Manage domains, knowledge base, and author assignments.
*   **Author Studio**: Create and tune author personas (Voice/Style).
*   **Tech Stack**: Server-side rendered HTML (Jinja2) + Vanilla CSS/JS for a lightweight, premium feel.

## 8. Strategic Roadmap (Phase 4)
For a detailed breakdown of future plans (Content Briefs, Voice Profiles, Performance Loops), see **[ROADMAP.md](ROADMAP.md)**.
