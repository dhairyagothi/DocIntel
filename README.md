
# DocIntel

### Evidence-Grounded Knowledge Layer for PDFs

DocIntel converts multiple PDF documents into a structured, evidence-grounded knowledge layer.

It extracts meaningful factual claims, preserves their source evidence, normalizes values and context, resolves entities, identifies relationships across documents, and produces an explainable final assessment.

Instead of treating every difference as a contradiction, DocIntel considers factors such as **time, scope, units, currency, definitions, entity identity, and historical updates** before classifying relationships.

---

## Overview

DocIntel follows an evidence-first approach:

```text
PDFs
  ↓
PDF Extraction
  ↓
Document Structuring
  ↓
JSON Knowledge Mapping
  ↓
Fact Extraction
  ↓
Entity Resolution
  ↓
Normalization
  ↓
Cross-Document Matching
  ↓
Relationship Reasoning
  ↓
Evidence Validation
  ↓
Final Verdict
````

The result is an inspectable knowledge layer where every important conclusion can be traced back to its source.

---

## Demo

### Dashboard

<img width="1535" height="782" alt="image" src="https://github.com/user-attachments/assets/7449c67c-a088-4541-8012-184f742e698c" />


### Analysis Interface

<img width="1535" height="740" alt="image" src="https://github.com/user-attachments/assets/96217723-fcc2-4176-bf9a-00a37af5d275" />


### Video Demo

[Watch the 3-minute demo](https://youtu.be/gfqqwo5HEoE?si=N5qd6OMqMGCXH9F6)

https://youtu.be/gfqqwo5HEoE?si=N5qd6OMqMGCXH9F6

The demo covers:

* PDF upload and processing
* Page-aware extraction
* JSON knowledge mapping
* Fact extraction
* Entity resolution
* Value and context normalization
* Cross-document relationship discovery
* Corroboration
* Contradiction detection
* Contextual reconciliation
* Failure detection
* Evidence inspection
* Final verdict

---

# Core Capabilities

## 1. Page-Aware PDF Extraction

PDFs are parsed locally using PyMuPDF while retaining document and page-level provenance.

For every extracted section, DocIntel preserves:

* Document ID
* Filename
* Page number
* Chunk ID
* Original source text

This allows extracted facts to remain traceable to their original evidence.

---

## 2. Dynamic Fact Extraction

DocIntel extracts both numerical and semantic facts using a flexible schema.

A fact can contain:

```json
{
  "fact_id": "F001",
  "subject": "Yatra Online",
  "predicate": "revenue",
  "value": 7957.3,
  "unit": "million",
  "currency": "INR",
  "time_period": "FY2025",
  "scope": "company",
  "confidence": 0.96,
  "evidence": {
    "document_id": "DOC001",
    "page": 3,
    "chunk_id": "DOC001-P03-C01",
    "text": "Revenue for FY2025 was INR 7,957.3 million."
  }
}
```

The schema is not limited to predefined categories such as revenue or employees.

New documents can produce predicates such as:

```text
revenue
employee_count
founder
headquarters
acquisition_date
market_share
production_capacity
patent_count
funding
customer_count
growth_rate
```

without changing the core application.

---

## 3. Entity Resolution

DocIntel identifies potentially equivalent entities across documents.

For example:

```text
Yatra Online, Inc.
Yatra Online
Yatra
```

may be resolved to the same canonical entity when sufficient evidence supports the match.

Ambiguous entity matches are flagged rather than blindly merged.

---

## 4. Deterministic Normalization

Before comparing facts, DocIntel programmatically normalizes:

* Numbers
* Units
* Currencies
* Dates
* Fiscal periods
* Entity names
* Duplicate representations

For example:

```text
25 Crore
250 Million
0.25 Billion
```

can be transformed into a common numerical representation before comparison.

Similarly:

```text
FY2025
Fiscal Year 2025
Year ended March 31, 2025
```

are represented with explicit temporal context rather than automatically treated as identical.

---

## 5. Cross-Document Relationship Analysis

DocIntel compares potentially related facts and classifies their relationship.

### Primary classifications

```text
CORROBORATED
CONTRADICTION
CONTEXTUAL_DIFFERENCE
PARTIALLY_CORROBORATED
UNCERTAIN
UNRELATED
```

### Additional flags

Relationships can also carry contextual or quality flags such as:

```text
TIME_DIFFERENCE
FISCAL_PERIOD_DIFFERENCE
QUARTER_DIFFERENCE
HISTORICAL_VS_CURRENT

SCOPE_DIFFERENCE
GEOGRAPHIC_SCOPE
GROUP_VS_SUBSIDIARY
PRODUCT_VS_COMPANY

UNIT_DIFFERENCE
CURRENCY_DIFFERENCE
SCALE_DIFFERENCE
ROUNDING_DIFFERENCE
NUMERIC_VARIANCE
PERCENTAGE_VS_ABSOLUTE

ENTITY_ALIAS
ENTITY_AMBIGUITY
POSSIBLE_ENTITY_MISMATCH

DEFINITION_DIFFERENCE
PREDICATE_AMBIGUITY

MISSING_CONTEXT
LOW_CONFIDENCE
DUPLICATE_FACT
POSSIBLE_EXTRACTION_ERROR
UNSUPPORTED_INFERENCE

UPDATED_INFORMATION
HISTORICAL_INFORMATION
SOURCE_DISAGREEMENT
```

This allows DocIntel to identify issues beyond the minimum assignment cases.

---

# Relationship Reasoning

DocIntel does not classify every numerical difference as a contradiction.

Each candidate relationship is evaluated across several dimensions:

```text
Entity
  ↓
Semantic meaning
  ↓
Value
  ↓
Unit
  ↓
Currency
  ↓
Time period
  ↓
Scope
  ↓
Definition
  ↓
Evidence
  ↓
Context
```

### Example: Corroboration

```text
Fact A:
Revenue = INR 25 Crore
Period = FY2025

Fact B:
Revenue = INR 250 Million
Period = FY2025
```

After normalization:

```text
INR 25 Crore = INR 250 Million
```

Result:

```text
CORROBORATED
```

### Example: Contextual Difference

```text
Fact A:
Revenue = $10M
Period = FY2024

Fact B:
Revenue = $15M
Period = FY2025
```

Result:

```text
CONTEXTUAL_DIFFERENCE

Reason:
Different reporting periods.
```

### Example: Uncertain

When available evidence is insufficient to establish whether two claims agree or conflict:

```text
UNCERTAIN
```

DocIntel prefers an explicit uncertainty classification over an unsupported conclusion.

---

# Evidence Grounding

Every extracted fact and cross-document relationship retains source evidence.

A relationship can be inspected through:

```text
Fact A
   ↓
Source document
   ↓
Page
   ↓
Evidence text

Fact B
   ↓
Source document
   ↓
Page
   ↓
Evidence text
```

The dashboard also shows the criteria used to reach a classification.

Example:

```text
Relationship R042

Classification:
CONTRADICTION

Confidence:
91%

Decision Criteria:

✓ Same entity
✓ Same predicate
✓ Same reporting period
✓ Comparable units
✗ Different values
? Scope requires review

Flags:

NUMERIC_VARIANCE
POSSIBLE_SCOPE_DIFFERENCE

Review:
Human review recommended
```

---

# Failure & Ambiguity Detection

DocIntel explicitly surfaces extraction and reasoning problems instead of hiding them.

Examples include:

* Possible percentage/value confusion
* Missing context
* Invalid evidence references
* Low-confidence extraction
* Duplicate facts
* Unsupported inference
* Entity ambiguity
* Numeric inconsistencies
* Unresolved relationships

Example:

```text
Input:
"Revenue increased by 20% to INR 50 crore."

Potential extraction:
Revenue = 20%

Validation:
A percentage was interpreted as the primary monetary value.

Expected:
Revenue = INR 50 crore
Growth = 20%

Status:
FLAGGED FOR REVIEW
```

---

# Processing Pipeline

The Streamlit interface exposes the internal processing stages:

```text
1. PDF Extraction
2. Document Structuring
3. JSON Mapping
4. Entity Resolution
5. Fact Normalization
6. Relationship Discovery
7. Semantic Reasoning
8. Evidence Validation
9. Final Verdict
```

The dashboard displays the progress, counts, and processing log associated with each stage.

---

# LLM Architecture

## Gemini API

**Model:** Gemini 2.5 Flash

Gemini is used only for tasks that require semantic understanding.

### Gemini is used for

* Semantic fact extraction
* Understanding differently worded claims
* Semantic entity interpretation
* Ambiguity resolution
* Cross-document relationship reasoning
* Concise relationship explanations

### Gemini is not used for

* PDF parsing
* Page tracking
* Arithmetic
* Number normalization
* Unit conversion
* Date normalization
* Database operations
* Evidence validation
* Deterministic matching

This separation reduces unnecessary API usage and keeps critical numerical and provenance operations deterministic.

---

# Token-Efficient Processing

DocIntel does not repeatedly send entire documents to the LLM.

The pipeline follows:

```text
PDF
 ↓
Local extraction
 ↓
Candidate detection
 ↓
Relevant content
 ↓
Gemini fact extraction
 ↓
Structured JSON
 ↓
Deterministic normalization
 ↓
Candidate relationship matching
 ↓
Gemini reasoning only where needed
 ↓
Evidence validation
```

This keeps model usage focused on semantic tasks.

---

# Final Verdict

After processing the document set, DocIntel generates an overall assessment.

Possible verdicts include:

```text
CONSISTENT
MOSTLY CONSISTENT
MIXED / NEEDS REVIEW
SIGNIFICANT CONTRADICTIONS
```

The final assessment includes:

* Documents analyzed
* Pages processed
* Facts extracted
* Entities identified
* Relationships analyzed
* Corroborated relationships
* Contradictions
* Contextual differences
* Partially corroborated relationships
* Uncertain cases
* High-priority issues
* Key findings
* Recommended review actions

## Knowledge Consistency Score

The dashboard may display a Knowledge Consistency Score based on the evaluated relationship classifications.

This is a prototype analytical metric and **not a statistical probability or guarantee of document correctness**.

---

# Required Assignment Cases

DocIntel supports the four required demonstration cases.

## 1. Fact Corroborated Across Documents

Two independently sourced facts represent the same underlying claim, even when expressed differently.

The system shows:

* Both facts
* Source evidence
* Normalized values
* Decision criteria
* Final classification

---

## 2. Genuine or Likely Contradiction

Two sources make incompatible claims about the same entity and semantic property within comparable context.

The system shows:

* Both conflicting claims
* Source evidence
* Comparison criteria
* Reason flags
* Confidence
* Review status

---

## 3. Apparent Contradiction Explained by Context

Differences caused by factors such as:

* Time
* Scope
* Units
* Currency
* Definition
* Historical vs current information

are identified and explained instead of being incorrectly labelled as contradictions.

---

## 4. Extraction or Reasoning Failure

The system surfaces a genuine extraction or reasoning problem and records:

* What was extracted
* Why it is suspicious
* Supporting source text
* Validation result
* Suggested improvement

---

# Generalization

DocIntel is designed to work with previously unseen PDFs.

It does not depend on:

* Hard-coded filenames
* Document-specific rules
* A fixed list of fact types
* Predefined starter-document structures
* Manual relationship definitions for each dataset

The dynamic fact schema and generic relationship engine allow new categories of information to be processed without modifying the core application.

---

# Dataset

The initial demonstration uses three public Yatra Online documents containing overlapping business and financial information across different reporting contexts.

The documents are used only as a demonstration dataset.

The application accepts additional PDFs through the Streamlit interface.

---

# Project Structure

```text
DocIntel/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── database/
│   ├── schema.sql
│   └── store.py
│
├── extraction/
│   ├── __init__.py
│   ├── candidate_detector.py
│   ├── json_mapper.py
│   └── prompts.py
│
├── ingestion/
│   ├── __init__.py
│   ├── chunker.py
│   ├── cleaner.py
│   └── pdf_parser.py
│
├── matching/
│   ├── __init__.py
│   ├── fact_matcher.py
│   └── similarity.py
│
├── models/
│   ├── __init__.py
│   ├── document.py
│   ├── fact.py
│   ├── relationship.py
│   └── result.py
│
├── normalization/
│   ├── __init__.py
│   ├── dates.py
│   ├── entities.py
│   ├── numbers.py
│   └── units.py
│
├── pipeline/
│   ├── __init__.py
│   ├── processor.py
│   └── stages.py
│
├── reasoning/
│   ├── __init__.py
│   ├── gemini_client.py
│   ├── relationship_reasoner.py
│   └── verdict_engine.py
│
├── validation/
│   ├── __init__.py
│   ├── evidence_validator.py
│   ├── failure_detector.py
│   └── result_validator.py
│
├── utils/
│   ├── __init__.py
│   ├── cache.py
│   ├── hashing.py
│   └── logger.py
│
├── tests/
│   ├── __init__.py
│   ├── test_extraction.py
│   ├── test_matching.py
│   ├── test_normalization.py
│   ├── test_validation.py
│   └── test_verdict.py
│
├── screenshots/
│   ├── docintel-home.jpg
│   └── docintel-final-overview.jpg
│
└── data/
    ├── uploads/
    └── processed/
```

---

# Setup & Installation

## 1. Clone the repository

```bash
git clone https://github.com/dhairyagothi/DocIntel.git
cd DocIntel
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure the Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

A template is provided in:

```text
.env.example
```

Never commit your `.env` file or expose your API key.

## 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

# Testing

Run the test suite with:

```bash
pytest
```

The tests cover core components including:

* Fact extraction validation
* Fact matching
* Number normalization
* Date and unit normalization
* Evidence validation
* Verdict generation



---

# Limitations

Current limitations include:

* Scanned PDFs may require OCR.
* Complex tables may require specialized extraction.
* Entity resolution can remain ambiguous when source context is incomplete.
* Some numerical differences cannot be reconciled without additional reporting context.
* LLM relationship confidence is not statistically calibrated.
* Very large document collections require more advanced retrieval and batching strategies.
* The current prototype is optimized for document analysis rather than high-volume production workloads.

---

# Future Improvements

Potential next steps include:

* OCR support for scanned PDFs
* Improved table extraction
* Incremental knowledge updates
* Semantic retrieval for large document collections
* Human feedback loops for uncertain cases
* Document version tracking
* More advanced entity resolution
* REST API support
* Production database support
* Additional document formats such as DOCX and HTML

---

# AI Tools

## Gemini API

**Model:** Gemini 2.5 Flash

Gemini is used for:

```text
Semantic fact extraction
Semantic entity interpretation
Ambiguity resolution
Cross-document relationship reasoning
Concise relationship explanations
```

Gemini is not used for:

```text
PDF parsing
Arithmetic
Number normalization
Unit conversion
Date normalization
Database operations
Evidence validation
Deterministic matching
```

AI-assisted development tools may be used during implementation for coding, debugging, refinement, and documentation. Final architecture and project behavior are reviewed and integrated into the application.

---

# Additional Notes

DocIntel is designed as an evidence-first document intelligence system rather than a black-box PDF chatbot.

The central design principle is:

```text
Source Documents
      ↓
Structured Facts
      ↓
Evidence
      ↓
Normalization
      ↓
Cross-Document Relationships
      ↓
Validation
      ↓
Final Verdict
```

The system prioritizes traceability, contextual reasoning, and explicit uncertainty over forcing every extracted claim into a definitive conclusion.



