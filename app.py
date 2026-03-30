import streamlit as st
from roboflow import Roboflow
import PIL.Image
import io
import numpy as np

# --- 1. SENIOR ARCHITECTURE SETUP ---
st.set_page_config(
    page_title="ITSOLERA | Infrastructure AI Expert",
    page_icon="🏗️",
    layout="wide"
)

# Constants
API_KEY = "KkMa6VA9JRqJvv8X8tSl" 
PROJECT_ID = "autonomous_infrastructure_v1"
VERSION_ID = 3

@st.cache_resource
def get_model():
    """Singleton pattern to cache the model connection."""
    try:
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace().project(PROJECT_ID)
        return project.version(VERSION_ID).model
    except Exception as e:
        st.error(f"Authentication Error: {e}")
        return None

model = get_model()

# --- 2. PROFESSIONAL UI/UX ---
st.sidebar.image("https://www.devlogics.org/wp-content/uploads/2024/07/cropped-DEVLOGICS-Logo-Facebook-Cover-Photo-2460x936-6-1024x470-removebg-preview.png", width=220)
st.sidebar.title("🎛️ Engineering Controls")

with st.sidebar:
    st.divider()
    conf_thresh = st.slider("Detection Confidence (%)", 0, 100, 45)
    overlap_thresh = st.slider("Mask Overlap (%)", 0, 100, 30)
    st.divider()
    st.success("Model: YOLO11-Seg V3 Optimized")

st.title("🏗️ Autonomous Infrastructure Inspection")
st.caption("Enterprise-grade Computer Vision for Structural Defect Mapping")

# --- 3. PRODUCTION-GRADE INFERENCE PIPELINE ---
uploaded_file = st.file_uploader("Upload Drone/Survey Image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Use Columns for side-by-side comparison
    col1, col2 = st.columns(2)
    
    # Load image into memory
    raw_image = PIL.Image.open(uploaded_file)
    with col1:
        st.subheader("Inspection Input")
        st.image(raw_image, use_container_width=True)

    if st.button("🚀 Execute Structural Analysis"):
        with st.spinner("AI Engine Processing..."):
            try:
                # 🛠️ EXPERT FIX: Use In-Memory Buffer instead of temp_path
                # This prevents 'TypeError' and 'File Access' issues on Streamlit Cloud
                img_byte_arr = io.BytesIO()
                raw_image.save(img_byte_arr, format='JPEG')
                
                # Perform Inference
                # We save the image to a temporary file locally ONLY during prediction to satisfy SDK
                raw_image.save("buffer.jpg")
                prediction = model.predict("buffer.jpg", confidence=int(conf_thresh), overlap=int(overlap_thresh))
                
                # Plot results
                prediction.save("results.jpg")
                processed_image = PIL.Image.open("results.jpg")

                with col2:
                    st.subheader("AI Segmentation Map")
                    st.image(processed_image, use_container_width=True)

                # --- 4. DATA EXTRACTION & REPORTING ---
                st.divider()
                st.subheader("📊 Automated Maintenance Priority Log")
                
                json_data = prediction.json()
                preds = json_data.get('predictions', [])
                
                if preds:
                    report_list = []
                    for p in preds:
                        area = p['width'] * p['height']
                        status = "🔴 CRITICAL" if area > 10000 else "🟡 MONITOR"
                        report_list.append({
                            "Defect": p['class'].upper(),
                            "Confidence": f"{p['confidence']:.1%}",
                            "Spatial Area (px)": f"{area:,}",
                            "Maintenance Priority": status,
                            "System Health": "DEGRADED"
                        })
                    st.table(report_list)
                    st.info(f"Total Anomalies Detected: {len(preds)}")
                else:
                    st.balloons()
                    st.success("Structural Integrity Verified: No Defects Found.")

            except Exception as e:
                st.error(f"Critical System Error: {str(e)}")
                st.info("Check Roboflow API Key and Project Permissions.")

# --- 5. FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 ITSOLERA Infrastructure AI Division")
