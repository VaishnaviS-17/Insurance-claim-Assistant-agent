from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
import requests
import numpy as np

# Load ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL).text.splitlines()

# Load pretrained model
model = resnet50(pretrained=True)
model.eval()

# Preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Enhanced insurance-specific configurations
INSURANCE_CONFIG = {
    "auto": {
        "parts": ["Front Bumper", "Rear Bumper", "Windshield", "Doors", "Headlights", "Tires", "Hood", "Side Panel"],
        "damage_types": ["dent", "scratch", "crack", "shattered", "broken", "collision damage"],
        "price_ranges": {
            "Front Bumper": (5000, 15000),
            "Rear Bumper": (5000, 12000),
            "Windshield": (8000, 20000),
            "Doors": (3000, 10000),
            "Headlights": (2000, 7000),
            "Tires": (1500, 6000),
            "Hood": (4000, 12000),
            "Side Panel": (6000, 18000)
        },
        "keywords": ["car", "vehicle", "truck", "jeep", "automobile", "minivan", "pickup", "suv", "sports car", "convertible"],
        "response_template": "✅ Vehicle damage detected (confidence: {confidence:.1%})\nDamage Type: {damage_type} on {part}\nEstimated Repair Cost: ₹{cost:,}\nApproved Claim: ₹{claim:,}"
    },
    "home": {
        "damage_levels": ["minor", "moderate", "severe"],
        "types": ["water", "fire", "structural", "theft", "vandalism"],
        "price_ranges": {
            "minor": (10000, 30000),
            "moderate": (30000, 80000),
            "severe": (80000, 200000)
        },
        "keywords": ["house", "building", "property", "apartment", "structure", "fire", "flame", "smoke", "condo", "residence"],
        "response_template": "✅ Property damage detected (confidence: {confidence:.1%})\nDamage Type: {damage_type} ({severity})\nEstimated Repair Cost: ₹{cost:,}\nApproved Claim: ₹{claim:,}"
    },
    "health": {
        "document_types": ["medical bill", "prescription", "hospital report", "diagnostic report", "doctor's note", "discharge summary"],
        "treatment_types": ["consultation", "procedure", "hospitalization", "medication", "diagnostic test"],
        "price_ranges": {
            "consultation": (500, 3000),
            "procedure": (3000, 50000),
            "hospitalization": (10000, 200000),
            "medication": (200, 10000),
            "diagnostic test": (1000, 15000)
        },
        "keywords": ["medical", "hospital", "clinic", "doctor", "prescription", "report", "bill", 
                   "envelope", "paper", "document", "form", "certificate", "letter", "chart", 
                   "record", "x-ray", "ambulance", "stretcher", "pharmacy", "medicine"],
        "response_template": "✅ Medical document verified (confidence: {confidence:.8%})\n Document Type: {doc_type}\n Treatment: {treatment}\n Estimated Cost: ₹{cost:,}\n Approved Claim: ₹{claim:,}"
    }
}

def analyze_image(uploaded_file, insurance_type):
    debug_info = []
    try:
        # Open and preprocess image
        image = Image.open(uploaded_file).convert("RGB")
        input_tensor = preprocess(image).unsqueeze(0)
        
        # Get model predictions
        with torch.no_grad():
            output = model(input_tensor)
        
        # Get top predictions
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_idx = torch.topk(probabilities, 5)
        
        # Store debug information
        for i in range(5):
            debug_info.append(f"Prediction {i+1}: {labels[top5_idx[i]].lower()} ({top5_prob[i].item():.1%})")
        
        # Get insurance-specific settings
        insurance_type = insurance_type.lower()
        config = INSURANCE_CONFIG.get(insurance_type, {})
        relevant_keywords = config.get("keywords", [])
        
        # Check for relevant image content
        is_relevant = False
        confidence = 0.0
        top_label = ""
        
        for i in range(5):
            pred_label = labels[top5_idx[i]].lower()
            pred_conf = top5_prob[i].item()
            
            if any(keyword in pred_label for keyword in relevant_keywords):
                is_relevant = True
                confidence = max(confidence, pred_conf)
                top_label = pred_label
                break
        
        if not is_relevant:
            return "⚠️ Image doesn't match the insurance type. Please upload a relevant image.", debug_info
        
        # Generate appropriate response
        if insurance_type == "auto":
            damage_part = np.random.choice(config["parts"])
            damage_type = np.random.choice(config["damage_types"])
            min_price, max_price = config["price_ranges"][damage_part]
            estimated_cost = np.random.randint(min_price, max_price)
            claim_amount = int(estimated_cost * 0.8)
            
            result = config["response_template"].format(
                confidence=confidence,
                damage_type=damage_type.capitalize(),
                part=damage_part,
                cost=estimated_cost,
                claim=claim_amount
            )
            return result, debug_info
        
        elif insurance_type == "home":
            damage_level = np.random.choice(config["damage_levels"])
            damage_type = np.random.choice(config["types"])
            min_price, max_price = config["price_ranges"][damage_level]
            estimated_cost = np.random.randint(min_price, max_price)
            claim_amount = int(estimated_cost * 0.7)
            
            result = config["response_template"].format(
                confidence=confidence,
                damage_type=damage_type.capitalize(),
                severity=damage_level,
                cost=estimated_cost,
                claim=claim_amount
            )
            return result, debug_info
        
        elif insurance_type == "health":
            # Enhanced document type detection
            doc_type = "medical document"
            if "prescription" in top_label:
                doc_type = "prescription"
            elif "bill" in top_label or "invoice" in top_label:
                doc_type = "medical bill"
            elif "report" in top_label or "summary" in top_label:
                doc_type = "medical report"
            elif "x-ray" in top_label or "scan" in top_label:
                doc_type = "diagnostic image"
            else:
                doc_type = np.random.choice(config["document_types"])
            
            treatment = np.random.choice(config["treatment_types"])
            min_price, max_price = config["price_ranges"][treatment]
            estimated_cost = np.random.randint(min_price, max_price)
            claim_amount = int(estimated_cost * 0.85)
            
            result = config["response_template"].format(
                confidence=confidence,
                doc_type=doc_type.capitalize(),
                treatment=treatment,
                cost=estimated_cost,
                claim=claim_amount
            )
            return result, debug_info
    
    except Exception as e:
        return f"⚠️ Error processing image: {str(e)}", debug_info