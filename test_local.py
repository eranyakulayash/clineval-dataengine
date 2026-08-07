"""
Local testing script for clineval-dataengine FHIR parser and AI readiness score calculator.
"""

import json
from clineval_dataengine import FHIRPatientParser, FHIRValidationError

def run_tests():
    print("=" * 60)
    print(" Running tests for clineval-dataengine ")
    print("=" * 60)

    parser = FHIRPatientParser()

    # 1. Comprehensive High Quality Patient Record
    high_quality_patient = {
        "resourceType": "Patient",
        "id": "pat-1001",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2026-08-01T10:00:00Z"
        },
        "active": True,
        "identifier": [
            {
                "system": "urn:oid:1.2.36.146.595.217.0.1",
                "value": "MRN-987654"
            }
        ],
        "name": [
            {
                "use": "official",
                "family": "Smith",
                "given": ["Jane", "Alice"]
            }
        ],
        "telecom": [
            {"system": "phone", "value": "555-0199", "use": "home"}
        ],
        "gender": "female",
        "birthDate": "1985-04-12",
        "address": [
            {
                "line": ["123 Main Street"],
                "city": "Boston",
                "state": "MA",
                "postalCode": "02115"
            }
        ],
        "communication": [
            {
                "language": {
                    "coding": [{"system": "urn:ietf:bcp:47", "code": "en"}]
                }
            }
        ],
        "generalPractitioner": [{"reference": "Practitioner/pr-55"}],
        "managingOrganization": [{"reference": "Organization/org-01"}],
        "extension": [
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "valueString": "Asian"
            }
        ]
    }

    print("\n[Test 1] Parsing & Scoring High Quality Patient Record...")
    parsed_hq = parser.parse_json(high_quality_patient)
    score_hq = parser.calculate_ai_readiness_score(parsed_hq)
    print(f" -> Readiness Score: {score_hq['score']}/100")
    print(f" -> Readiness Category: {score_hq['readiness_category']}")
    print(f" -> Score Breakdown: {score_hq['breakdown']}")
    assert score_hq['score'] >= 85, f"Expected >= 85, got {score_hq['score']}"
    print(" [OK] PASSED!")

    # 2. Basic Patient Record
    basic_patient = {
        "resourceType": "Patient",
        "id": "pat-1002",
        "name": [{"family": "Doe"}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }

    print("\n[Test 2] Parsing & Scoring Basic Patient Record...")
    parsed_basic = parser.parse_json(json.dumps(basic_patient))
    score_basic = parser.calculate_ai_readiness_score(parsed_basic)
    print(f" -> Readiness Score: {score_basic['score']}/100")
    print(f" -> Readiness Category: {score_basic['readiness_category']}")
    print(f" -> Score Breakdown: {score_basic['breakdown']}")
    assert 0 < score_basic['score'] < 85, f"Unexpected score: {score_basic['score']}"
    print(" [OK] PASSED!")

    # 3. Invalid Patient Record (invalid resourceType)
    invalid_patient = {
        "resourceType": "Observation",
        "id": "obs-001"
    }

    print("\n[Test 3] Validating Invalid Resource Type Handling...")
    try:
        parser.parse_json(invalid_patient)
        print(" [FAIL] FAILED: Expected FHIRValidationError not raised")
        assert False
    except FHIRValidationError as e:
        print(f" -> Caught expected exception: {e}")
        print(" [OK] PASSED!")

    # 4. Invalid birthDate format
    invalid_date_patient = {
        "resourceType": "Patient",
        "id": "pat-1003",
        "birthDate": "12/05/1995"
    }

    print("\n[Test 4] Validating Invalid birthDate Format...")
    try:
        parser.parse_json(invalid_date_patient)
        print(" [FAIL] FAILED: Expected FHIRValidationError not raised")
        assert False
    except FHIRValidationError as e:
        print(f" -> Caught expected exception: {e}")
        print(" [OK] PASSED!")

    print("\n" + "=" * 60)
    print(" ALL TESTS EXECUTED SUCCESSFULLY! ")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
