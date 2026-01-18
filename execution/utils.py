import os
import yaml
from typing import Optional, Dict, Any
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "blogs.yaml")

# Caching for Blog Configs
_BLOGS_CACHE = []
_BLOGS_CACHE_TIME = 0

def load_blogs_config(force: bool = False) -> list[Dict[str, Any]]:
    """
    Loads blog configurations from Airtable (Blogs table) with fallback to local yaml.
    Results are cached for 60 seconds to prevent API throttling.
    """
    global _BLOGS_CACHE, _BLOGS_CACHE_TIME
    import time
    
    # Check cache (TTL 60s), skip if force=True
    if not force and _BLOGS_CACHE and (time.time() - _BLOGS_CACHE_TIME < 60):
        return _BLOGS_CACHE
        
    loaded_blogs = []
    
    # 1. Try Airtable
    try:
        api_key = os.environ.get("AIRTABLE_API_KEY")
        master_base = os.environ.get("AIRTABLE_BASE_ID") # Assuming master base holds the 'Blogs' directory
        if api_key and master_base:
            api = Api(api_key)
            table = api.table(master_base, "Blogs")
            records = table.all()
            for r in records:
                f = r["fields"]
                name = f.get("Name", "Unnamed Blog")
                
                # Skip invalid/empty records
                if not name or name == "Unnamed Blog":
                    continue
                    
                loaded_blogs.append({
                    "id": str(r["id"]), # Use Airtable Record ID as app ID
                    "name": name,
                    "domain": f.get("Domain", "localhost"),
                    "airtable": {
                        "base_id_env": "AIRTABLE_BASE_ID", # Hack: Reuse valid Env Var or store ID directly?
                        # Better approach: Store raw ID in Airtable and assume it's valid, 
                        # OR if the existing codebase requires an ENV VAR NAME, we might need a workaround.
                        # For now, let's treat the field 'Airtable_Base_ID' as containing the RAW ID, 
                        # and we'll patch `get_base_id` to handle raw IDs.
                        "base_id_direct": f.get("Airtable_Base_ID"), 
                        "table_name": f.get("Table_Name", "Posts")
                    },
                    "system_prompt_key": f.get("System_Prompt_Key", "DEFAULT_PROMPT"),
                    "affiliate_tag": f.get("Affiliate_Tag", ""),
                    "generation_contract_default": f.get("Generation_Contract", "v2.0")
                })
    except Exception as e:
        print(f"Warning: Failed to load blogs from Airtable: {e}")
        
    # 2. Fallback to YAML if Airtable empty (or failed)
    if not loaded_blogs:
        if os.path.exists(CONFIG_PATH):
             with open(CONFIG_PATH, "r") as f:
                data = yaml.safe_load(f)
                loaded_blogs = data.get("blogs", [])

    _BLOGS_CACHE = loaded_blogs
    _BLOGS_CACHE_TIME = time.time()
    return loaded_blogs

def get_blog_config(blog_id: str) -> Optional[Dict[str, Any]]:
    """Returns the config for a specific blog ID."""
    blogs = load_blogs_config()
    for blog in blogs:
        if blog["id"] == blog_id:
            return blog
    return None

def get_blog_by_domain(domain: str) -> Optional[Dict[str, Any]]:
    """Returns the config for a specific domain."""
    blogs = load_blogs_config()
    for blog in blogs:
        if blog["domain"] == domain:
            return blog
    # Fallback for localhost testing if needed, or handle in server
    return None

def get_airtable_client() -> Api:
    """Returns an authenticated Airtable API client."""
    api_key = os.environ.get("AIRTABLE_API_KEY")
    if not api_key:
        raise ValueError("AIRTABLE_API_KEY not found in environment variables")
    return Api(api_key)

def get_base_id(blog_config: Dict[str, Any]) -> str:
    """Resolves the Base ID. Supports Direct ID (from Airtable) or Env Var Lookup (from YAML)."""
    # 1. Direct ID (New method)
    if "base_id_direct" in blog_config["airtable"] and blog_config["airtable"]["base_id_direct"]:
        return blog_config["airtable"]["base_id_direct"]

    # 2. Env Var Lookup (Legacy method)
    env_var_name = blog_config["airtable"]["base_id_env"]
    base_id = os.environ.get(env_var_name)
    if not base_id:
        raise ValueError(f"Base ID not found in env var: {env_var_name}")
    return base_id

# Agency Caching
_AGENCIES_CACHE = []
_AGENCIES_CACHE_TIME = 0

def get_all_agencies(force: bool = False) -> list[Dict[str, Any]]:
    """
    Loads agencies from Airtable with caching.
    """
    global _AGENCIES_CACHE, _AGENCIES_CACHE_TIME
    import time
    
    if not force and _AGENCIES_CACHE and (time.time() - _AGENCIES_CACHE_TIME < 60):
        return _AGENCIES_CACHE
        
    loaded_agencies = []
    try:
        api_key = os.environ.get("AIRTABLE_API_KEY")
        base_id = os.environ.get("AIRTABLE_BASE_ID")
        
        if api_key and base_id:
            api = Api(api_key)
            table = api.table(base_id, "Agencies")
            records = table.all()
            
            for r in records:
                f = r["fields"]
                name = f.get("Name", "Unnamed")
                # Filter invalid/placeholder agencies
                if not name or name == "Unnamed" or name == "Unnamed Agency Blog":
                    continue
                    
                loaded_agencies.append({
                    "id": r["id"],
                    "name": name,
                    "website": f.get("Website", ""),
                    "status": f.get("Status", "Active"),
                    "blog_ids": f.get("Blogs", []) # Store Linked Blog IDs
                })
    except Exception as e:
        print(f"Warning: Failed to load agencies: {e}")
        
    _AGENCIES_CACHE = loaded_agencies
    _AGENCIES_CACHE_TIME = time.time()
    return loaded_agencies
