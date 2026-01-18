
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

def debug_state():
    print(f"CWD: {os.getcwd()}")
    print("Files in CWD:")
    for f in os.listdir("."):
        if "log" in f or "py" in f:
            print(f" - {f}")
            
    print("\n--- Checking Airtable Agencies ---")
    try:
        api = Api(os.environ.get("AIRTABLE_API_KEY"))
        table = api.table(os.environ.get("AIRTABLE_BASE_ID"), "Agencies")
        records = table.all()
        print(f"Total Records: {len(records)}")
        for r in records:
            print(f" - {r['fields'].get('Name', 'Unnamed')} (ID: {r['id']})")
    except Exception as e:
        print(f"Airtable Error: {e}")

if __name__ == "__main__":
    debug_state()
