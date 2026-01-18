
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

def fix_blog_base_ids():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    
    if not api_key or not base_id:
        print("Error: Env vars missing.")
        return

    print(f"Target Base ID: {base_id}")
    api = Api(api_key)
    blogs_table = api.table(base_id, "Blogs")
    
    # Fetch all blogs
    all_blogs = blogs_table.all()
    print(f"Found {len(all_blogs)} blogs.")
    
    for blog in all_blogs:
        current_base = blog["fields"].get("Airtable_Base_ID")
        name = blog["fields"].get("Name")
        
        # If blank or placeholder, update it
        if current_base == "appPlaceholderBaseID" or not current_base:
            print(f"Updating '{name}' Base ID (was '{current_base}')...")
            blogs_table.update(blog["id"], {"Airtable_Base_ID": base_id})
        else:
            print(f"Skipping '{name}' (Base ID '{current_base}' seems ok or specific).")
            # Actually, for this Single-Tenant User, we probably want ALL to point to the current base.
            # But let's only fix the broken ones for now.

if __name__ == "__main__":
    fix_blog_base_ids()
