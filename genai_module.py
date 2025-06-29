from transformers import pipeline
import random

# Load GPT-2 model
generator = pipeline("text-generation", model="gpt2")

# Enhanced insurance-specific guidance templates
INSURANCE_GUIDANCE = {
    "auto": {
        "next_steps": [
            "📋 Contact your insurance agent within 24 hours",
            "🚔 File a police report if it's a collision",
            "📸 Take photos of all damage from multiple angles",
            "🔧 Get 2-3 repair estimates from authorized garages",
            "📞 Keep all receipts and documentation",
            "🚗 Don't drive the damaged vehicle if unsafe"
        ],
        "documents_needed": [
            "Driver's license and registration",
            "Police report (if applicable)",
            "Repair estimates",
            "Photos of damage",
            "Witness statements (if any)"
        ],
        "tips": [
            "Don't admit fault at the scene",
            "Exchange information with other parties",
            "Note weather and road conditions",
            "Get medical attention if injured"
        ]
    },
    "home": {
        "next_steps": [
            "📞 Contact emergency services if needed",
            "📸 Document all damage with photos/videos",
            "🔒 Secure the property to prevent further damage",
            "📋 Contact your insurance agent immediately",
            "🏠 Don't make permanent repairs until inspected",
            "💰 Keep all receipts for temporary repairs"
        ],
        "documents_needed": [
            "Property ownership documents",
            "Photos/videos of damage",
            "Police report (for theft/vandalism)",
            "Repair estimates",
            "Inventory of damaged items"
        ],
        "tips": [
            "Don't throw away damaged items",
            "Take photos before cleanup",
            "Keep detailed records of all expenses",
            "Consider temporary accommodation if needed"
        ]
    },
    "health": {
        "next_steps": [
            "🏥 Seek immediate medical attention if emergency",
            "📞 Contact your insurance provider",
            "📋 Get pre-authorization for procedures",
            "📄 Keep all medical bills and receipts",
            "💊 Save prescription receipts",
            "📊 Request detailed medical reports"
        ],
        "documents_needed": [
            "Medical bills and receipts",
            "Doctor's prescriptions",
            "Hospital discharge summary",
            "Diagnostic test reports",
            "Insurance card and ID"
        ],
        "tips": [
            "Always get pre-authorization",
            "Keep copies of all documents",
            "Track all medical expenses",
            "Follow up on claim status regularly"
        ]
    }
}

def get_genai_response(insurance_type, description):
    insurance_type = insurance_type.lower()
    
    # Get insurance-specific guidance
    guidance = INSURANCE_GUIDANCE.get(insurance_type, {})
    
    # Generate contextual response
    if insurance_type == "auto":
        context = "Auto Insurance Claim Guidance"
        if "collision" in description.lower():
            response = "🚗 Collision detected. Priority: Ensure safety, document damage, and contact authorities."
        elif "theft" in description.lower():
            response = "🔒 Vehicle theft reported. Priority: File police report and provide vehicle details."
        else:
            response = "🚙 Auto claim submitted. Follow the next steps for smooth processing."
    
    elif insurance_type == "home":
        context = "Home Insurance Claim Guidance"
        if "fire" in description.lower():
            response = "🔥 Fire damage detected. Priority: Ensure safety, contact fire department, and document damage."
        elif "flood" in description.lower():
            response = "💧 Flood damage reported. Priority: Stop water source and prevent further damage."
        else:
            response = "🏠 Home claim submitted. Follow the next steps for proper assessment."
    
    elif insurance_type == "health":
        context = "Health Insurance Claim Guidance"
        if "emergency" in description.lower():
            response = "🚨 Emergency medical situation. Priority: Seek immediate care and contact insurance provider."
        elif "surgery" in description.lower():
            response = "⚕️ Surgical procedure needed. Priority: Get pre-authorization and detailed cost estimates."
        else:
            response = "🏥 Health claim submitted. Follow the next steps for coverage verification."
    
    else:
        context = "Insurance Claim Guidance"
        response = "📋 Claim submitted successfully. Follow the provided guidance for processing."
    
    # Add next steps
    next_steps = guidance.get("next_steps", [])
    if next_steps:
        response += "\n\n**Next Steps:**\n" + "\n".join(next_steps[:3])  # Show first 3 steps
    
    return response

def get_claim_guidance(insurance_type):
    """Get comprehensive guidance for a specific insurance type"""
    guidance = INSURANCE_GUIDANCE.get(insurance_type.lower(), {})
    
    guidance_text = f"## 📋 {insurance_type} Insurance Claim Guide\n\n"
    
    if guidance.get("next_steps"):
        guidance_text += "### 🎯 Immediate Next Steps:\n"
        for step in guidance["next_steps"]:
            guidance_text += f"- {step}\n"
        guidance_text += "\n"
    
    if guidance.get("documents_needed"):
        guidance_text += "### 📄 Required Documents:\n"
        for doc in guidance["documents_needed"]:
            guidance_text += f"- {doc}\n"
        guidance_text += "\n"
    
    if guidance.get("tips"):
        guidance_text += "### 💡 Important Tips:\n"
        for tip in guidance["tips"]:
            guidance_text += f"- {tip}\n"
    
    return guidance_text

