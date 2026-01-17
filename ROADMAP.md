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

## 🛠 Technical Enablers

*   **Deep Research Agent**: Integration with `Tavily` or `Serper` to fetch live competitor data for the Brief.
*   **Vector Database**: (Pgvector/Pinecone) to store "Knowledge Memories" and "Voice Samples" for retrieval.
*   **Visual Editor**: A "Block-based" editor in the Admin Dashboard to allow manual tweaks to the JSON structure (FAQ, Tables).

---
*Created: Jan 2026*
