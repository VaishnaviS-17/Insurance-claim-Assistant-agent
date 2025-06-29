import pandas as pd
import os

# Load your policy dataset once with proper path handling
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(os.path.dirname(current_dir), "poilicies.csv")
POLICIES = pd.read_csv(csv_path)

def validate_claim(insurance_type, policy_number, description):
    if not policy_number or not description:
        return "❌ Please provide all required claim details."

    try:
        policy_number = int(policy_number)
    except ValueError:
        return "❌ Invalid policy number format. Please enter digits only."

    # Check if policy number exists and matches insurance type
    matching_policy = POLICIES[
        (POLICIES['policy_number'] == policy_number) &
        (POLICIES['insurance_type'].str.lower() == insurance_type.lower())
    ]

    if matching_policy.empty:
        return "❌ Invalid policy number or mismatched insurance type."

    desc = description.lower()
    
    # STRICT VALIDATION: Only allow legitimate insurance claims
    VALID_CLAIM_EVENTS = {
        "Auto": [
            "accident", "collision", "crash", "total loss", "stolen", "theft", 
            "hit and run", "severe damage", "major damage", "write-off",
            "rear-ended", "side-swiped", "rollover", "flood damage", "fire damage"
        ],
        "Home": [
            "fire", "flood", "earthquake", "storm", "hurricane", "tornado", 
            "theft", "burglary", "vandalism", "structural damage", "roof damage",
            "water damage", "mold", "electrical fire", "gas leak", "explosion",
            "natural disaster", "severe weather", "lightning strike"
        ],
        "Health": [
            "emergency", "hospitalization", "surgery", "critical illness", 
            "serious injury", "accident", "heart attack", "stroke", "cancer",
            "broken bone", "fracture", "severe pain", "life-threatening",
            "medical emergency", "ambulance", "intensive care", "icu"
        ]
    }

    # Check if description contains a valid claim event
    valid_events = VALID_CLAIM_EVENTS.get(insurance_type, [])
    has_valid_event = any(event in desc for event in valid_events)
    
    if not has_valid_event:
        return f"❌ Invalid {insurance_type} claim. Must specify a legitimate insurance event like accident, fire, theft, or medical emergency."
    
    # Check for minor issues that shouldn't be claimed
    minor_issues = {
        "Auto": ["small scratch", "minor dent", "cosmetic damage", "paint chip", "small ding", "light scratch"],
        "Home": ["small leak", "minor stain", "cosmetic damage", "small crack", "minor wear", "light damage"],
        "Health": ["minor cold", "small cut", "minor bruise", "headache", "minor pain", "small injury"]
    }
    
    minor_keywords = minor_issues.get(insurance_type, [])
    if any(issue in desc for issue in minor_keywords):
        return f"❌ Minor {insurance_type} issue detected. This doesn't qualify for insurance claim."
    
    # Check for maintenance/regular issues
    maintenance_issues = [
        "regular maintenance", "routine check", "preventive care", "annual checkup",
        "wear and tear", "normal wear", "aging", "old", "worn out", "maintenance",
        "service", "oil change", "tune up", "cleaning", "minor repair"
    ]
    
    if any(issue in desc for issue in maintenance_issues):
        return "❌ Maintenance/regular issues are not covered by insurance."
    
    # Enhanced fraud detection
    fraud_patterns = [
        "repeat claim", "exaggerated", "suspicious", "fake", "scam", "false report",
        "fraudulent", "duplicate", "multiple claims", "suspicious activity", 
        "unusual pattern", "made up", "fake damage", "pretend", "simulate"
    ]
    
    if any(pat in desc for pat in fraud_patterns):
        return "🚨 Fraud detected! Claim flagged for investigation."
    
    # Check for severity indicators
    severity_indicators = ["severe", "major", "extensive", "significant", "substantial", "serious", "critical"]
    has_severity = any(severity in desc for severity in severity_indicators)
    
    if has_severity:
        return f"✅ {insurance_type} claim APPROVED. High severity incident confirmed."
    else:
        return f"⚠️ {insurance_type} claim PENDING REVIEW. Please provide more details about damage severity."

def get_policy_holder(policy_number):
    """Get policy holder name for a given policy number"""
    try:
        policy_number = int(policy_number)
        matching_policy = POLICIES[POLICIES['policy_number'] == policy_number]
        if not matching_policy.empty:
            return matching_policy.iloc[0]['policy_holder']
        return None
    except:
        return None

def get_claim_guidance(insurance_type):
    """Get guidance for what constitutes a valid claim"""
    guidance = {
        "Auto": {
            "valid_claims": [
                "Vehicle collision/accident with significant damage",
                "Total loss due to accident or natural disaster",
                "Theft of vehicle",
                "Severe damage from fire, flood, or storm",
                "Hit and run incidents with substantial damage"
            ],
            "not_covered": [
                "Minor scratches or dents",
                "Regular maintenance and wear",
                "Cosmetic damage only",
                "Small paint chips",
                "Routine service issues"
            ]
        },
        "Home": {
            "valid_claims": [
                "Fire damage to property",
                "Flood or water damage",
                "Theft or burglary",
                "Storm or natural disaster damage",
                "Structural damage",
                "Vandalism with significant damage"
            ],
            "not_covered": [
                "Minor wear and tear",
                "Regular maintenance",
                "Cosmetic damage",
                "Small leaks or stains",
                "Normal aging of property"
            ]
        },
        "Health": {
            "valid_claims": [
                "Medical emergencies requiring hospitalization",
                "Surgery or major procedures",
                "Critical illness treatment",
                "Serious injuries from accidents",
                "Life-threatening conditions"
            ],
            "not_covered": [
                "Regular checkups",
                "Minor illnesses",
                "Preventive care",
                "Cosmetic procedures",
                "Minor injuries"
            ]
        }
    }
    
    return guidance.get(insurance_type, {}) 