from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from config import APP_VERSION, GEMINI_API_KEY
from pipeline.processor import process_documents
from pipeline.stages import STAGES

st.set_page_config(page_title="DocIntel", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    /* =========================================================
       DESIGN TOKENS — LIGHT MODE ONLY
       ========================================================= */
    :root {
        --bg: #f5f7f7;
        --surface: #ffffff;
        --surface-2: #eef2f2;
        --surface-3: #e7ecec;

        --sidebar: #eef2f2;
        --sidebar-surface: #ffffff;

        --text: #17212b;
        --text-secondary: #4a555c;
        --text-muted: #6b777f;

        --border: #dce4e4;
        --border-strong: #c8d3d3;

        --accent: #0e766e;
        --accent-hover: #0a655e;
        --accent-soft: #e2f2ef;

        --success: #18794e;
        --success-soft: #e7f5ee;

        --warning: #a86412;
        --warning-soft: #fff2df;

        --danger: #c23b3b;
        --danger-soft: #fdeaea;

        --info: #3568a8;
        --info-soft: #eaf1fb;

        --verdict-bg: #ffffff;
        --verdict-text: #17212b;
        --verdict-muted: #4a555c;

        --evidence-bg: #f2faf7;
        --evidence-border: #9fd5c4;

        --code-bg: #f1f4f4;

        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 6px 20px rgba(0, 0, 0, 0.06);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* =========================================================
       GLOBAL
       ========================================================= */
    .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
    }

    [data-testid="stMain"] {
        background: var(--bg) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* =========================================================
       SIDEBAR
       ========================================================= */
    [data-testid="stSidebar"] {
        background: var(--sidebar) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {
        color: var(--text-muted) !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"],
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border-color: var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    /* =========================================================
       TYPOGRAPHY
       ========================================================= */
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    p,
    label,
    li,
    span {
        font-family: Manrope, sans-serif;
    }

    h1 {
        color: var(--text) !important;
        letter-spacing: -0.045em;
        font-weight: 800;
    }

    h2,
    h3,
    h4,
    h5,
    h6 {
        color: var(--text) !important;
    }

    p,
    li {
        color: var(--text-secondary);
    }

    .eyebrow {
        color: var(--accent) !important;
        font: 500 11px 'DM Mono', monospace;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .hero {
        padding: 1.25rem 0 .75rem;
    }

    .hero h1 {
        margin-bottom: .4rem;
    }

    .hero p {
        color: var(--text-secondary) !important;
        max-width: 750px;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .small {
        color: var(--text-muted) !important;
        font-size: .87rem;
    }

    /* =========================================================
       CARDS
       ========================================================= */
    .status-card {
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 18px;
        background: var(--surface);
        color: var(--text);
        box-shadow: var(--shadow-sm);
    }

    .metric {
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        padding: 13px 16px;
        background: var(--surface);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        min-height: 90px;
        box-shadow: var(--shadow-sm);
    }

    .metric .value {
        color: var(--text) !important;
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -.05em;
    }

    .metric .label {
        color: var(--text-muted) !important;
        font: 500 11px 'DM Mono', monospace;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    /* =========================================================
       VERDICT
       ========================================================= */
    .verdict {
        padding: 22px;
        border-radius: var(--radius-lg);
        background: var(--verdict-bg);
        color: var(--verdict-text);
        border: 1px solid var(--border-strong);
        box-shadow: var(--shadow-md);
    }

    .verdict h2 {
        margin: 2px 0 8px;
        color: var(--accent) !important;
    }

    .verdict p {
        color: var(--verdict-muted) !important;
    }

    .verdict strong {
        color: var(--text) !important;
    }

    /* =========================================================
       TAGS
       ========================================================= */
    .tag {
        display: inline-block;
        border-radius: 99px;
        padding: 4px 9px;
        margin: 2px 3px 2px 0;
        font: 500 11px 'DM Mono', monospace;
        background: var(--accent-soft);
        color: var(--accent) !important;
        border: 1px solid color-mix(in srgb, var(--accent) 22%, transparent);
    }

    /* =========================================================
       EVIDENCE
       ========================================================= */
    .evidence {
        border-left: 3px solid var(--evidence-border);
        padding: 10px 14px;
        background: var(--evidence-bg);
        color: var(--text-secondary);
        margin: 4px 0 14px;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }

    /* =========================================================
       NATIVE STREAMLIT SURFACES
       ========================================================= */

    /* Expander */
    [data-testid="stExpander"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--text) !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: var(--surface-2) !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: var(--text-secondary) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent) !important;
    }

    /* Select boxes */
    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }

    [data-baseweb="select"] * {
        color: var(--text) !important;
    }

    /* Text inputs */
    input,
    textarea {
        background: var(--surface) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border-color: var(--border) !important;
    }

    [data-testid="stFileUploader"] * {
        color: var(--text-secondary) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        font-family: Manrope, sans-serif !important;
        font-weight: 600 !important;
        transition: all .15s ease;
    }

    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background: var(--accent-soft) !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        color: #ffffff !important;
        border-color: var(--accent) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
        color: #ffffff !important;
    }

    /* =========================================================
       DATAFRAME
       ========================================================= */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] * {
        color: var(--text) !important;
    }

    /* =========================================================
       CODE / JSON
       ========================================================= */
    [data-testid="stCodeBlock"] {
        background: var(--code-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }

    pre,
    code {
        background: var(--code-bg) !important;
        color: var(--text-secondary) !important;
    }

    /* =========================================================
       ALERTS
       ========================================================= */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border) !important;
    }

    /* =========================================================
       DIVIDERS
       ========================================================= */
    hr {
        border-color: var(--border) !important;
        opacity: .8;
    }

    /* =========================================================
       CAPTIONS
       ========================================================= */
    [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric(label: str, value: Any) -> None:
    st.markdown(f'<div class="metric"><div class="value">{value}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)


def display_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def load_result() -> dict[str, Any] | None:
    return st.session_state.get("result")


def render_relationship(item: dict[str, Any], facts: dict[str, dict[str, Any]]) -> None:
    left, right = facts.get(item["fact_a"], {}), facts.get(item["fact_b"], {})
    title = f'{left.get("predicate", "Fact")} · {left.get("time_period") or "period unspecified"}'
    with st.expander(f'{item["relationship_id"]}  ·  {item["classification"]}  ·  {item.get("severity", "INFO")}  ·  {item["confidence"]:.0%}  ·  {title}'):
        st.markdown(f'<span class="tag">{item.get("review_status", "AUTO_RESOLVED")}</span> <span class="tag">{item.get("severity", "INFO")} severity</span>', unsafe_allow_html=True)
        if item.get("flags"):
            st.caption("Flags: " + " · ".join(item["flags"]))
        a, b = st.columns(2)
        for column, fact, heading in ((a, left, "FACT A"), (b, right, "FACT B")):
            with column:
                st.markdown(f"**{heading}**")
                st.write(f'{fact.get("predicate", "claim").replace("_", " ").title()} = {fact.get("value")}')
                st.caption(f'Source: {fact.get("evidence", {}).get("document_id")} · page {fact.get("evidence", {}).get("page")}')
                st.code(fact.get("evidence", {}).get("text", ""), language="text")
        st.markdown("**Decision criteria**")
        criteria = item.get("criteria", [])
        if criteria:
            st.dataframe(pd.DataFrame([
                {"Criterion": criterion.get("label"), "Result": "✓" if criterion.get("passed") else "✗", "Detail": criterion.get("detail")}
                for criterion in criteria
            ]), width="stretch", hide_index=True)
        st.markdown("**Why?**")
        st.info(item.get("reasoning", "No reasoning available."))
        st.markdown(f"**Review:** {'Required — human review recommended' if item.get('review_required') else 'Auto-resolved'}")
        if item.get("validation_errors"):
            st.error("Validation: " + "; ".join(item["validation_errors"]))


def render_overview(result: dict[str, Any]) -> None:
    metadata, verdict = result.get("metadata", {}), result.get("verdict", {})
    st.markdown('<div class="eyebrow">Evidence-grounded knowledge layer</div>', unsafe_allow_html=True)
    st.markdown("<div class='hero'><h1>DocIntel</h1><p>Turn a collection of PDFs into an inspectable map of facts, relationships, and uncertainty. Every conclusion stays anchored to source evidence.</p></div>", unsafe_allow_html=True)
    
    cards = st.columns(5)
    for column, label, value in zip(cards, ("Documents", "Pages", "Facts Extracted", "Canonical Entities", "Relationships Analyzed"), (metadata.get("documents", 0), metadata.get("pages", 0), len(result.get("facts", [])), len(result.get("entities", [])), len(result.get("relationships", [])))):
        with column:
            metric(label, value)
    st.write("")
    st.markdown("**PROCESSING PIPELINE**")
    pipeline = result.get("processing", {}).get("stages", [{"name": stage, "status": "complete"} for stage in STAGES])
    st.markdown(" &nbsp;→&nbsp; ".join(f'<span class="tag">✓ {stage["name"]}</span>' for stage in pipeline), unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.15, 1])
    with left:
        score = verdict.get("consistency_score")
        score_text = f"{score:.0%}" if isinstance(score, (float, int)) else "—"
        st.markdown('<div class="verdict"><div class="eyebrow">Final verdict</div><h2>' + verdict.get("label", "NOT PROCESSED") + f'</h2><p>Knowledge consistency · <strong>{score_text}</strong></p><p>{verdict.get("summary", "")}</p><p>{verdict.get("high_priority", 0)} high-priority issues require review.</p></div>', unsafe_allow_html=True)
    with right:
        counts = verdict.get("counts", {})
        st.markdown("**RELATIONSHIP ANALYSIS**")
        labels = ("CORROBORATED", "CONTRADICTION", "CONTEXTUAL_DIFFERENCE", "PARTIALLY_CORROBORATED", "UNCERTAIN", "UNRELATED")
        st.write("  \n".join(f"**{key.replace('_', ' ').title()}** · {counts.get(key, 0)}" for key in labels) or "No relationships evaluated.")
    st.write("")
    issues = result.get("issues", [])
    st.markdown("**NEEDS ATTENTION**")
    attention = st.columns(4)
    for column, severity, label in zip(attention, ("HIGH", "MEDIUM", "LOW", "INFO"), ("Potential contradictions", "Extraction / entity issues", "Data quality", "Contextual differences")):
        with column:
            metric(label, sum(issue.get("severity") == severity for issue in issues))
    if issues:
        with st.expander("Open attention queue"):
            for issue in issues:
                st.markdown(f'**{issue["issue_id"]} · {issue["severity"]} · {issue["type"]}** — {issue["reason"]}')
    st.markdown("**KEY FINDINGS**")
    findings = verdict.get("key_findings", [])
    finding_columns = st.columns(max(1, min(3, len(findings))))
    for column, finding in zip(finding_columns, findings):
        with column:
            st.markdown(f'<div class="status-card">— {finding}</div>', unsafe_allow_html=True)
    if verdict.get("recommendation"):
        st.caption(verdict["recommendation"])
   
    st.caption("A plain-language synthesis of the structured extraction and relationship analysis. Use Evidence and Flags & Review to verify the cited basis.")
    for paragraph in verdict.get("detailed_finding", []):
        st.markdown(paragraph)
    st.write("")
    coverage, quality = st.columns(2)
    with coverage:
        st.markdown("**EVIDENCE COVERAGE**")
        evidence_coverage = metadata.get("evidence_coverage", 0)
        st.progress(evidence_coverage, text=f"{evidence_coverage:.0%} · {sum(bool(f.get('evidence', {}).get('text')) for f in result.get('facts', []))} / {len(result.get('facts', []))} facts have source evidence")
        st.caption(f'{metadata.get("page_anchors", 0)} facts have page anchors · {len([r for r in result.get("relationships", []) if not r.get("validation_errors")])} validated relationships')
    with quality:
        st.markdown("**DATA QUALITY**")
        high_confidence = metadata.get("high_confidence_facts", 0)
        total_facts = len(result.get("facts", []))
        st.write(f"High-confidence facts · **{high_confidence} / {total_facts}**")
        st.write(f"Missing context · **{metadata.get('missing_context', 0)}**")
        st.write(f"Duplicate facts · **{metadata.get('duplicate_facts', 0)}**")
        st.write(f"Extraction warnings · **{len(result.get('failures', []))}**")
    with st.expander("How DocIntel works"):
        st.write("1. **Extract** — PDFs are parsed locally while preserving page anchors.\n2. **Structure** — Content is mapped into a dynamic JSON knowledge model.\n3. **Normalize** — Numbers, units, dates, and entities are standardized.\n4. **Analyze** — Related facts are identified and semantically evaluated when needed.\n5. **Validate** — Conclusions are checked against source evidence.\n6. **Assess** — DocIntel produces relationship-level and case-level verdicts.")


def app() -> None:
    if "result" not in st.session_state:
        st.session_state.result = None
    with st.sidebar:
        st.markdown('<div class="eyebrow">DOCINTEL  </div>', unsafe_allow_html=True)
        st.markdown("### Process a case")
        uploaded = st.file_uploader("Upload one or more PDFs", type=["pdf"], accept_multiple_files=True)
        st.caption("Files are parsed locally. Page and evidence anchors are retained throughout the pipeline.")
        process = st.button("Process documents", type="primary", width="stretch", disabled=not uploaded)
        st.divider()
        st.markdown("**Reasoning provider**")
        st.write("Gemini 2.5 Flash" if GEMINI_API_KEY else "Local deterministic fallback")
        if not GEMINI_API_KEY:
            st.caption("Add GEMINI_API_KEY to enable semantic extraction and ambiguity resolution. The local pipeline is available now.")
        if st.session_state.result:
            if st.button("Clear current case", width="stretch"):
                st.session_state.result = None
                st.rerun()

    if process and uploaded:
        stage_box = st.empty()
        progress = st.progress(0)
        log_box = st.empty()
        stage_states = ["○ " + stage for stage in STAGES]
        def on_stage(index: int, name: str, payload: dict) -> None:
            stage_states[index] = "✓ " + name
            progress.progress((index + 1) / len(STAGES))
            stage_box.markdown("\n\n".join(stage_states))
        logs: list[str] = []
        def on_log(line: str) -> None:
            logs.append(line)
            log_box.code("\n".join(logs[-8:]), language="text")
        try:
            files = [(item.name, item.getvalue()) for item in uploaded]
            st.session_state.result = process_documents(files, on_stage=on_stage, on_log=on_log).model_dump()
            st.rerun()
        except Exception as exc:
            st.error(f"Processing failed: {exc}")
            st.exception(exc)
        return

    result = load_result()
    if not result:
        render_overview({"metadata": {}, "verdict": {}, "facts": [], "entities": [], "relationships": []})
        st.info("Upload two or more PDFs in the sidebar to compare their factual claims. One PDF is also useful for inspecting extraction and evidence.")
        return

    render_overview(result)
    st.divider()
    facts = {fact["fact_id"]: fact for fact in result.get("facts", [])}
    tabs = st.tabs(["Documents", "Facts", "Entities", "Relationships", "Flags & Review", "Evidence", "Decision Criteria", "Failures", "Raw JSON", "Processing Log"])
    with tabs[0]:
        st.subheader("Source documents")
        st.dataframe(pd.DataFrame([{"Document": doc["filename"], "Pages": doc["page_count"], "ID": doc["document_id"]} for doc in result["documents"]]), width="stretch", hide_index=True)
    with tabs[1]:
        st.subheader("Extracted facts")
        rows = []
        fact_flags = {}
        for relationship in result.get("relationships", []):
            for fact_id in (relationship.get("fact_a"), relationship.get("fact_b")):
                fact_flags.setdefault(fact_id, set()).update(relationship.get("flags", []))
        for fact in result["facts"]:
            flags = sorted(fact_flags.get(fact["fact_id"], set()))
            rows.append({"Fact": fact["fact_id"], "Entity": display_value(fact.get("attributes", {}).get("entity_name", fact["subject"])), "Predicate": fact["predicate"].replace("_", " "), "Value": display_value(fact.get("value")), "Period": display_value(fact.get("time_period")), "Source page": fact["evidence"]["page"], "Confidence": f'{fact["confidence"]:.0%}', "Status": "Flagged" if flags else "Verified", "Flags": ", ".join(flags) or "—"})
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.caption("Facts retain dynamic predicates; the system does not require a fixed financial schema.")
    with tabs[2]:
        st.subheader("Resolved entities")
        st.dataframe(pd.DataFrame(result.get("entities", [])), width="stretch", hide_index=True)
    with tabs[3]:
        st.subheader("Cross-document relationships")
        if result["relationships"]:
            for item in result["relationships"]:
                render_relationship(item, facts)
        else:
            st.info("No cross-document candidate pairs were found.")
    with tabs[4]:
        st.subheader("Flags & review queue")
        if result.get("issues"):
            severity = st.selectbox("Severity", ["All", "HIGH", "MEDIUM", "LOW", "INFO"])
            filtered = result["issues"] if severity == "All" else [issue for issue in result["issues"] if issue.get("severity") == severity]
            st.dataframe(pd.DataFrame([{
                "ID": issue.get("issue_id"),
                "Severity": issue.get("severity"),
                "Flag": issue.get("type"),
                "Title": issue.get("title"),
                "Confidence": f'{issue["confidence"]:.0%}' if isinstance(issue.get("confidence"), (int, float)) else "—",
                "Status": issue.get("status"),
            } for issue in filtered]), width="stretch", hide_index=True)
            for issue in filtered:
                with st.expander(f'{issue.get("issue_id")} · {issue.get("title")}'):
                    st.write(issue.get("reason"))
        else:
            st.success("No review items were generated.")
        st.markdown("**Detected flag taxonomy**")
        st.write(" · ".join(f'{item["flag"]} ({item["count"]})' for item in result.get("flags", [])) or "No flags detected.")
    with tabs[5]:
        st.subheader("Source evidence")
        evidence = result.get("evidence", [])
        if not evidence:
            st.info("No evidence anchors were generated. Check the Processing Log for extraction details.")
        documents = {document["document_id"]: document for document in result.get("documents", [])}
        document_ids = list(documents)
        selected_document = st.selectbox("Document", document_ids, format_func=lambda value: documents[value]["filename"]) if document_ids else None
        document_evidence = [item for item in evidence if item["document_id"] == selected_document]
        pages = sorted({item["page"] for item in document_evidence})
        selected_page = st.selectbox("Page", pages) if pages else None
        for item in document_evidence:
            if item["page"] == selected_page:
                fact = facts.get(item["fact_id"], {})
                st.markdown(f'**{item["fact_id"]} · {fact.get("predicate", "claim").replace("_", " ").title()}**')
                st.caption(f'Page {item["page"]} · chunk {item["chunk_id"]}')
                st.code(item["text"], language="text")
                related = [relationship["relationship_id"] for relationship in result.get("relationships", []) if item["fact_id"] in (relationship.get("fact_a"), relationship.get("fact_b"))]
                st.caption("Related relationships: " + (", ".join(related) if related else "none"))
    with tabs[6]:
        st.subheader("Decision criteria matrix")
        st.caption("Each row is a deterministic comparison against stored source evidence.")
        if not result["relationships"]:
            st.info("No comparable relationships were generated from the extracted facts.")
        for item in result["relationships"]:
            st.markdown(f"**{item['relationship_id']} → {item['classification']}**")
            st.dataframe(pd.DataFrame([
                {"Criterion": criterion.get("label"), "Result": "✓" if criterion.get("passed") else "✗", "Detail": criterion.get("detail")}
                for criterion in item.get("criteria", [])
            ]), width="stretch", hide_index=True)
    with tabs[7]:
        st.subheader("Extraction and validation failures")
        if result["failures"]:
            st.dataframe(pd.DataFrame(result["failures"]), width="stretch", hide_index=True)
        else:
            st.success("No suspicious extraction patterns were detected.")
    with tabs[8]:
        st.subheader("Master knowledge JSON")
        for label, payload in (("Document JSON", result.get("documents", [])), ("Fact JSON", result.get("facts", [])), ("Analysis JSON", {"relationships": result.get("relationships", []), "verdict": result.get("verdict", {}), "issues": result.get("issues", [])})):
            with st.expander(label):
                st.json(payload)
    with tabs[9]:
        st.subheader("Processing log")
        st.code("\n".join(result.get("logs", [])) or "No processing log available.", language="text")


if __name__ == "__main__":
    app()