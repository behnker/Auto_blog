from execution.models import ObjectiveEnum, MetricEnum, IntentEnum, StatusEnum

def print_enums(name, enum_cls):
    print(f"\n--- {name} Options ---")
    for e in enum_cls:
        print(f"- {e.value}")

def main():
    print("=== Auto_Blog v1.1 Airtable Migration Helper ===")
    print("Please configure your Airtable Base with the following options:\n")

    print_enums("ObjectiveEnum (Tables: Blogs.PrimaryObjective, Posts.SecondaryObjective)", ObjectiveEnum)
    print_enums("MetricEnum (Table: Blogs.DefaultMetricFocus)", MetricEnum)
    print_enums("IntentEnum (Table: Blogs.DefaultIntent)", IntentEnum)
    print_enums("StatusEnum (Table: Posts.Status)", StatusEnum)

    print("\n--- v1.1 Fields ---")
    print("[ ] Table 'Blogs': Add 'PrimaryObjective' (Single Select)")
    print("[ ] Table 'Posts': Add 'PrimaryObjective' (Lookup from Blog)")
    print("[ ] Table 'Posts': Add 'SecondaryObjective' (Single Select)")
    print("[ ] Table 'Posts': Add 'PostIntentNote' (Long Text)")
    print("[ ] Table 'Posts': Add 'MetaDescription' (Text)")
    print("[ ] Table 'Posts': Add 'QA_Result' (JSON/Text)")
    print("[ ] Table 'Posts': Add 'QA_Passed' (Checkbox)")

    print("\n--- v2.0 Fields (Phase 3) ---")
    print("[ ] Table 'Blogs': Add 'GenerationContractDefault' (Single Select: 'v1.1', 'v2.0')")
    print("[ ] Table 'Posts': Add 'ContractVersion' (Single Line Text)")
    print("[ ] Table 'Posts': Add 'QA_Score_GEO_AEO' (Number)")
    print("[ ] Table 'Posts': Add 'QA_Report_JSON' (Long Text)")
    print("[ ] Table 'Posts': Add 'GeneratorInput_JSON' (Long Text)")
    print("[ ] Table 'Posts': Add 'GeneratorOutput_JSON' (Long Text)")
    
    # v2 Content (Long Text for JSON)
    print("\n--- v2.0 Content & SEO Storage (Long Text) ---")
    print("[ ] Table 'Posts': Add 'TLDR'")
    print("[ ] Table 'Posts': Add 'FAQ_JSON'")
    print("[ ] Table 'Posts': Add 'HowTo_JSON'")
    print("[ ] Table 'Posts': Add 'Tables_JSON'")
    print("[ ] Table 'Posts': Add 'Glossary_JSON'")
    print("[ ] Table 'Posts': Add 'Entities_JSON'")
    print("[ ] Table 'Posts': Add 'Schema_JSONLD'")
    print("[ ] Table 'Posts': Add 'LLM_SnippetPack_JSON'")
    print("[ ] Table 'Posts': Add 'Citations_JSON'")
    print("[ ] Table 'Posts': Add 'CitationsEnabled' (Checkbox)")
    print("[ ] Table 'Posts': Add 'MetaTitle' (Single Line Text)")
    print("[ ] Table 'Posts': Add 'Tags' (Multi-Select or Long Text)")

if __name__ == "__main__":
    main()
