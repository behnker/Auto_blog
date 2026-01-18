
import os
import sys
from collections import defaultdict
from pyairtable import Api
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

TABLES = ["Agencies", "Blogs", "Posts", "Voice_Profiles", "Author_Profiles"]

def analyze_usage():
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    
    if not api_key or not base_id:
        print("Error: Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID")
        return

    api = Api(api_key)
    
    print(f"Analyzing Base: {base_id}")
    print("="*40)

    for table_name in TABLES:
        print(f"\nTable: {table_name}")
        try:
            table = api.table(base_id, table_name)
            records = table.all()
            total_records = len(records)
            
            if total_records == 0:
                print("  [Reference] Table is empty.")
                continue

            field_counts = defaultdict(int)
            all_fields = set()

            # First pass: collect all possible fields from all records
            # (Airtable only returns fields that have values)
            for r in records:
                fields = r["fields"]
                for k in fields.keys():
                    all_fields.add(k)
            
            # Second pass: count non-empty
            for r in records:
                fields = r["fields"]
                for k in all_fields:
                    if k in fields and fields[k]: # Check if truthy (not None, not empty string/list)
                        field_counts[k] += 1
            
            # Report to file
            with open("scripts/airtable_report.txt", "a", encoding="utf-8") as f:
                f.write(f"\nTable: {table_name}\n")
                f.write(f"  Total Records: {total_records}\n")
                f.write(f"  Field Usage Stats:\n")
                
                sorted_fields = sorted(all_fields)
                low_usage = []
                
                for field in sorted_fields:
                    count = field_counts[field]
                    percent = (count / total_records) * 100
                    f.write(f"    - {field:<30} : {count:>3}/{total_records:<3} ({percent:>5.1f}%)\n")
                    
                    if percent < 10:
                        low_usage.append(field)

                if low_usage:
                    f.write(f"\n  ⚠️  Low Usage (<10%) Candidates for Removal:\n")
                    for field in low_usage:
                        f.write(f"      - {field}\n")

        except Exception as e:
            with open("scripts/airtable_report.txt", "a", encoding="utf-8") as f:
                f.write(f"  Error accessing table {table_name}: {e}\n")

if __name__ == "__main__":
    # Clear file
    with open("scripts/airtable_report.txt", "w", encoding="utf-8") as f:
        f.write("Airtable Analysis Report\n========================\n")
    analyze_usage()
