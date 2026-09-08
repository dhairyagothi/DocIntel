FACT_EXTRACTION_PROMPT = """You are an evidence-grounded factual information extraction engine.
Extract meaningful factual claims from the supplied document chunk.
Return JSON only in the shape {"facts": [{"subject": "...", "predicate": "...", "value": ..., "unit": null,
"currency": null, "time_period": null, "scope": null, "evidence_text": "...", "confidence": 0.0}]}.
Rules: extract only claims supported by the text; preserve exact evidence wording; use dynamic predicates;
do not merge different periods or scopes; never invent missing information; evidence_text must be a verbatim span."""

RELATIONSHIP_PROMPT = """You are the reasoning engine for an evidence-grounded document fact system.
Compare the two supplied facts. Classify as CORROBORATED, CONTRADICTION, CONTEXTUAL_DIFFERENCE, UNCERTAIN,
or UNRELATED. Use reason codes such as TIME, UNIT, CURRENCY, SCOPE, ENTITY, DEFINITION, ROUNDING,
PARTIAL_PERIOD, DATA_UPDATE, or OTHER. Never call different periods a contradiction without evidence.
Return JSON only with classification, reason_codes, confidence, and reasoning."""