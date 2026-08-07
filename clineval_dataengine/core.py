"""
Core module for clineval-dataengine.
Provides FHIR Patient record parsing, validation, and Clinical AI Readiness scoring.
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Any, Union, Optional


class FHIRValidationError(Exception):
    """Exception raised for errors in FHIR Patient resource validation."""
    pass


class FHIRPatientParser:
    """
    Parser and Validator for FHIR R4 Patient Resources with AI Readiness Assessment.
    """

    VALID_GENDERS = {"male", "female", "other", "unknown"}

    def parse_json(self, raw_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses a JSON string or dict into a validated dictionary structure.
        """
        if isinstance(raw_data, str):
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError as e:
                raise FHIRValidationError(f"Invalid JSON string: {e}")
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            raise FHIRValidationError("Input must be a JSON string or Python dictionary.")

        is_valid, errors = self.validate_patient(data)
        if not is_valid:
            raise FHIRValidationError(f"FHIR Patient Validation Failed: {'; '.join(errors)}")

        return data

    def validate_patient(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates whether a dictionary conforms to basic FHIR R4 Patient resource specifications.
        Returns a tuple of (is_valid, list_of_validation_errors).
        """
        errors = []

        if not isinstance(data, dict):
            return False, ["Resource must be a JSON object."]

        # Check resourceType
        resource_type = data.get("resourceType")
        if resource_type != "Patient":
            errors.append(f"Expected resourceType 'Patient', got '{resource_type}'.")

        # Check ID
        if not data.get("id"):
            errors.append("Patient resource missing 'id'.")

        # Check gender if present
        gender = data.get("gender")
        if gender and gender.lower() not in self.VALID_GENDERS:
            errors.append(f"Invalid gender '{gender}'. Must be one of {self.VALID_GENDERS}.")

        # Check birthDate format if present
        birth_date = data.get("birthDate")
        if birth_date:
            try:
                datetime.strptime(birth_date, "%Y-%m-%d")
            except ValueError:
                errors.append(f"Invalid birthDate format '{birth_date}'. Must be YYYY-MM-DD.")

        # Check names if present
        names = data.get("name")
        if names is not None:
            if not isinstance(names, list) or len(names) == 0:
                errors.append("'name' must be a non-empty list of HumanName elements.")
            else:
                for idx, name_item in enumerate(names):
                    if not isinstance(name_item, dict):
                        errors.append(f"name[{idx}] must be an object.")

        return len(errors) == 0, errors

    def calculate_ai_readiness_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a Clinical AI Readiness Score (0-100) based on data completeness,
        structural integrity, and demographic completeness required for clinical ML models.

        Score Breakdown (Total 100 points):
        - Core Demographics & Identity (30 pts)
        - Contact & Location Details (20 pts)
        - Provider & Organization Context (20 pts)
        - AI Feature Enrichment & Metadata (30 pts)
        """
        is_valid, _ = self.validate_patient(data)
        if not is_valid:
            return {
                "score": 0.0,
                "readiness_category": "Unusable",
                "details": {"error": "Invalid FHIR Patient record"}
            }

        scores = {
            "demographics": 0.0,
            "contact": 0.0,
            "provider_context": 0.0,
            "enrichment_metadata": 0.0,
        }

        # 1. Core Demographics & Identity (Max 30 pts)
        # ID present (+5)
        if data.get("id"):
            scores["demographics"] += 5.0

        # Names: family (+10), given (+5)
        names = data.get("name", [])
        if isinstance(names, list) and len(names) > 0:
            primary_name = names[0]
            if isinstance(primary_name, dict):
                if primary_name.get("family"):
                    scores["demographics"] += 10.0
                if primary_name.get("given"):
                    scores["demographics"] += 5.0

        # Gender (+5)
        if data.get("gender") in self.VALID_GENDERS:
            scores["demographics"] += 5.0

        # birthDate (+5)
        if data.get("birthDate"):
            scores["demographics"] += 5.0

        # 2. Contact & Location Details (Max 20 pts)
        # Identifiers (MRN, SSN, etc.) (+10)
        identifiers = data.get("identifier", [])
        if isinstance(identifiers, list) and len(identifiers) > 0:
            scores["contact"] += 10.0

        # Address completeness (+5)
        addresses = data.get("address", [])
        if isinstance(addresses, list) and len(addresses) > 0:
            addr = addresses[0]
            if isinstance(addr, dict) and (addr.get("postalCode") or addr.get("city")):
                scores["contact"] += 5.0

        # Telecom contact (+5)
        telecoms = data.get("telecom", [])
        if isinstance(telecoms, list) and len(telecoms) > 0:
            scores["contact"] += 5.0

        # 3. Provider & Organization Context (Max 20 pts)
        # Active status explicitly set (+5)
        if "active" in data and isinstance(data["active"], bool):
            scores["provider_context"] += 5.0

        # General Practitioner (+8)
        if data.get("generalPractitioner"):
            scores["provider_context"] += 8.0

        # Managing Organization (+7)
        if data.get("managingOrganization"):
            scores["provider_context"] += 7.0

        # 4. AI Feature Enrichment & Metadata (Max 30 pts)
        # Language / Communication (+10)
        communications = data.get("communication", [])
        if isinstance(communications, list) and len(communications) > 0:
            scores["enrichment_metadata"] += 10.0

        # Extension (Race, Ethnicity, US-Core extensions) (+10)
        extensions = data.get("extension", [])
        if isinstance(extensions, list) and len(extensions) > 0:
            scores["enrichment_metadata"] += 10.0

        # Meta timestamp / version (+10)
        meta = data.get("meta", {})
        if isinstance(meta, dict) and (meta.get("lastUpdated") or meta.get("versionId")):
            scores["enrichment_metadata"] += 10.0

        total_score = round(sum(scores.values()), 2)

        if total_score >= 85:
            category = "Production AI Ready"
        elif total_score >= 60:
            category = "Moderate AI Readiness"
        elif total_score >= 35:
            category = "Basic AI Readiness"
        else:
            category = "Low Quality / Incomplete"

        return {
            "score": total_score,
            "readiness_category": category,
            "breakdown": scores
        }
