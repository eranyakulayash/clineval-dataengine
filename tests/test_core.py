import pytest
from clineval_dataengine import FHIRPatientParser, FHIRValidationError


@pytest.fixture
def parser():
    return FHIRPatientParser()


def test_high_quality_patient(parser):
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

    parsed = parser.parse_json(high_quality_patient)
    score_result = parser.calculate_ai_readiness_score(parsed)
    assert score_result["score"] == 100.0
    assert score_result["readiness_category"] == "Production AI Ready"


def test_basic_patient(parser):
    basic_patient = {
        "resourceType": "Patient",
        "id": "pat-1002",
        "name": [{"family": "Doe"}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }

    parsed = parser.parse_json(basic_patient)
    score_result = parser.calculate_ai_readiness_score(parsed)
    assert 0 < score_result["score"] < 85


def test_invalid_resource_type(parser):
    invalid_patient = {
        "resourceType": "Observation",
        "id": "obs-001"
    }

    with pytest.raises(FHIRValidationError, match="Expected resourceType 'Patient'"):
        parser.parse_json(invalid_patient)


def test_invalid_birth_date(parser):
    invalid_date_patient = {
        "resourceType": "Patient",
        "id": "pat-1003",
        "birthDate": "12/05/1995"
    }

    with pytest.raises(FHIRValidationError, match="Invalid birthDate format"):
        parser.parse_json(invalid_date_patient)
