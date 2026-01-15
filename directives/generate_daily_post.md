# SOP: Generate Daily Post

**Goal**: Create a new blog post for the specified blog.

## Inputs
- `blog_id`: The ID of the blog (from `config/blogs.yaml`).
- `Knowledge`: (Optional) Relevant expertise from Airtable 'Knowledge' table.

## Steps
1.  **Select Topic**:
    - If `Knowledge` is provided, pick a topic related to that expertise.
    - Otherwise, select a random "Standard" topic related to the blog niche.
2.  **Generate Content**:
    - Use Claude to write the post.
    - **Tone**: Professional, insightful, personal (use "I" if Knowledge is present).
    - **Structure**: Title, Introduction, Body (H2s), Conclusion, Affiliate Recommendation.
3.  **Publish**:
    - Save to Airtable with Status="Draft" (for review) or "Published" (if fully confident).

## Edge Cases
- If Claude API fails, retry once then log error.
- If Airtable fails, save content to `.tmp/failed_post.md`.
