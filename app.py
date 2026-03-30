import streamlit as st
from roboflow import Roboflow
import PIL.Image
import cv2
import tempfile
import os
import time

# --- 1. INDUSTRIAL THEME CONFIGURATION ---
# Neutral color palette to avoid Light/Dark mode UI clashing
st.set_page_config(
    page_title="Infrastructure Intelligence System",
    layout="wide"
)

st.markdown("""
    <style>
    /* Force Industrial Neutral Colors */
    .stApp { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { 
        background-color: #1a202c; 
        color: #ffffff;
        border-right: 1px solid #2d3748;
    }
    h1, h2, h3 { color: #1a202c !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { 
        background-color: #2b6cb0; 
        color: white; 
        border-radius: 2px; 
        width: 100%;
        border: none;
        font-weight: 600;
    }
    .stTable { background-color: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    /* Metric styling */
    [data-testid="stMetricValue"] { color: #2b6cb0 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# API Constants
API_KEY = "KkMa6VA9JRqJvv8X8tSl"
PROJECT_ID = "autonomous_infrastructure_v1"
VERSION_ID = 3

@st.cache_resource
def load_vision_engine():
    try:
        rf = Roboflow(api_key=API_KEY)
        project = rf.workspace().project(PROJECT_ID)
        return project.version(VERSION_ID).model
    except Exception:
        return None

model = load_vision_engine()

# --- 2. NAVIGATION HUB ---
with st.sidebar:
    st.title("SYSTEM CONTROL")
    st.write("---")
    inspect_mode = st.selectbox("INSPECTION TARGET", ["Static Frame Analysis", "Dynamic Video Stream"])
    st.write("---")
    
    # Precision Controls
    conf_level = st.slider("DETECTION SENSITIVITY (%)", 0, 100, 45)
    
    # Sampling Control for Speed
    st.write("VIDEO OPTIMIZATION")
    sampling_rate = st.select_slider(
        "PROCESSING FREQUENCY",
        options=[1, 5, 15, 30, 60],
        value=15,
        help="Higher values increase speed by skipping frames."
    )
    
    st.write("---")
    st.caption("ITSOLERA ENGINEERING DIVISION | 2026")

# --- 3. CORE ANALYTICS ENGINE ---
st.title("AUTONOMOUS INFRASTRUCTURE INSPECTION")
st.write("SYSTEM STATUS: ONLINE | CORE: YOLO11-SEGMENTATION")

if inspect_mode == "Static Frame Analysis":
    file = st.file_uploader("UPLOAD SOURCE IMAGE", type=['jpg', 'jpeg', 'png'])
    
    if file:
        col_in, col_out = st.columns(2)
        input_img = PIL.Image.open(file)
        
        with col_in:
            st.write("INPUT STREAM")
            st.image(input_img, use_container_width=True)

        if st.button("EXECUTE ANALYSIS"):
            with st.spinner("PROCESSING..."):
                input_img.save("static_buffer.jpg")
                prediction = model.predict("static_buffer.jpg", confidence=int(conf_level))
                prediction.save("static_result.jpg")
                
                with col_out:
                    st.write("ANOMALY MAPPING")
                    st.image("static_result.jpg", use_container_width=True)

                # Formal Reporting
                st.write("---")
                st.subheader("MAINTENANCE LOG")
                preds = prediction.json().get('predictions', [])
                if preds:
                    log = []
                    for p in preds:
                        size = p['width'] * p['height']
                        prio = "URGENT" if size > 12000 else "MONITOR"
                        log.append({
                            "CLASSIFICATION": p['class'].upper(),
                            "CONFIDENCE": f"{p['confidence']:.2%}",
                            "SPATIAL AREA": f"{size:,} px",
                            "MAINTENANCE PRIORITY": prio
                        })
                    st.table(log)
                else:
                    st.success("NO STRUCTURAL DEFECTS IDENTIFIED.")

elif inspect_mode == "Dynamic Video Stream":
    video_file = st.file_uploader("UPLOAD DRONE FOOTAGE", type=['mp4', 'avi', 'mov'])
    
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        display_handle = st.empty()
        
        # Real-time Telemetry
        kpi1, kpi2, kpi3 = st.columns(3)
        total_defects = kpi1.metric("DEFECTS FOUND", "0")
        processed_frames = kpi2.metric("PROCESSED FRAMES", "0")
        latency_metric = kpi3.metric("ENGINE LATENCY", "0ms")

        if st.button("START STREAM INSPECTION"):
            found_count = 0
            frame_ptr = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                # Logic to skip frames based on sampling rate for speed
                if frame_ptr % sampling_rate == 0:
                    start_time = time.time()
                    
                    # Convert BGR to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    cv2.imwrite("video_buffer.jpg", frame)
                    
                    prediction = model.predict("video_buffer.jpg", confidence=int(conf_level))
                    prediction.save("video_out.jpg")
                    
                    # Update Metrics
                    current_batch = len(prediction.json().get('predictions', []))
                    found_count += current_batch
                    end_time = time.time()
                    
                    # Refresh UI
                    display_handle.image("video_out.jpg", caption=f"FRAME ID: {frame_ptr}", use_container_width=True)
                    total_defects.metric("DEFECTS FOUND", str(found_count))
                    processed_frames.metric("PROCESSED FRAMES", str(frame_ptr))
                    latency_metric.metric("ENGINE LATENCY", f"{int((end_time - start_time)*1000)}ms")

                frame_ptr += 1
            
            cap.release()
            st.success("STREAM ANALYSIS FINALIZED.")

# --- 4. DATA INTEGRITY FOOTER ---
st.write("---")
st.caption("CONFIDENTIAL: INTERNAL INSPECTION USE ONLY | ITSOLERA CORE v3.1")
