
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load Env
load_dotenv()

def debug_create():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")

    print(f"DEBUG: API Key present? {bool(api_key)}")
    print(f"DEBUG: Base ID: {base_id}")

    if not api_key or not base_id:
        print("ERROR: Missing Credentials")
        return

    api = Api(api_key)
    table = api.table(base_id, "Agencies")

    print("Attempting to create record in 'Agencies'...")
    try:
        fields = {"Name": "Debug Agency Creation"}
        record = table.create(fields, typecast=True)
        print(f"SUCCESS: Created record {record['id']}")
        print(f"Fields: {record['fields']}")
        
        # Cleanup
        print("Cleaning up (deleting record)...")
        table.delete(record['id'])
        print("Cleanup successful.")
        
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_create()
