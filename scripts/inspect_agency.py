
import os
import sys
from pyairtable import Api
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

def check_agency_fields():
    api = Api(os.environ.get("AIRTABLE_API_KEY"))
    table = api.table(os.environ.get("AIRTABLE_BASE_ID"), "Agencies")
    records = table.all(max_records=1)
    if records:
        print(f"Fields: {records[0]['fields'].keys()}")
        print(f"Blogs Field: {records[0]['fields'].get('Blogs')}")
    else:
        print("No agencies found.")

if __name__ == "__main__":
    check_agency_fields()
