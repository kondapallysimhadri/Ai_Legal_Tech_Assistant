LEGAL_ONTOLOGY = {
    "US": {
        "primary_statute": "California Consumer Privacy Act (CCPA)",
        "deadline_days": 365,
        "records_threshold": 500,
        "compensation_rules": "Statutory damages $100-$750 per consumer per incident.",
        "breach_types": {
            "finance": {"priority": "High", "consequence": "GLBA Regulation"},
            "healthcare": {"priority": "Critical", "consequence": "HIPAA Penalty"},
        },
    },
    "EU": {
        "primary_statute": "General Data Protection Regulation (GDPR)",
        "deadline_days": 730,
        "records_threshold": 1,
        "compensation_rules": "Right to compensation for material or non-material damage.",
        "breach_types": {
            "tech": {"priority": "High", "consequence": "Art. 82 Damage Claim"},
            "healthcare": {
                "priority": "Critical",
                "consequence": "Special Category Data Violation",
            },
        },
    },
    "India": {
        "primary_statute": "Digital Personal Data Protection Act (DPDP)",
        "deadline_days": 180,
        "records_threshold": 1000,
        "compensation_rules": "Penalties for failure to prevent data breach.",
        "breach_types": {
            "finance": {"priority": "High", "consequence": "Section 43A IT Act"}
        },
    },
}

def get_jurisdiction_rules(jurisdiction: str):
    return LEGAL_ONTOLOGY.get(jurisdiction.upper(), LEGAL_ONTOLOGY["US"])
