```markdown
# DocIntel

### Evidence-Grounded Knowledge Layer for PDFs

DocIntel transforms multiple PDF documents into a structured, evidence-grounded knowledge layer. It extracts factual claims, normalizes values, and analyzes cross-document relationships to determine if facts are **corroborated, contradictory, contextually different, or unrelated**.

Unlike standard document summarizers or black-box PDF chatbots, DocIntel prioritizes traceability—making cross-document facts **inspectable, comparable, and explicitly tied to source evidence**.

---

## Demo

**Dashboard:** ![DocIntel Dashboard](screenshots/docintel-final-overview.jpg)  
**Analysis:** ![DocIntel Analysis](screenshots/docintel-home.jpg)  
**Video:** [Add your 3-minute demo video link here]

---

## Core Capabilities

* **Page-Aware Extraction:** Pulls numerical and semantic claims from PDFs while retaining exact document and page anchors.
* **Dynamic Fact Structuring:** Maps unstructured text into a flexible JSON schema (Subject, Predicate, Value, Unit, Period, Scope).
* **Deterministic Normalization:** Programmatically standardizes numbers (e.g., `25 crore` to `250 million`), units, and dates for accurate comparison.
* **Entity Resolution:** Identifies when differently written names refer to the same canonical entity.
* **Relationship Analysis:** Compares facts across documents to flag contradictions, verify corroborations, and identify contextual differences (e.g., different fiscal years or scopes).
* **Failure & Ambiguity Detection:** Actively surfaces extraction errors, missing context, and unsupported inferences instead of hallucinating.

---

## How It Works

The system follows a strict, traceable pipeline:

`PDF Upload` → `Local Parsing` → `Fact Extraction` → `Normalization` → `Relationship Discovery` → `Semantic Reasoning` → `Evidence Validation` → `Final Verdict`

### LLM vs. Deterministic Processing
DocIntel uses **Gemini 2.5 Flash** *only* for semantic tasks (fact extraction, ambiguity resolution, relationship reasoning). 
It relies on **strict, deterministic Python** for parsing, arithmetic, unit/date normalization, and evidence grounding to ensure accuracy and limit unnecessary API calls.

---

## Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/dhairyagothi/DocIntel.git](https://github.com/dhairyagothi/DocIntel.git)
cd DocIntel

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Configure Environment**
Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

```

**4. Run the application**

```bash
streamlit run app.py

```

---

## Testing

Run the local test suite to validate extraction, normalization, and relationship logic:

```bash
pytest

```

---

## Project Structure (Highlights)

* `/extraction/` - Gemini-powered semantic parsing and JSON mapping
* `/normalization/` - Deterministic standardizers for dates, entities, and numbers
* `/matching/` & `/reasoning/` - Cross-document relationship logic
* `/pipeline/` - Core orchestrator
* `app.py` - Streamlit dashboard UI

---

## Key Design Principles

1. **Evidence First:** Every claim must point to a specific document, page, and raw text chunk.
2. **Context Matters:** Not every difference is a contradiction; fiscal periods and scopes are explicitly tracked.
3. **Transparent Failures:** If the system is uncertain or data is missing, it explicitly flags it for human review.

```

```