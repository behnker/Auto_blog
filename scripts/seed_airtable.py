import os
import json
import time
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

if not AIRTABLE_API_KEY or not BASE_ID:
    print("Error: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not found in environment.")
    exit(1)

api = Api(AIRTABLE_API_KEY)

def load_data():
    with open("scripts/mock_data.json", "r") as f:
        return json.load(f)

def get_or_create(table_name, search_field, search_value, fields):
    table = api.table(BASE_ID, table_name)
    # Check if exists
    formula = f"{{{search_field}}}='{search_value}'"
    existing = table.all(formula=formula)
    
    if existing:
        print(f"[{table_name}] Found existing '{search_value}'")
        return existing[0]["id"]
    else:
        print(f"[{table_name}] Creating '{search_value}'...")
        record = table.create(fields, typecast=True)
        return record["id"]

def seed():
    data = load_data()
    
    # 1. Agencies
    agency_map = {} # Name -> ID
    for agency in data["Agencies"]:
        # Sanitize: Remove read-only computed fields
        agency.pop("Date Created", None)
        
        aid = get_or_create("Agencies", "Name", agency["Name"], agency)
        agency_map[agency["Name"]] = aid
        
    # 2. Blogs
    blog_map = {} # Name -> ID
    blog_authors_map = {} # BlogName -> [AuthorName]
    for blog in data["Blogs"]:
        # Resolve Agency Link
        agency_names = blog.pop("Agency", [])
        blog["Agency"] = [agency_map[n] for n in agency_names if n in agency_map]
        
        # Capture authors for later linking
        author_names = blog.pop("Authors", [])
        blog_authors_map[blog["Name"]] = author_names
        
        bid = get_or_create("Blogs", "Name", blog["Name"], blog)
        blog_map[blog["Name"]] = bid
        
    # 3. Voice Profiles
    voice_map = {}
    for voice in data["Voice_Profiles"]:
        vid = get_or_create("Voice_Profiles", "Name", voice["Name"], voice)
        voice_map[voice["Name"]] = vid
        
    # 4. Author Profiles
    author_map = {}
    for author in data["Author_Profile"]:
        # Links
        voice_names = author.pop("Voice_Profile", [])
        author["Voice_Profile"] = [voice_map[n] for n in voice_names if n in voice_map]
        
        agency_names = author.pop("Agencies", [])
        author["Agencies"] = [agency_map[n] for n in agency_names if n in agency_map]
        
        # Sanitize computed
        author.pop("Number_of_Posts", None)
        author.pop("Date Created", None)
        
        aid = get_or_create("Author_Profile", "Author_Name", author["Author_Name"], author)
        author_map[author["Author_Name"]] = aid

    # 4b. Update Blogs with Authors (Now that Authors exist)
    print("Linking Authors to Blogs...")
    for blog_name, author_names in blog_authors_map.items():
        if blog_name in blog_map and author_names:
            blog_id = blog_map[blog_name]
            linked_author_ids = [author_map[n] for n in author_names if n in author_map]
            if linked_author_ids:
                api.table(BASE_ID, "Blogs").update(blog_id, {"Authors": linked_author_ids}, typecast=True)

    # 5. Knowledge
    for know in data["Knowledge"]:
         # Links
        blog_names = know.pop("Blog", [])
        know["Blog"] = [blog_map[n] for n in blog_names if n in blog_map]
        
        # Agency is a Lookup (Read Only)
        know.pop("Agency", None)
        
        get_or_create("Knowledge", "Name", know["Name"], know)

    # 6. Posts
    for post in data["Posts"]:
         # Links
        blog_names = post.pop("Blog", [])
        post["Blog"] = [blog_map[n] for n in blog_names if n in blog_map]
        
        # Remove Read-Only Lookups/Formulas
        post.pop("Agency", None)
        post.pop("PrimaryObjective", None) # Lookup
        post.pop("PrimaryObjective_Text", None) # Formula
        
        author_names = post.pop("Author", [])
        post["Author_Profile"] = [author_map[n] for n in author_names if n in author_map] # Schema name is Author_Profile
        # post["Author"] came from mock data but schema likely "Author_Profile"
        
        voice_names = post.pop("Voice_Profile_Override", [])
        post["Voice_Profile_Override"] = [voice_map[n] for n in voice_names if n in voice_map]

        get_or_create("Posts", "Title", post["Title"], post)

    print("Seeding Complete!")

if __name__ == "__main__":
    seed()
