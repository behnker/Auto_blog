import os
import yaml
from typing import Optional, Dict, Any
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "blogs.yaml")

def load_blogs_config() -> list[Dict[str, Any]]:
    """Loads the blogs.yaml configuration file."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f)
        return data.get("blogs", [])

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
    """Resolves the Base ID from the blog config (checking env vars)."""
    env_var_name = blog_config["airtable"]["base_id_env"]
    base_id = os.environ.get(env_var_name)
    if not base_id:
        raise ValueError(f"Base ID not found in env var: {env_var_name}")
    return base_id
