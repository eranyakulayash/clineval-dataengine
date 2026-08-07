# clineval-dataengine

[![Test Status](https://github.com/eranyakulayash/clineval-dataengine/actions/workflows/test.yml/badge.svg)](https://github.com/eranyakulayash/clineval-dataengine/actions/workflows/test.yml)

Clinical AI Data Evaluation and Processing Engine for FHIR records.

## Features
- **FHIR Patient Resource Validation**: Validates JSON payloads against HL7 FHIR R4 Patient specifications.
- **Clinical AI Readiness Scoring**: Calculates a score from 0-100 evaluating data completeness across core demographics, contact details, provider context, and metadata enrichment needed for machine learning models.

## Installation

```bash
pip install clineval-dataengine
```

## Quickstart

```python
from clineval_dataengine import FHIRPatientParser

parser = FHIRPatientParser()

patient_data = {
    "resourceType": "Patient",
    "id": "pat-1001",
    "name": [{"family": "Smith", "given": ["Jane"]}],
    "gender": "female",
    "birthDate": "1985-04-12"
}

# Parse and validate
parsed = parser.parse_json(patient_data)

# Calculate Clinical AI Readiness Score
score_result = parser.calculate_ai_readiness_score(parsed)
print("Readiness Score:", score_result["score"])
print("Category:", score_result["readiness_category"])
```

## License
MIT License