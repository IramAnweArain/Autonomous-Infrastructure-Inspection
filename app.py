import streamlit as st
from roboflow import Roboflow
import PIL.Image
import numpy as np
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ITSOLERA | Infrastructure AI",
    page_icon="🏗️",
    layout="wide"
)

# --- 2. THE ROBOLOFLOW ENGINE ---
# Your specific V3 Model Credentials
API_KEY = "KkMa6VA9JRqJvv8X8tSl" 
LIB_PROJECT = "autonomous_infrastructure_v1"
LIB_VERSION = 3

@st.cache_resource
def load_roboflow_model():
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace("irams-workspace").project(LIB_PROJECT)
    return project.version(LIB_VERSION).model

model = load_roboflow_model()

# --- 3. USER INTERFACE (UI) ---
st.title("🏗️ Autonomous Infrastructure Inspection System")
st.markdown("""
**Advanced YOLO11-Segmentation Pipeline** Detecting Cracks, Potholes, and Corrosion for Proactive Maintenance.
""")

st.sidebar.image("https://www.devlogics.org/wp-content/uploads/2024/07/cropped-DEVLOGICS-Logo-Facebook-Cover-Photo-2460x936-6-1024x470-removebg-preview.png", width=200)
st.sidebar.title("🛠️ Control Panel")

with st.sidebar:
    st.info("Model: YOLO11-Nano (Instance Segmentation)")
    conf_thresh = st.slider("Confidence Threshold (%)", 0, 100, 40)
    overlap_thresh = st.slider("Overlap Threshold (%)", 0, 100, 30)
    st.markdown("---")
    st.write("📊 **V3 Performance Stats**")
    st.write("- Corrosion: 99.0%")
    st.write("- Pothole: 44.0%")
    st.write("- Crack: 16.0%")

# --- 4. DATA INGESTION ---
uploaded_file = st.file_uploader("📤 Upload Drone Imagery or Inspection Frame", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Display Original
    col1, col2 = st.columns(2)
    image = PIL.Image.open(uploaded_file)
    
    with col1:
        st.subheader("Original Input")
        st.image(image, use_container_width=True)
    
    # Run Analysis
    if st.button("🚀 Start AI Structural Analysis"):
        with st.spinner("Analyzing image segments..."):
            # Temporary save for API processing
            temp_path = "temp_analysis.jpg"
            image.save(temp_path)
            
            # Request Prediction from Roboflow Cloud
            prediction = model.predict(temp_path, confidence=conf_thresh, overlap=overlap_thresh)
            
            # Save and Show Result
            output_path = "output_analysis.jpg"
            prediction.save(output_path)
            
            with col2:
                st.subheader("AI Annotated Output")
                st.image(output_path, use_container_width=True)

            # --- 5. THE AUTOMATED REPORT (Project Requirement) ---
            st.markdown("---")
            st.subheader("📋 Automated Maintenance & Severity Report")
            
            results = prediction.json()
            if results['predictions']:
                # Create data for table
                report_table = []
                for p in results['predictions']:
                    # Logic for 'Novelty' Severity calculation
                    area = p['width'] * p['height']
                    severity = "🔴 CRITICAL" if area > 12000 else "🟡 MINOR"
                    
                    report_table.append({
                        "Defect Type": p['class'].upper(),
                        "Confidence": f"{p['confidence']:.1%}",
                        "Est. Area (px)": f"{area:,.0f}",
                        "Severity Status": severity,
                        "GPS Tag": "34.0522, -118.2437" # Simulated as per methodology
                    })
                
                st.table(report_table)
                
                # Success Logic for your Document
                st.success(f"Analysis Complete. {len(results['predictions'])} structural defects identified.")
            else:
                st.balloons()
                st.success("No critical defects detected. Structure status: COMPLIANT.")

# --- 6. FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Developed by Iram Anwer | ITSOLERA Final Project 2026")
