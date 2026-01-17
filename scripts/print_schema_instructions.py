from execution.models import ObjectiveEnum, MetricEnum, IntentEnum, StatusEnum

def print_enums(name, enum_cls):
    print(f"\n--- {name} Options ---")
    for e in enum_cls:
        print(f"- {e.value}")

def main():
    print("=== Auto_Blog Consolidated Airtable Schema Instructions (Phases 1-4) ===")
    print("Please ensure your Airtable Base has the following Tables and Fields.\n")

    print_enums("ObjectiveEnum (Tables: Blogs.PrimaryObjective, Posts.SecondaryObjective)", ObjectiveEnum)
    print_enums("MetricEnum (Table: Blogs.DefaultMetricFocus)", MetricEnum)
    print_enums("IntentEnum (Table: Blogs.DefaultIntent)", IntentEnum)
    print_enums("StatusEnum (Table: Posts.Status)", StatusEnum)

    print("\n\n=== TABLE 1: Agencies ===")
    print("[ ] Name (Single Line Text)")
    print("[ ] Administrator (User)")
    
    print("\n\n=== TABLE 2: Blogs ===")
    print("[ ] Name (Single Line Text)")
    print("[ ] Domain (Single Line Text)")
    print("[ ] Agency (Link to Agencies)")
    print("[ ] PrimaryObjective (Single Select -> See ObjectiveEnum)")
    print("[ ] DefaultMetricFocus (Single Select -> See MetricEnum)")
    print("[ ] DefaultIntent (Single Select -> See IntentEnum)")
    print("[ ] GenerationContractDefault (Single Select: 'v1.1', 'v2.0')")
    
    print("\n\n=== TABLE 3: Author_Profile ===")
    print("[ ] Name (Single Line Text)")
    print("[ ] Bio (Long Text)")
    print("[ ] Writing_Style (Long Text) - [DEPRECATED in Phase 4, use Voice_Profile]")
    print("[ ] Voice_Profile (Link to Voice_Profiles) [NEW Phase 4]")

    print("\n\n=== TABLE 4: Voice_Profiles [NEW Phase 4] ===")
    print("[ ] Name (Single Line Text) - e.g. 'Professional', 'Witty'")
    print("[ ] Description (Long Text)")
    print("[ ] Tone_Instructions (Long Text) - Specific adjectives and tonal guides")
    print("[ ] Style_Guide (Long Text) - Do's and Don'ts")
    print("[ ] Sample_Text (Long Text) - Excerpt for few-shot prompting")

    print("\n\n=== TABLE 5: Posts ===")
    print("--- Core ---")
    print("[ ] Title (Single Line Text)")
    print("[ ] Slug (Single Line Text)")
    print("[ ] Content (Long Text)")
    print("[ ] Status (Single Select -> See StatusEnum)")
    print("[ ] PublishedDate (Date)")
    print("[ ] Blog (Link to Blogs)")
    print("[ ] Author (Link to Author_Profile)")
    print("[ ] Voice_Profile_Override (Link to Voice_Profiles) [NEW Phase 4]")
    
    print("\n--- Strategy & Objectives ---")
    print("[ ] PrimaryObjective (Lookup from Blog)")
    print("[ ] SecondaryObjective (Single Select)")
    print("[ ] PostIntentNote (Long Text)")

    print("\n--- Phase 4: Research & Briefs ---")
    print("[ ] Brief_Status (Single Select: 'Pending', 'Generated', 'Approved')")
    print("[ ] Brief_Data_JSON (Long Text) - The generated brief content")
    print("[ ] Brief_Feedback (Long Text) - User feedback on the brief")

    print("\n--- Phase 3: SEO & QA (v2.0) ---")
    print("[ ] ContractVersion (Single Line Text)")
    print("[ ] QA_Score_GEO_AEO (Number)")
    print("[ ] QA_Report_JSON (Long Text)")
    print("[ ] GeneratorInput_JSON (Long Text)")
    print("[ ] GeneratorOutput_JSON (Long Text)")
    
    print("\n--- Phase 3: Content Packages (Long Text for JSON) ---")
    print("[ ] TLDR")
    print("[ ] FAQ_JSON")
    print("[ ] HowTo_JSON")
    print("[ ] Tables_JSON")
    print("[ ] Glossary_JSON")
    print("[ ] Entities_JSON")
    print("[ ] Schema_JSONLD")
    print("[ ] LLM_SnippetPack_JSON")
    print("[ ] Citations_JSON")
    
    print("\n--- Phase 3: Metadata ---")
    print("[ ] CitationsEnabled (Checkbox)")
    print("[ ] MetaTitle (Single Line Text)")
    print("[ ] MetaDescription (Single Line Text)")
    print("[ ] CanonicalUrl (Single Line Text)")
    print("[ ] Tags (Multi-Select)")

    print("\n\n=== TABLE 6: Knowledge ===")
    print("[ ] Name (Single Line Text)")
    print("[ ] Core_Subject (Single Line Text)")
    print("[ ] Detailed_Instructions (Long Text)")
    print("[ ] Blog (Link to Blogs)")

if __name__ == "__main__":
    main()
