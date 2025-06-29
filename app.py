import streamlit as st
from claim_validation import validate_claim, get_policy_holder
from genai_module import get_genai_response, get_claim_guidance
from vision_module import analyze_image
import os
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Insurance Claim AI Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .claim-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
    }
    
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 5px solid #dc3545;
    }
    
    .info-card {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
    }
    
    .custom-label {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        margin-top: 16px;
        color: #2c3e50;
    }
    
    .stSelectbox, .stTextInput, .stTextArea {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stSelectbox:focus, .stTextInput:focus, .stTextArea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'claim_history' not in st.session_state:
    st.session_state.claim_history = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'claim_data' not in st.session_state:
    st.session_state.claim_data = {}

# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ Insurance AI Agent")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📝 New Claim", "📊 Claim History", "📋 Guidelines", "⚙️ Settings"]
    )
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📈 Quick Stats")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.claim_history)}</div>
            <div class="metric-label">Total Claims</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        approved_claims = sum(1 for claim in st.session_state.claim_history if "✅" in claim.get('status', ''))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{approved_claims}</div>
            <div class="metric-label">Approved</div>
        </div>
        """, unsafe_allow_html=True)

# Main content based on navigation
if page == "📝 New Claim":
    # Header
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #2c3e50; font-size: 3rem; margin-bottom: 0.5rem;">🛡️ Insurance Claim AI Assistant</h1>
            <p style="color: #6c757d; font-size: 1.2rem; margin-bottom: 2rem;">
                Intelligent claim processing with AI-powered analysis and fraud detection
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add helpful guidance section
    with st.expander("📋 What constitutes a VALID insurance claim?", expanded=False):
        st.markdown("""
        ### ✅ **VALID Claims (Will be processed):**
        
        **🚗 Auto Insurance:**
        - Vehicle accidents/collisions with significant damage
        - Total loss due to accident or natural disaster
        - Theft of vehicle
        - Severe damage from fire, flood, or storm
        - Hit and run incidents with substantial damage
        
        **🏠 Home Insurance:**
        - Fire damage to property
        - Flood or water damage
        - Theft or burglary
        - Storm or natural disaster damage
        - Structural damage
        - Vandalism with significant damage
        
        **🏥 Health Insurance:**
        - Medical emergencies requiring hospitalization
        - Surgery or major procedures
        - Critical illness treatment
        - Serious injuries from accidents
        - Life-threatening conditions
        
        ### ❌ **INVALID Claims (Will be rejected):**
        
        **Minor Issues:**
        - Small scratches, dents, or cosmetic damage
        - Minor leaks, stains, or wear and tear
        - Regular maintenance and routine checks
        - Minor illnesses or small injuries
        - Preventive care and checkups
        
        **Maintenance:**
        - Oil changes, tune-ups, regular service
        - Normal wear and aging
        - Cosmetic procedures
        - Minor repairs and cleaning
        """)

    st.markdown("---")
    
    # Progress indicator
    steps = ["Basic Info", "Claim Details", "Documentation", "Review & Submit"]
    progress = st.session_state.current_step / len(steps)
    
    st.markdown(f"""
        <div style="margin: 2rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                {''.join([f'<span style="color: {"#667eea" if i < st.session_state.current_step else "#6c757d"}; font-weight: {"bold" if i < st.session_state.current_step else "normal"};">{step}</span>' for i, step in enumerate(steps)])}
            </div>
            <div class="progress-bar" style="width: {progress * 100}%;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Step 1: Basic Information
    if st.session_state.current_step == 1:
        st.markdown('<div class="claim-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Step 1: Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="custom-label">Insurance Type</div>', unsafe_allow_html=True)
            insurance_type = st.selectbox(
                "",
                ["Auto", "Home", "Health"],
                key="insurance_type"
            )
            
            st.markdown('<div class="custom-label">👤 Full Name</div>', unsafe_allow_html=True)
            name = st.text_input("", placeholder="Enter your full name", key="name")
        
        with col2:
            st.markdown('<div class="custom-label">📄 Policy Number</div>', unsafe_allow_html=True)
            policy_number = st.text_input("", placeholder="Enter your policy number", key="policy_number")
            
            # Policy validation
            if policy_number:
                policy_holder = get_policy_holder(policy_number)
                if policy_holder:
                    st.success(f"✅ Policy found for: {policy_holder}")
                else:
                    st.warning("⚠️ Policy number not found in database")
        
        if st.button("Next Step", key="next_step_1"):
            if name and policy_number and insurance_type:
                st.session_state.claim_data.update({
                    'name': name,
                    'policy_number': policy_number,
                    'insurance_type': insurance_type
                })
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Claim Details
    elif st.session_state.current_step == 2:
        st.markdown('<div class="claim-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Step 2: Claim Details")
        
        st.markdown(f'<div class="custom-label">📝 Describe your {st.session_state.claim_data.get("insurance_type", "")} Insurance Claim</div>', unsafe_allow_html=True)
        description = st.text_area(
            "",
            placeholder="Provide detailed description of the incident, damage, or medical condition...",
            height=150,
            key="description"
        )
        
        # Claim guidance
        if st.session_state.claim_data.get("insurance_type"):
            with st.expander("📋 Claim Guidelines", expanded=False):
                guidance = get_claim_guidance(st.session_state.claim_data["insurance_type"])
                st.markdown(guidance)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Step", key="prev_step_2"):
                st.session_state.current_step = 1
                st.rerun()
        
        with col2:
            if st.button("Next Step", key="next_step_2"):
                if description:
                    st.session_state.claim_data['description'] = description
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.error("Please provide a claim description")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: Documentation
    elif st.session_state.current_step == 3:
        st.markdown('<div class="claim-card">', unsafe_allow_html=True)
        st.markdown("### 📎 Step 3: Documentation")
        
        st.markdown('<div class="custom-label">📎 Upload Supporting Documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="Upload photos, medical reports, or other supporting documents"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
            
            # Show uploaded files
            for i, file in enumerate(uploaded_files):
                st.write(f"📄 {file.name} ({file.size} bytes)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Step", key="prev_step_3"):
                st.session_state.current_step = 2
                st.rerun()
        
        with col2:
            if st.button("Next Step", key="next_step_3"):
                st.session_state.claim_data['uploaded_files'] = uploaded_files
                st.session_state.current_step = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 4: Review and Submit
    elif st.session_state.current_step == 4:
        st.markdown('<div class="claim-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Step 4: Review and Submit")
        
        # Display claim summary
        st.markdown("#### 📋 Claim Summary")
        summary_data = {
            "Name": st.session_state.claim_data.get('name', ''),
            "Policy Number": st.session_state.claim_data.get('policy_number', ''),
            "Insurance Type": st.session_state.claim_data.get('insurance_type', ''),
            "Description": st.session_state.claim_data.get('description', ''),
            "Documents": len(st.session_state.claim_data.get('uploaded_files', []))
        }
        
        for key, value in summary_data.items():
            st.write(f"**{key}:** {value}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Step", key="prev_step_4"):
                st.session_state.current_step = 3
                st.rerun()
        
        with col2:
            if st.button("Submit Claim", key="submit_claim"):
                # Process the claim
                with st.spinner("Processing your claim..."):
                    validation_result = validate_claim(
                        st.session_state.claim_data['insurance_type'],
                        st.session_state.claim_data['policy_number'],
                        st.session_state.claim_data['description']
                    )
                    
                    ai_response = get_genai_response(
                        st.session_state.claim_data['insurance_type'],
                        st.session_state.claim_data['description']
                    )
                
                # Store claim in history
                claim_record = {
                    'timestamp': datetime.now().isoformat(),
                    'name': st.session_state.claim_data['name'],
                    'policy_number': st.session_state.claim_data['policy_number'],
                    'insurance_type': st.session_state.claim_data['insurance_type'],
                    'description': st.session_state.claim_data['description'],
                    'status': validation_result,
                    'ai_guidance': ai_response,
                    'documents': len(st.session_state.claim_data.get('uploaded_files', []))
                }
                st.session_state.claim_history.append(claim_record)
                
                # Display results
                st.markdown('<div class="success-card">', unsafe_allow_html=True)
                st.markdown("### 🎉 Claim Submitted Successfully!")
                st.write(f"**Validation Result:** {validation_result}")
                st.write(f"**AI Guidance:** {ai_response}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Image analysis if files uploaded
                if st.session_state.claim_data.get('uploaded_files'):
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown("### 📷 Document Analysis")
                    
                    for file in st.session_state.claim_data['uploaded_files']:
                        if file.type.startswith('image'):
                            image_feedback, debug_messages = analyze_image(
                                file, 
                                st.session_state.claim_data['insurance_type']
                            )
                            st.success(f"**Analysis Result:** {image_feedback}")
                            
                            with st.expander("🔍 Technical Details", expanded=False):
                                for msg in debug_messages:
                                    st.write(msg)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Reset for new claim
                st.session_state.current_step = 1
                st.session_state.claim_data = {}
                
                st.success("✅ Claim processed! You can start a new claim or view your claim history.")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📊 Claim History":
    st.markdown("## 📊 Claim History")
    
    if not st.session_state.claim_history:
        st.info("No claims submitted yet. Start by filing a new claim!")
    else:
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.claim_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Display claims
        for _, claim in df.iterrows():
            status_color = "success-card" if "✅" in claim['status'] else "warning-card" if "⚠️" in claim['status'] else "error-card"
            
            st.markdown(f'<div class="{status_color}">', unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{claim['insurance_type']} Claim** - {claim['name']}")
                st.write(f"**Policy:** {claim['policy_number']}")
                st.write(f"**Status:** {claim['status']}")
                st.write(f"**Description:** {claim['description'][:100]}...")
            
            with col2:
                # Convert string timestamp to datetime for proper formatting
                timestamp_str = claim['timestamp']
                if isinstance(timestamp_str, str):
                    from datetime import datetime
                    timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    st.write(f"**Date:** {timestamp_dt.strftime('%Y-%m-%d %H:%M')}")
                else:
                    st.write(f"**Date:** {timestamp_str}")
                st.write(f"**Documents:** {claim['documents']} files")
            
            with st.expander("AI Guidance", expanded=False):
                st.write(claim['ai_guidance'])
            
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "📋 Guidelines":
    st.markdown("## 📋 Insurance Claim Guidelines")
    
    insurance_type = st.selectbox("Select Insurance Type", ["Auto", "Home", "Health"])
    
    if insurance_type:
        guidance = get_claim_guidance(insurance_type)
        st.markdown(guidance)

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔧 Application Settings")
    
    # Clear claim history
    if st.button("Clear Claim History"):
        st.session_state.claim_history = []
        st.success("Claim history cleared!")
    
    # Export data
    if st.session_state.claim_history:
        if st.button("Export Claim History"):
            df = pd.DataFrame(st.session_state.claim_history)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="claim_history.csv",
                mime="text/csv"
            )
    
    st.markdown("### 📊 System Information")
    st.write(f"**Total Claims Processed:** {len(st.session_state.claim_history)}")
    st.write(f"**Current Session:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem 0;">
        <p>🛡️ Insurance Claim AI Agent | Powered by AI & Machine Learning</p>
        <p>For support, contact: support@insuranceai.com</p>
    </div>
""", unsafe_allow_html=True) 