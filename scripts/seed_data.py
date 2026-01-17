import os
import json
from datetime import datetime
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

# Config
API_KEY = os.environ.get("AIRTABLE_API_KEY") # User needs to provide this or use PAT
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

if not API_KEY or not BASE_ID:
    print("Error: credentials missing. Ensure AIRTABLE_API_KEY (PAT) and AIRTABLE_BASE_ID are in .env")
    exit(1)

api = Api(API_KEY)

def create_dummy_data():
    print(f"Connecting to Base: {BASE_ID}")
    
    # 1. Author Profile
    print("Creating Authors...")
    t_authors = api.table(BASE_ID, "Author_Profile")
    author_recs = t_authors.batch_create([
        {
            "Author_Name": "Sarah Connor",
            "Author_Bio": "Tech futurist and AI skeptic. Writes about the dangers and promises of AGI.",
            "Publication_Name": "The Resistance Tech",
        },
        {
            "Author_Name": "Neo Anderson",
            "Author_Bio": "Senior Developer advocate. Loves Python, Rust, and breaking out of the simulation.",
            "Publication_Name": "Matrix Code",
        }
    ])
    sarah_id = author_recs[0]['id']
    neo_id = author_recs[1]['id']
    print(f"Created {len(author_recs)} authors.")

    # 2. Knowledge
    print("Creating Knowledge Basing...")
    t_knowledge = api.table(BASE_ID, "Knowledge")
    kn_recs = t_knowledge.batch_create([
        {
            "Name": "Tech Trends 2026",
            "Core_Subject": "AI Agents & Automation",
            "Identity": "TechTrends Bot",
            "Writing_Style": "Professional, Data-Driven, Optimistic",
            "Notes": "Focus on Agentic Workflows, LLM Ops, and Python Integration."
        }
    ])
    kn_id = kn_recs[0]['id'] # We don't link this yet as Blogs table isn't fully active in code, but good to have.
    print(f"Created {len(kn_recs)} knowledge items.")

    # 3. Posts (Various Statuses)
    print("Creating Posts...")
    t_posts = api.table(BASE_ID, "Posts")
    
    # Post 1: Published (v1.1)
    post_published = {
        "Name": "Published Demo 1",
        "Title": "Why Python is eating the world in 2026",
        "Slug": "python-eating-world-2026",
        "Content": "# Python Dominance\n\nPython has become the de-facto language for AI...\n\n## The Rise of Agents\nAgents are everywhere.",
        "Status": "Published",
        "PublishedDate": datetime.now().isoformat(),
        "Author_Profile": [neo_id],
        "ContractVersion": "v1.1",
        "MetaTitle": "Why Python is eating the world in 2026 - Tech Blog",
        "MetaDescription": "An in-depth look at Python's dominance in the AI era."
    }

    # Post 2: Needs Review (v2.0 with Rich Data)
    tldr = ["AI agents are autonomous.", "Python is key.", "Security is a concern."]
    faq = [{"question": "Is AI safe?", "answer": "Mostly, with guardrails."}, {"question": "How to start?", "answer": "Download Python."}]
    
    post_review = {
        "Name": "Review Demo v2",
        "Title": "The Ultimate Guide to AI Agents",
        "Slug": "ultimate-guide-ai-agents",
        "Content": "# Guide to Agents\n\nAgents are the next big thing...\n\n## What are they?\n Autonomous scripts.",
        "Status": "NeedsReview",
        "Author_Profile": [sarah_id],
        "ContractVersion": "v2.0",
        "GenerationContractDefault": "v2.0",
        "QA_Score_GEO_AEO": 85,
        "TLDR": json.dumps(tldr),
        "FAQ_JSON": json.dumps(faq),
        "MetaTitle": "Ultimate Guide to AI Agents (2026)",
        "Tags": ["AI", "Agents", "Tutorial"]
    }

    # Post 3: Draft
    post_draft = {
        "Name": "Draft Idea",
        "Title": "10 Ways to optimize SQL",
        "Slug": "optimize-sql-tips",
        "Content": "To be generated...",
        "Status": "Draft",
        "Author_Profile": [neo_id]
    }

    posts = t_posts.batch_create([post_published, post_review, post_draft])
    print(f"Created {len(posts)} posts.")
    print("Done! Check your Airtable.")

if __name__ == "__main__":
    create_dummy_data()
