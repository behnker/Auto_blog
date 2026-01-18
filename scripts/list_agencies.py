
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

def list_agencies():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        print("Missing credentials")
        return

    api = Api(api_key)
    table = api.table(base_id, "Agencies")
    records = table.all()
    print(f"Found {len(records)} records:")
    for r in records:
        print(f"- {r['fields'].get('Name', 'Unnamed')} ({r['id']})")

if __name__ == "__main__":
    list_agencies()
