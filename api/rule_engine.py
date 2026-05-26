import math
import random

class ProductionRuleEngine:
    def __init__(self):

        self.data_weights = {
            "ssn": 0.95,
            "financial": 0.90,
            "medical": 0.85,
            "drivers_license": 0.80,
            "passport": 0.80,
            "full_name": 0.40,
            "email": 0.30,
            "phone": 0.20,
            "address": 0.25,
            "password": 0.50,
        }

        self.breach_base_scores = {
            "healthcare": 0.80,
            "finance": 0.85,
            "tech": 0.60,
            "retail": 0.55,
            "government": 0.90,
            "education": 0.50,
        }

    def calculate_eligibility(self, data: dict):
        """
        Production-grade rule-based scoring.
        Ensures 100% deterministic output without NaNs.
        """

        breach_type = data.get("breach_type", "tech").lower()
        base_score = self.breach_base_scores.get(breach_type, 0.50)

        exposed_data = str(data.get("data_exposed", "")).lower()
        data_score = 0.1
        for key, weight in self.data_weights.items():
            if key in exposed_data:
                data_score = max(data_score, weight)

        records = data.get("records_affected", 1000)
        try:
            records = int(records)
            impact_bonus = min(0.2, math.log10(max(1, records)) / 20)
        except:
            impact_bonus = 0.05

        impact_level = data.get("user_impact_level", "Medium").lower()
        impact_multiplier = (
            1.2 if impact_level == "high" else 1.0 if impact_level == "medium" else 0.8
        )

        raw_score = (base_score * 0.4 + data_score * 0.6) + impact_bonus
        final_score = min(0.99, max(0.01, raw_score * impact_multiplier))

        if final_score >= 0.85:
            status = "Highly Eligible"
            urgency = "Immediate Action Recommended"
        elif final_score >= 0.60:
            status = "Likely Eligible"
            urgency = "Action Recommended"
        elif final_score >= 0.40:
            status = "Possibly Eligible"
            urgency = "Monitor Situation"
        else:
            status = "Not Eligible"
            urgency = "Low Priority"

        base_payout = 125
        if "ssn" in exposed_data or "financial" in exposed_data:
            payout_range = f"${base_payout * 4} - ${base_payout * 80}"
        elif "medical" in exposed_data:
            payout_range = f"${base_payout * 2} - ${base_payout * 40}"
        else:
            payout_range = f"${base_payout} - ${base_payout * 5}"

        success_prob = min(0.95, final_score * 0.9)

        return {
            "eligibility_status": status,
            "confidence_score": round(final_score, 4),
            "success_probability": round(success_prob, 4),
            "payout_estimate": payout_range,
            "urgency_level": urgency,
            "reasoning": self._generate_reasoning(status, exposed_data, breach_type),
            "recommended_actions": self._generate_actions(status, exposed_data),
        }

    def _generate_reasoning(self, status, exposed_data, breach_type):
        reasons = [f"Our AI analyzed the {breach_type} nature of this incident."]
        if "ssn" in exposed_data or "financial" in exposed_data:
            reasons.append(
                "Exposure of sensitive identifiers (SSN/Financial) significantly increases legal standing."
            )
        if "medical" in exposed_data:
            reasons.append(
                "Medical data exposure is protected under strict privacy regulations (e.g. HIPAA)."
            )

        if status == "Highly Eligible":
            reasons.append(
                "The high concentration of sensitive data elements suggests a strong claim case."
            )
        elif status == "Not Eligible":
            reasons.append(
                "Minimal exposure of sensitive data types reduces the likelihood of a successful claim."
            )

        return reasons

    def _generate_actions(self, status, exposed_data):
        actions = ["Monitor your accounts for suspicious activity."]
        if status != "Not Eligible":
            actions.append("Locate your official breach notification letter or email.")
            actions.append("Join the claim registration list to preserve your rights.")

        if "ssn" in exposed_data:
            actions.append(
                "Place a security freeze on your credit reports at all three major bureaus."
            )
        if "password" in exposed_data:
            actions.append(
                "Change your passwords and enable 2FA on all major accounts."
            )

        return actions

rule_engine = ProductionRuleEngine()
