
import os
import sys
import json
import random
from pyairtable import Api
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load Env
load_dotenv()

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

if not AIRTABLE_API_KEY or not BASE_ID:
    print("Error: Missing API credentials.")
    exit(1)

api = Api(AIRTABLE_API_KEY)

def get_or_create_voice(table, name):
    existing = table.all(formula=f"{{Name}}='{name}'")
    if existing:
        return existing[0]["id"]
    return table.create({
        "Name": name,
        "Description": f"Auto-generated voice for {name}", 
        "Tone_Instructions": "Be professional."
    }, typecast=True)["id"]

def get_or_create_author(table, name, voice_id, agency_id):
    existing = table.all(formula=f"{{Author_Name}}='{name}'")
    if existing:
         # Ensure agency link
        rec = existing[0]
        curr_agencies = rec["fields"].get("Agencies", [])
        if agency_id not in curr_agencies:
             table.update(rec["id"], {"Agencies": curr_agencies + [agency_id]})
        return rec["id"]
        
    return table.create({
        "Author_Name": name, 
        "Author_Bio": "Auto-generated author.",
        "Voice_Profile": [voice_id]
        # "Agencies": [agency_id] # Schema apparently doesn't match mock data
    }, typecast=True)["id"]

def reseed():
    print("Starting Comprehensive Reseed...")
    
    # 1. Fetch Agencies
    agencies_table = api.table(BASE_ID, "Agencies")
    blogs_table = api.table(BASE_ID, "Blogs")
    posts_table = api.table(BASE_ID, "Posts")
    authors_table = api.table(BASE_ID, "Author_Profile")
    voice_table = api.table(BASE_ID, "Voice_Profiles")
    
    agencies = agencies_table.all()
    print(f"Found {len(agencies)} agencies.")
    
    default_voice_id = get_or_create_voice(voice_table, "Neutral Professional")

    for agency in agencies:
        agency_name = agency["fields"].get("Name", "Unnamed Agency")
        agency_id = agency["id"]
        print(f"Processing Agency: {agency_name} ({agency_id})")
        
        # 2. Check for Blogs
        # Note: Airtable relation field might return IDs, but we should search by link or just create one if "Agency Name Blog" doesn't exist.
        # Safer to search for blogs where 'Agency' contains this ID, but formula for linked records is tricky.
        # We'll just list all blogs and filter in python (mock dataset is small).
        all_blogs = blogs_table.all()
        agency_blogs = [b for b in all_blogs if agency_id in b["fields"].get("Agency", [])]
        
        if not agency_blogs:
            print(f"  > No blogs found. Creating 'Blog for {agency_name}'...")
            blog_name = f"{agency_name} Blog"
            # Create Blog
            blog_fields = {
                "Name": blog_name,
                "Domain": f"{agency_name.lower().replace(' ', '')}.com",
                "Agency": [agency_id],
                "Airtable_Base_ID": BASE_ID, # Self-ref for MVP
                "Table_Name": "Posts"
            }
            blog_rec = blogs_table.create(blog_fields, typecast=True)
            agency_blogs.append(blog_rec)
        else:
            print(f"  > Found {len(agency_blogs)} blogs.")

        # 3. Ensure Author
        author_name = f"Editor at {agency_name}"
        author_id = get_or_create_author(authors_table, author_name, default_voice_id, agency_id)

        # 4. Check for Posts in each Blog
        for blog in agency_blogs:
            blog_id = blog["id"]
            blog_name = blog["fields"].get("Name")
            
            # Simple check: does this blog have posts?
            # Again, filtering details.
            all_posts = posts_table.all()
            blog_posts = [p for p in all_posts if blog_id in p["fields"].get("Blog", [])]
            
            if not blog_posts:
                print(f"    > No posts in '{blog_name}'. Seeding 3 posts...")
                titles = [
                    f"Welcome to {agency_name}",
                    f"Why {agency_name} is the Future",
                    f"Top 5 Tips from {agency_name}"
                ]
                for title in titles:
                    posts_table.create({
                        "Title": title,
                        "Blog": [blog_id],
                        # "Agency": [agency_id], # Transitive lookup, cannot write
                        "Author_Profile": [author_id],
                        "Status": random.choice(["Published", "Draft", "InReview"]),
                        "Content": f"This is a seeded post for {title}.",
                        "Voice_Profile_Override": [default_voice_id],
                        "PublishedDate": "2026-01-15"
                    }, typecast=True)
            else:
                 print(f"    > Found {len(blog_posts)} posts in '{blog_name}'.")

    print("Reseed verify complete.")

if __name__ == "__main__":
    reseed()
