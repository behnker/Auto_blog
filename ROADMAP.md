# Auto_Blog Strategic Roadmap

This document outlines the strategic direction for Auto_Blog, focusing on high-leverage features inspired by industry leaders (Jasper, Surfer, Contentful).

## 🚀 Phase 4: The Agency Workbench (Planned)

### 1. Brand Voice & Authenticity
*   **Voice Profiles**:
    *   **Concept**: Upload samples/URLs -> Generate "Voice Profile".
    *   **Application**: Assign unique voices per Author/ICP (e.g., "Enterprise Tone" vs "SMB Tone").
*   **Authenticity Slots**:
    *   **Feature**: Structure the prompt to explicitly ask for "Human Value".
    *   **Mechanism**: A UI step *before* generation asking: "Add a quote", "Add a contrarian take", "Add a case study". The AI injects these into the draft.

### 2. The "Content Brief" Object
Moving beyond "Prompt -> Post".
*   **Workflow**: `Research` -> `Brief Generation` -> `Human Approval` -> `Drafting`.
*   **Artifact**: Store a `Brief` object in Airtable containing:
    *   Target Entities & Keywords.
    *   Angle/Hook ("Information Gain").
    *   Required Section Headings.
    *   Competitor Weaknesses to exploit.

### 3. Advanced Workflow & Review
*   **Review Tasks**: Granular checkboxes for the human editor (e.g., "Check Compliance", "Verify Links").
*   **Actionable QA Panel**:
    *   Turn the v2.0 Score into a "Fix-it" list.
    *   **One-Click Fix**: "Add missing entities" button triggers a targeted redraft of specific sections.
*   **Scheduled Revisions**: "Approve this change to go live next Tuesday."

### 4. Performance Loops (Traffic & Refresh)
*   **Refresh Queue**:
    *   Auto-flag posts >6 months old or with dropping traffic.
    *   **"AI Answer Gap"**: Identify if our post is missing from Perplexity/SearchGPT answers for its target keywords.
*   **Topic Cluster Planner**: Identify gaps in the blog's topical authority.

## 🌍 Phase 5: Global Expansion (ML-1 to ML-3)
*   **ML-1: Infrastructure**:
    *   **Configuration**: Blogs define `SupportedLanguages` (e.g., "en, es, fr").
    *   **Inheritance**: Posts inherit this list, triggering automated translation/transcreation jobs.
*   **ML-2: Localization Workflow**:
    *   **Editor Assignments**: `Blog_Language_Editors` mapping (Language -> Editor).
    *   **Queues**: Specialized "Spanish Queue" or "French Queue" for editors.
*   **ML-3: Transcreation**:
    *   Adapting "Voice Profiles" to target cultural idioms (Authenticity Localization).

## 🏭 Phase 6: The Production Factory (UI/UX v1.2)
*   **UX-1: Operational Core**:
    *   **Persistent Scope Bar**: Global switcher for Agency / Blog / Language / Status.
    *   **Work Queue**: Kanban-style status board (Tiles instead of Tables).
    *   **Authenticity Panel**: Explicit inputs for Quote / Opinion / Proof (0/3 → 3/3 Badge).
    *   **Roles & Policy**: Admin/Owner/Editor/Writer roles + Blog Approval Policies (A/B/C).
*   **UX-2: Scale & Batching**:
    *   **Batch Operations**: Bulk Approve, Bulk Publish, Bulk Assign.
    *   **Saved Views**: "My Drafts", "Needs Authenticity", "High Stale Score".

## 🛠 Technical Enablers

*   **Deep Research Agent**: Integration with `Tavily` or `Serper` to fetch live competitor data for the Brief.
*   **Vector Database**: (Pgvector/Pinecone) to store "Knowledge Memories" and "Voice Samples" for retrieval.
*   **Visual Editor**: A "Block-based" editor in the Admin Dashboard to allow manual tweaks to the JSON structure (FAQ, Tables).

---
*Created: Jan 2026*
