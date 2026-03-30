import streamlit as st
from roboflow import Roboflow
import PIL.Image
import cv2
import tempfile
import os
import time

# --- 1. ENTERPRISE UI CONFIGURATION ---
st.set_page_config(
    page_title="ITSOLERA | Autonomous Infrastructure Inspection",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS for Professional Industry Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stSidebar { background-color: #1e293b; color: white; }
    div[data-testid="stExpander"] { border: none; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# API Constants
API_KEY = "KkMa6VA9JRqJvv8X8tSl"
PROJECT_ID = "autonomous_infrastructure_v1"
VERSION_ID = 3

@st.cache_resource
def init_vision_engine():
    try:
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace().project(PROJECT_ID)
        return project.version(VERSION_ID).model
    except Exception as e:
        st.error(f"Critical System Initialization Failure: {e}")
        return None

model = init_vision_engine()

# --- 2. SIDEBAR & KPI DASHBOARD ---
with st.sidebar:
    st.title("🛡️ Inspection Hub")
    st.caption("ITSOLERA Infrastructure AI Division")
    st.divider()
    
    # Application Mode Selector
    app_mode = st.radio("Select Input Source", ["Static Imagery", "Drone Video Feed"])
    
    st.divider()
    conf_thresh = st.slider("Confidence Threshold (%)", 0, 100, 40)
    st.info(f"YOLO11-Segmentation Core Active\nProcessing Latency: Optimized")

# --- 3. MAIN INTERFACE LOGIC ---
st.title("🏗️ Autonomous Infrastructure Inspection")
st.markdown("##### Enterprise Computer Vision Pipeline for Structural Health Monitoring")

if app_mode == "Static Imagery":
    uploaded_img = st.file_uploader("Upload Inspection Image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_img:
        col1, col2 = st.columns(2)
        raw_img = PIL.Image.open(uploaded_img)
        
        with col1:
            st.subheader("Inspection Input")
            st.image(raw_img, use_container_width=True)

        if st.button("🚀 Run Deep Analysis"):
            with st.spinner("AI Engine In-Progress..."):
                raw_img.save("buffer.jpg")
                prediction = model.predict("buffer.jpg", confidence=int(conf_thresh))
                prediction.save("results.jpg")
                
                with col2:
                    st.subheader("Annotated Defect Map")
                    st.image("results.jpg", use_container_width=True)

                # Report Generation
                st.divider()
                st.subheader("📋 Structural Integrity Report")
                data = prediction.json()
                preds = data.get('predictions', [])
                
                if preds:
                    report = []
                    for p in preds:
                        area = p['width'] * p['height']
                        status = "🔴 CRITICAL" if area > 10000 else "🟡 MONITOR"
                        report.append({
                            "Defect Type": p['class'].upper(),
                            "Confidence": f"{p['confidence']:.1%}",
                            "Area (Pixels)": f"{area:,}",
                            "Priority": status
                        })
                    st.table(report)
                else:
                    st.success("Verification Complete: No Anomalies Detected.")

elif app_mode == "Drone Video Feed":
    uploaded_video = st.file_uploader("Upload Drone Flight Footage", type=['mp4', 'avi', 'mov'])
    
    if uploaded_video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        
        vid_cap = cv2.VideoCapture(tfile.name)
        st_frame = st.empty()
        st_progress = st.progress(0)
        
        # Real-time Metrics
        m1, m2, m3 = st.columns(3)
        issue_count = m1.metric("Anomalies Found", "0")
        frame_metric = m2.metric("Frames Processed", "0")
        status_metric = m3.metric("System Status", "Scanning")

        total_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        defect_found_total = 0
        frame_idx = 0

        if st.button("🛰️ Process Video Stream"):
            while vid_cap.isOpened():
                ret, frame = vid_cap.read()
                if not ret: break
                
                # Inference every 15 frames for speed and balance (Industry Standard)
                if frame_idx % 15 == 0:
                    cv2.imwrite("frame_buffer.jpg", frame)
                    prediction = model.predict("frame_buffer.jpg", confidence=int(conf_thresh))
                    prediction.save("frame_result.jpg")
                    
                    # Update metrics
                    current_preds = len(prediction.json().get('predictions', []))
                    defect_found_total += current_preds
                    
                    # Display Result
                    res_img = PIL.Image.open("frame_result.jpg")
                    st_frame.image(res_img, caption=f"Analyzing Frame {frame_idx}/{total_frames}", use_container_width=True)
                    
                    issue_count.metric("Anomalies Found", str(defect_found_total))
                    frame_metric.metric("Frames Processed", str(frame_idx))

                frame_idx += 1
                st_progress.progress(frame_idx / total_frames)
            
            vid_cap.release()
            status_metric.metric("System Status", "Inspection Complete", delta="Ready")
            st.success(f"Video Analysis Complete. Final Report generated for {defect_found_total} total anomalies.")

# --- 4. FOOTER ---
st.divider()
st.caption("ITSOLERA Final Project | Senior AI/ML Engineering Division | © 2026")
