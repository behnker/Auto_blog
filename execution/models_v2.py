import json
import re
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# --- v2.0 Data Models ---

class PostContentV2(BaseModel):
    title: str
    slug: str
    markdown_body: str
    tldr: List[str] = Field(description="3-5 bullet points summary")
    faq: List[Dict[str, str]] = Field(description="List of {question, answer} pairs")
    howto: Optional[Dict[str, Any]] = None
    tables: List[Dict[str, Any]] = []
    glossary: List[Dict[str, str]] = Field(description="List of {term, definition}")

class PostMetadataV2(BaseModel):
    meta_title: str
    meta_description: str
    canonical_url: str
    tags: List[str] = []
    entities: List[Dict[str, str]] = Field(description="List of {name, type} entities")
    language: str = "en"

class PostSchemaV2(BaseModel):
    json_ld: List[Dict[str, Any]] = Field(description="List of JSON-LD objects (BlogPosting, FAQPage, etc)")

class PostCitationsV2(BaseModel):
    enabled: bool = False
    references: List[Dict[str, Any]] = []

class PostDistributionV2(BaseModel):
    llm_snippet_pack: Dict[str, Any] = Field(description="{one_paragraph_summary, key_takeaways, recommended_when_asked}")

class PostOutputV2(BaseModel):
    contract_version: str = "2.0"
    content: PostContentV2
    metadata: PostMetadataV2
    schema_data: PostSchemaV2 = Field(alias="schema") # 'schema' is reserved in pydantic v1, aliasing to be safe or just use schema if v2
    citations: PostCitationsV2
    distribution: PostDistributionV2


# --- QA Scoring Logic (0-100) ---

def _contains(haystack: str, needle: str) -> bool:
    return re.search(r"\b" + re.escape(needle) + r"\b", haystack, flags=re.IGNORECASE) is not None

def score_v2_geo_aeo(output: Dict[str, Any], input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes GEO/AEO Readiness Score (0-100) based on the v2.0 Spec Rubric.
    """
    warnings: List[str] = []
    checks: Dict[str, Any] = {}

    # Extract sections (safe access)
    content = output.get("content", {}) or {}
    metadata = output.get("metadata", {}) or {}
    schema = output.get("schema", {}) or {}
    citations = output.get("citations", {}) or {}
    dist = output.get("distribution", {}) or {}

    body = content.get("markdown_body", "") or ""

    # --- A) AEO Answer Packaging (25) ---
    a_points = 0
    tldr = content.get("tldr") or []
    faq = content.get("faq") or []
    tables = content.get("tables") or []

    # TL;DR 3–5 bullets
    if isinstance(tldr, list) and 3 <= len(tldr) <= 5:
        a_points += 5
    else:
        warnings.append("TL;DR should be 3–5 bullets.")

    # FAQ coverage: match questions_to_win count if provided
    questions = ((input_payload.get("search_targets") or {}).get("questions_to_win")) or []
    if isinstance(faq, list) and len(faq) >= max(3, len(questions) or 0):
        a_points += 10
    else:
        warnings.append("FAQ count is low vs questions_to_win (or <3).")

    # H1 + >=3 H2s
    h1 = len(re.findall(r"^#\s+", body, flags=re.MULTILINE))
    h2 = len(re.findall(r"^##\s+", body, flags=re.MULTILINE))
    if h1 >= 1 and h2 >= 3:
        a_points += 5
    else:
        warnings.append("Heading structure weak (need 1 H1 and >=3 H2s).")

    # Comparison table if requested
    comparison_required = (((input_payload.get("content_requirements") or {}).get("structure") or {}).get("comparison_table") is True)
    if comparison_required:
        if isinstance(tables, list) and len(tables) >= 1:
            a_points += 5
        else:
            warnings.append("Comparison table requested but missing.")
    else:
        a_points += 5  # not required → full points

    checks["aeo_answer_packaging"] = {"score": a_points, "tldr_len": len(tldr) if isinstance(tldr, list) else None, "faq_len": len(faq) if isinstance(faq, list) else None, "h1": h1, "h2": h2}

    # --- B) Entity & Semantic Coverage (20) ---
    b_points = 0
    entities = metadata.get("entities") or []
    glossary = content.get("glossary") or []
    key_terms = ((input_payload.get("search_targets") or {}).get("key_terms")) or []

    ent_names = [e.get("name") for e in entities if isinstance(e, dict) and e.get("name")]
    if len(ent_names) >= 3:
        b_points += 5
    else:
        warnings.append("metadata.entities should include >=3 entities.")

    missing_entities = [n for n in ent_names if not _contains(body, n)]
    if not missing_entities:
        b_points += 5
    else:
        warnings.append(f"Some entities not mentioned in body: {missing_entities[:8]}")

    gloss_terms = {g.get("term") for g in glossary if isinstance(g, dict) and g.get("term")}
    if ent_names:
        glossary_ratio = len([n for n in ent_names if n in gloss_terms]) / max(1, len(ent_names))
    else:
        glossary_ratio = 0.0
    if glossary_ratio >= 0.60:
        b_points += 5
    else:
        warnings.append("Glossary coverage < 60% of entities.")

    # Key terms coverage
    if key_terms:
        kt_hit = sum(1 for kt in key_terms if _contains(body, kt))
        kt_ratio = kt_hit / max(1, len(key_terms))
        if kt_ratio >= 0.70:
            b_points += 5
        else:
            warnings.append(f"Key terms coverage low: {kt_hit}/{len(key_terms)}.")
    else:
        b_points += 5  # no terms requested

    checks["entity_coverage"] = {"score": b_points, "entities_count": len(ent_names), "entities_missing_in_body": missing_entities, "glossary_coverage_ratio": round(glossary_ratio, 2)}

    # --- C) Structured Data Completeness (20) — WARN-ONLY ---
    c_points = 0
    json_ld = schema.get("json_ld") or []
    has_blogposting = False
    has_faqpage = False
    has_howto = False
    parse_errors = []

    # Validate JSON-LD items are dicts (already JSON object in output)
    for item in json_ld:
        if isinstance(item, dict):
            t = item.get("@type")
            if t == "BlogPosting":
                has_blogposting = True
            if t == "FAQPage":
                has_faqpage = True
            if t == "HowTo":
                has_howto = True
        else:
            parse_errors.append("json_ld item is not an object")

    if has_blogposting:
        c_points += 8
    else:
        warnings.append("Schema missing BlogPosting (warn-only).")

    if faq:
        if has_faqpage:
            c_points += 6
        else:
            warnings.append("FAQ present but Schema missing FAQPage (warn-only).")
    else:
        c_points += 6

    if content.get("howto"):
        if has_howto:
            c_points += 6
        else:
            warnings.append("HowTo present but Schema missing HowTo (warn-only).")
    else:
        c_points += 6

    checks["schema_completeness"] = {"score": c_points, "has_blogposting": has_blogposting, "has_faqpage": has_faqpage, "has_howto": has_howto, "json_parse_errors": parse_errors}

    # --- D) Trust & Verifiability (15) — toggle-aware ---
    d_points = 0
    cit_enabled = bool(citations.get("enabled", False))
    refs = citations.get("references") or []

    if not cit_enabled:
        d_points = 5
    else:
        if isinstance(refs, list) and len(refs) >= 3:
            d_points += 5
        else:
            warnings.append("Citations enabled but <3 references provided.")

        used_in_ok = 0
        dated_ok = 0
        for r in refs:
            if isinstance(r, dict):
                if r.get("used_in"):
                    used_in_ok += 1
                if r.get("published_date") and r.get("publisher"):
                    dated_ok += 1
        if refs:
            if used_in_ok == len(refs):
                d_points += 3
            else:
                warnings.append("Some citations missing used_in pointers.")
            if dated_ok >= max(1, len(refs) // 2):
                d_points += 2
            else:
                warnings.append("Many citations missing publisher/date.")
        d_points += 5  # baseline trust points when citations enabled

    checks["trust_verifiability"] = {"score": d_points, "citations_enabled": cit_enabled, "references_count": len(refs)}

    # --- E) Metadata & Indexability (10) ---
    e_points = 0
    if metadata.get("meta_title"):
        e_points += 4
    else:
        warnings.append("Missing meta_title.")
    if metadata.get("meta_description"):
        e_points += 4
    else:
        warnings.append("Missing meta_description.")
    if metadata.get("canonical_url"):
        e_points += 1
    else:
        warnings.append("Missing canonical_url.")
    if metadata.get("language"):
        e_points += 1
    else:
        warnings.append("Missing language.")
    checks["metadata"] = {"score": e_points}

    # --- F) LLM Extraction Pack (10) ---
    f_points = 0
    snip = ((dist.get("llm_snippet_pack") or {}) if isinstance(dist.get("llm_snippet_pack"), dict) else {})
    if snip.get("one_paragraph_summary"):
        f_points += 3
    else:
        warnings.append("Snippet pack missing one_paragraph_summary.")
    takeaways = snip.get("key_takeaways") or []
    if isinstance(takeaways, list) and 3 <= len(takeaways) <= 7:
        f_points += 3
    else:
        warnings.append("Snippet pack key_takeaways should be 3–7.")
    rwa = snip.get("recommended_when_asked") or []
    if isinstance(rwa, list) and len(rwa) >= 2:
        f_points += 4
    else:
        warnings.append("Snippet pack recommended_when_asked should include >=2 Q→A pairs.")
    checks["llm_extraction_pack"] = {"score": f_points}

    total = a_points + b_points + c_points + d_points + e_points + f_points

    # question coverage summary
    answered = 0
    if questions and isinstance(faq, list):
        faq_qs = [x.get("question", "") for x in faq if isinstance(x, dict)]
        for q in questions:
            if any(q.strip().lower() in fq.strip().lower() or fq.strip().lower() in q.strip().lower() for fq in faq_qs):
                answered += 1
    checks["question_coverage"] = {"questions_requested": len(questions), "questions_answered": answered}

    report = {
        "qa_version": "1.0",
        "geo_aeo_score": max(0, min(100, total)),
        "warnings": warnings,
        "checks": checks
    }
    return report
