Insurance Claim AI Assistant Agent

Problem Statement
Insurance claims often face delays due to manual documentation, fraud risks, and lack of clarity for customers. Our AI Agent streamlines Auto, Home, and Health Insurance claims by:

✅ Validating policy details  
✅ Generating AI-powered next steps for claimants  
✅ Detecting fraud patterns  
✅ Analyzing uploaded images to verify damage evidence  

Features

- Supports Auto, Home, and Health insurance claims  
- AI Guidance powered by Hugging Face GenAI models (GPT-2)  
- Real-time policy validation using mock dataset  
- Image upload with Vision AI to detect claim-related images  
- Flags unrelated images or suspicious claims  
- Designed for BFSI industry to improve claim processing speed and transparency  


Technology Stack

| Component       | Library/Tool                     |
|-----------------|----------------------------------|
| UI              | Streamlit                        |
| Backend Logic   | Python                           |
| GenAI           | Hugging Face Transformers(GPT-2) | 
| Vision AI       | TorchVision with ResNet18        |
| Image Handling  | Pillow                           |
| Data Processing | Pandas                           |


Installation
pip install -r requirements.txt
python -m streamlit run app.py