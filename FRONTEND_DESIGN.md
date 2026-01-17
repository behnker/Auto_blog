# Auto_Blog Management Interface - Frontend Design

## 1. Overview
The Management Interface is a web-based dashboard allowing administrators to manage Agencies, Blogs, Authors, and Knowledge Bases. It serves as the control plane for the Multi-Tenant Auto_Blog platform.

## 2. Technology Stack
*   **Backend**: FastAPI (Existing `server.py`).
*   **Rendering**: Server-Side Rendering (SSR) with **Jinja2** templates.
*   **Styling**: **Vanilla CSS** with CSS Variables for theming.
    *   *Aesthetics*: Modern, Premium, Glassmorphism elements, Dark Mode default.
*   **Interactivity**: **Vanilla JavaScript** (ES6+).
    *   Uses `fetch` API for async CRUD operations (e.g., saving settings without reload).

## 3. Site Map & Navigation

### 3.1 Global Navigation
*   **Sidebar/Top Bar**:
    *   Dashboard (Home)
    *   Agencies
    *   Authors (Author Studio)
    *   Settings

### 3.2 Pages

#### **A. Agency Dashboard (`/admin/agencies`)**
*   **View**: Grid of cards representing Agencies.
*   **Actions**:
    *   "Create New Agency" (Modal).
    *   Click Card -> Drill down to Agency Detail.

#### **B. Agency Detail / Blog Manager (`/admin/agencies/{id}`)**
*   **Header**: Agency stats (Total Blogs, Authors).
*   **Section 1: Blogs**:
    *   List of Blogs.
    *   "Add Blog" button.
    *   **Blog Card**: Shows Domain, Status, Last Post Date.
    *   **Config Config**: Edit Airtable Base ID, Domain.
*   **Section 2: Authors**:
    *   List of Authors assigned to this Agency.
    *   "Assign Author" (Search & Select).

#### **C. Blog Workspace (`/admin/blogs/{id}`)**
This is where the detailed configuration happens.
*   **Tab 1: Configuration**: Domain, Airtable settings.
*   **Tab 2: Knowledge Base**:
    *   Rich Text Editor (or plain text with markdown highlighting) for "Deep Knowledge".
    *   Fields: "Core Subject", "Detailed Instructions".
*   **Tab 3: Author Assignment**:
    *   Toggle Authors available for this blog.

#### **D. Author Studio (`/admin/authors`)**
Central library of all Author Personas.
*   **View**: List/Grid of Authors with avatars/icons.
*   **Edit View (`/admin/authors/{id}`)**:
    *   **Profile**: Name, Bio.
    *   **Voice Engine**:
        *   "Writing Style" (Text Area): e.g., "Sarcastic, witty, uses 90s references."
        *   "Example Excerpt" (Text Area): Sample text for few-shot prompting.
    *   **Assignments**: Multi-select Agencies/Blogs.

## 4. UI/UX Design System

### 4.1 Design Philosophy ("Premium & Dynamic")
*   **Color Palette**: Deep Indigo/Violet backgrounds (Dark Mode), Neon accents (Cyan/Pink) for active states.
*   **Components**:
    *   **Cards**: Translucent backgrounds (`backdrop-filter: blur`), subtle borders, hover lift effects.
    *   **Typography**: Inter or Roboto (Google Fonts). Clean, legible hierarchy.
    *   **Input Fields**: Minimalist, floating labels, smooth focus transitions.

### 4.2 Application Logic (Frontend)
*   **State Management**: Minimal client state; rely on server HTML.
*   **Notifications**: Toast messages for success/error (e.g., "Knowledge Base Saved").

## 5. API Endpoints (Internal)
Consumed by the frontend AJAX calls.
*   `POST /api/admin/agencies`
*   `PATCH /api/admin/blogs/{id}/knowledge`
*   `POST /api/admin/authors`
*   `POST /api/admin/authors/{id}/assign`

## 6. Implementation Plan (Frontend)
1.  Create `static/css/admin.css` (Theming & Layout).
2.  Create `templates/admin/base.html` (Layout wrapper).
3.  Implement Views iteratively: Dashboard -> Authors -> Blogs.
