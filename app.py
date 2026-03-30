import streamlit as st
from roboflow import Roboflow
import PIL.Image
import cv2
import tempfile
import os
import time
import io
import requests

# --- 1. INDUSTRIAL THEME & HIGH-CONTRAST CSS ---
st.set_page_config(
    page_title="Infrastructure Intelligence System",
    page_icon="🏗️",
    layout="wide"
)

st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* TABLE FIX: High Contrast for Data Visibility */
    .stTable { 
        background-color: #161b22 !important; 
        border: 1px solid #30363d !important;
        color: #f0f6fc !important;
    }
    th { background-color: #21262d !important; color: #58a6ff !important; font-family: monospace; }
    td { border-bottom: 1px solid #30363d !important; font-size: 14px; }

    /* Button & Metric UI */
    .stButton>button { 
        background-color: #238636; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3em;
    }
    .stButton>button:hover { background-color: #2ea043; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE INITIALIZATION ---
API_KEY = "KkMa6VA9JRqJvv8X8tSl"
PROJECT_ID = "autonomous_infrastructure_v1"
VERSION_ID = 3

@st.cache_resource
def load_vision_engine():
    try:
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace().project(PROJECT_ID)
        return project.version(VERSION_ID).model
    except Exception as e:
        st.error(f"Engine Load Failure: {e}")
        return None

model = load_vision_engine()

def safe_predict(image_path, confidence):
    """Expert Wrapper: Handles HTTP errors with retries and resizing."""
    try:
        # Resize image if too large (Optimization for Cloud API)
        img = PIL.Image.open(image_path)
        if max(img.size) > 1280:
            img.thumbnail((1280, 1280))
            img.save(image_path, quality=85)
            
        return model.predict(image_path, confidence=int(confidence))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            st.warning("API Rate Limit Reached. Retrying in 2s...")
            time.sleep(2)
            return model.predict(image_path, confidence=int(confidence))
        else:
            raise e

# --- 3. DUAL-MODE INTERFACE ---
with st.sidebar:
    st.header("CORE SETTINGS")
    st.divider()
    inspect_mode = st.selectbox("ANALYSIS MODE", ["IMAGE DIAGNOSTIC", "VIDEO STREAMING"])
    conf_level = st.slider("CONFIDENCE (%)", 10, 100, 45)
    
    if inspect_mode == "VIDEO STREAMING":
        sampling_rate = st.select_slider("FRAME SAMPLING", options=[1, 10, 20, 30], value=10)
    st.divider()
    st.caption("ITSOLERA INFRASTRUCTURE OS v4.0")

st.title("🏗️ Autonomous Infrastructure Inspection")
st.write("STATUS: OPERATIONAL | ARCHITECTURE: YOLO11-SEGMENTATION")

if inspect_mode == "IMAGE DIAGNOSTIC":
    file = st.file_uploader("SOURCE FILE", type=['jpg', 'jpeg', 'png'])
    
    if file:
        col_in, col_out = st.columns(2)
        raw_img = PIL.Image.open(file)
        
        with col_in:
            st.subheader("Inspection Input")
            st.image(raw_img, use_container_width=True)

        if st.button("RUN SYSTEM ANALYSIS"):
            with st.spinner("AI INFERENCE IN PROGRESS..."):
                raw_img.save("static_buffer.jpg")
                try:
                    prediction = safe_predict("static_buffer.jpg", conf_level)
                    prediction.save("static_result.jpg")
                    
                    with col_out:
                        st.subheader("Anomaly Mapping")
                        st.image("static_result.jpg", use_container_width=True)

                    # Maintenance Report
                    st.divider()
                    st.subheader("📋 Maintenance Priority Log")
                    preds = prediction.json().get('predictions', [])
                    if preds:
                        log_table = []
                        for p in preds:
                            area = p['width'] * p['height']
                            severity = "🔴 CRITICAL" if area > 12000 else "🟡 MONITOR"
                            log_table.append({
                                "DEFECT": p['class'].upper(),
                                "CONFIDENCE": f"{p['confidence']:.1%}",
                                "AREA (PX)": f"{area:,}",
                                "PRIORITY": severity
                            })
                        st.table(log_table)
                    else:
                        st.success("INTEGRITY VERIFIED: NO DEFECTS FOUND.")
                except Exception as e:
                    st.error(f"Inference Error: {e}")

elif inspect_mode == "VIDEO STREAMING":
    video_file = st.file_uploader("DRONE FOOTAGE", type=['mp4', 'avi', 'mov'])
    
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        display_handle = st.empty()
        
        k1, k2, k3 = st.columns(3)
        total_defects = k1.metric("DEFECTS", "0")
        processed_frames = k2.metric("FRAMES", "0")
        latency_metric = k3.metric("LATENCY", "0ms")

        if st.button("EXECUTE STREAM INSPECTION"):
            found_count = 0
            frame_ptr = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                if frame_ptr % sampling_rate == 0:
                    start = time.time()
                    cv2.imwrite("video_buffer.jpg", frame)
                    
                    try:
                        prediction = safe_predict("video_buffer.jpg", conf_level)
                        prediction.save("video_out.jpg")
                        
                        found_count += len(prediction.json().get('predictions', []))
                        latency = int((time.time() - start) * 1000)
                        
                        display_handle.image("video_out.jpg", use_container_width=True)
                        total_defects.metric("DEFECTS", str(found_count))
                        processed_frames.metric("FRAMES", str(frame_ptr))
                        latency_metric.metric("LATENCY", f"{latency}ms")
                    except:
                        continue

                frame_ptr += 1
            cap.release()
            st.success("STREAM ANALYSIS COMPLETE.")

st.divider()
st.caption("CONFIDENTIAL | INTERNAL MAINTENANCE ACCESS | © 2026")
