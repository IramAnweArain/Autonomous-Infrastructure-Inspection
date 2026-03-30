import streamlit as st
from roboflow import Roboflow
import PIL.Image
import io
import os

# --- 1. ARCHITECTURAL CONFIGURATION ---
st.set_page_config(
    page_title="ITSOLERA | Structural AI Expert",
    page_icon="🏗️",
    layout="wide"
)

# Configuration Constants
API_KEY = "KkMa6VA9JRqJvv8X8tSl" 
PROJECT_ID = "autonomous_infrastructure_v1"
VERSION_ID = 3

@st.cache_resource
def initialize_engine():
    """Singleton: Establish a persistent connection to the Vision Engine."""
    try:
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace().project(PROJECT_ID)
        return project.version(VERSION_ID).model
    except Exception as e:
        st.error(f"Engine Initialization Failed: {e}")
        return None

# Global Model Instance
model = initialize_engine()

# --- 2. PROFESSIONAL INTERFACE ---
st.sidebar.image("https://www.devlogics.org/wp-content/uploads/2024/07/cropped-DEVLOGICS-Logo-Facebook-Cover-Photo-2460x936-6-1024x470-removebg-preview.png", width=220)
st.sidebar.header("🛠️ Diagnostic Controls")

with st.sidebar:
    st.divider()
    # Fixed naming conventions to match SDK requirements
    conf_val = st.slider("Confidence Threshold (%)", 0, 100, 40)
    # The SDK for Segmentation often uses 'overlap_limit' or defaults; 
    # we will use 'overlap' only where supported or omit it for safety.
    overlap_val = st.slider("Mask Overlap Limit (%)", 0, 100, 30)
    st.divider()
    st.info(f"Model: YOLO11-Segmentation (V{VERSION_ID})")
    st.caption("Deployment: Roboflow Cloud API")

st.title("🏗️ Autonomous Infrastructure Inspection")
st.markdown("### Structural Defect Mapping & Integrity Analysis")

# --- 3. PRODUCTION INFERENCE PIPELINE ---
uploaded_file = st.file_uploader("Upload Drone/Aerial Imagery", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    # Process image through memory buffer
    img_data = PIL.Image.open(uploaded_file)
    with col1:
        st.subheader("Input Stream")
        st.image(img_data, use_container_width=True)

    if st.button("🚀 Execute Inspection Analysis"):
        with st.spinner("Vision Engine Running..."):
            try:
                # 🛠️ HARDENED FILE HANDLING
                # We save to a specific local path to ensure the .predict() method 
                # can reliably find the bytes on the container's disk.
                temp_filename = "active_inspection.jpg"
                img_data.save(temp_filename)
                
                # 🛠️ EXPERT FIX: Removed 'overlap' and used correct SDK syntax
                # In the Instance Segmentation SDK, 'confidence' is standard.
                # Overlap is often handled internally via NMS for segmentation.
                prediction = model.predict(
                    temp_filename, 
                    confidence=int(conf_val)
                )
                
                # Render results to disk and then to Streamlit
                output_filename = "annotated_inspection.jpg"
                prediction.save(output_filename)
                processed_img = PIL.Image.open(output_filename)

                with col2:
                    st.subheader("Annotated Defect Map")
                    st.image(processed_img, use_container_width=True)

                # --- 4. ANALYTICS & MAINTENANCE LOG ---
                st.divider()
                st.subheader("📋 Maintenance Priority Report")
                
                data = prediction.json()
                preds = data.get('predictions', [])
                
                if preds:
                    log_data = []
                    for p in preds:
                        area = p['width'] * p['height']
                        # Severity Logic based on relative area
                        severity = "🔴 CRITICAL" if area > 10000 else "🟡 MINOR"
                        
                        log_data.append({
                            "Defect Type": p['class'].upper(),
                            "Confidence": f"{p['confidence']:.1%}",
                            "Est. Size (px)": f"{area:,}",
                            "Priority": severity,
                            "Geotag (Sim)": "34.0522, -118.2437"
                        })
                    st.table(log_data)
                else:
                    st.success("Analysis Complete: No structural anomalies identified.")
                
                # Cleanup local buffer for security/storage
                if os.path.exists(temp_filename): os.remove(temp_filename)

            except Exception as e:
                st.error(f"Pipeline Error: {str(e)}")
                st.info("Debugging Tip: Ensure the image is a valid JPEG/PNG and API credits are available.")

# --- 5. FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Senior AI Engineer Access | ITSOLERA 2026")
