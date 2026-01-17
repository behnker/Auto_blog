# AI_Blog Base Schema Description
*Confirmed as of January 17, 2026 (Updated for Phase 4)*

This document serves as the "Source of Truth" for the Airtable Schema (covering Phases 1-4).

## Table 1: Posts
**Purpose**: Stores all blog content, publishing metadata, QA scores, and structured SEO/AI data.

### Core Content
*   **Name** (Single line text): `Primary identifier`
*   **Title** (Single line text): `Blog post headline`
*   **Content** (Long text): `Main body of the post`
*   **Notes** (Long text): `Internal notes`
*   **Slug** (Single line text): `URL-friendly identifier`
*   **Attachments** (Attachment): `Associated files`
*   **Attachment Summary** (AI text): `AI-generated file summary`

### Publishing & Assignment
*   **Status** (Single select): `Draft`, `Published`, `NeedsReview`
*   **Assignee** (User): `Responsible team member`
*   **PublishedDate** (Date): `Publication timestamp`
*   **Author_Profile** (Linked record): `Links to Author_Profile table`
*   **Voice_Profile_Override** (Linked record): `Specific voice for this post` [Phase 4]

### Contract & QA Fields
*   **GenerationContractDefault** (Single select): `v1.1`, `v2.0`
*   **ContractVersion** (Single line text): `Specific contract version used`
*   **QA_Score_GEO_AEO** (Number - Integer): `Quality score for GEO/AEO optimization`
*   **QA_Report_JSON** (Long text): `Full QA report in JSON format`
*   **GeneratorInput_JSON** (Long text): `Input parameters for content generator`
*   **GeneratorOutput_JSON** (Long text): `Raw output from content generator`

### Phase 4: Research & Briefs
*   **Brief_Status** (Single select): `Pending`, `Generated`, `Approved`
*   **Brief_Data_JSON** (Long text): `The generated brief content`
*   **Brief_Feedback** (Long text): `User feedback on the brief`

### v2.0 Content & SEO Storage (JSON Buffers)
*   **TLDR** (Long text): `Short summary/abstract`
*   **FAQ_JSON** (Long text): `Structured FAQ data`
*   **HowTo_JSON** (Long text): `Step-by-step instructions`
*   **Tables_JSON** (Long text): `Structured table data`
*   **Glossary_JSON** (Long text): `Term definitions`
*   **Entities_JSON** (Long text): `Named entities for SEO`
*   **Schema_JSONLD** (Long text): `JSON-LD schema markup`
*   **LLM_SnippetPack_JSON** (Long text): `AI-optimized content snippets`
*   **Citations_JSON** (Long text): `Source references`

### Metadata & Flags
*   **CitationsEnabled** (Checkbox): `Toggle for citation display`
*   **MetaTitle** (Single line text): `SEO meta title`
*   **Tags** (Long text): `Content categorization`

## Table 2: Knowledge (Writing Profile)
**Purpose**: Defines the AI writing persona.

*   **Name** (Single line text)
*   **Identity** (Single line text)
*   **Core Subject** (Single line text)
*   **Writing Style** (Single line text)
*   **Notes** (Long text)
*   **Example Excerpt** (Long text)
*   **Profile Summary** (AI text)

## Table 3: Author_Profile
**Purpose**: Manages author biographical information.

*   **Author_Name** (Single line text)
*   **Author_Bio** (Long text)
*   **Writing_Style** (Long text) [Deprecated in Phase 4]
*   **Voice_Profile** (Linked record): `Default voice for this author` [Phase 4]
*   **Publication_Name** (Single line text)
*   **Number_of_Posts** (Count)
*   **Posts** (Linked record)

## Table 4: Voice_Profiles [NEW Phase 4]
**Purpose**: Reusable tone and style configurations.

*   **Name** (Single line text): `e.g. Professional, Witty`
*   **Description** (Long text): `Internal description`
*   **Tone_Instructions** (Long text): `Specific adjectives and tonal guides`
*   **Style_Guide** (Long text): `Do's and Don'ts`
*   **Sample_Text** (Long text): `Excerpt for few-shot prompting`
*   **Authors** (Linked record): `Authors using this voice`
*   **Posts** (Linked record): `Posts using this voice`

## Table 5: Agencies [New Phase 4]
**Purpose**: Multi-tenant management.

*   **Name** (Single line text)
*   **Website** (URL): `Agency homepage` [Added Phase 4]
*   **Notes** (Long text)
*   **Blogs** (Linked Record -> Blogs [Phase 5 Config])
