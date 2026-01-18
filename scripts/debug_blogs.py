
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from execution.utils import load_blogs_config

print("--- Loading Blogs Config ---")
blogs = load_blogs_config(force=True)
print(f"Total Blogs Found: {len(blogs)}")
for b in blogs:
    print(f"- Name: {b['name']}")
    print(f"  Domain: {b['domain']}")
    print(f"  ID: {b['id']}")
    print(f"  Contract: {b['generation_contract_default']}")
    print("-" * 20)
