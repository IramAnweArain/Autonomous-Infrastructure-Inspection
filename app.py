import streamlit as st
from roboflow import Roboflow
import PIL.Image
import cv2
import tempfile
import os
import time
import io

# --- 1. INDUSTRIAL THEME & HIGH-CONTRAST CSS ---
st.set_page_config(
    page_title="Infrastructure Intelligence System",
    layout="wide"
)

st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #161b22; 
        border-right: 1px solid #30363d;
    }
    
    /* HIGH-CONTRAST TABLE FIX */
    /* This forces the table to be dark with light text regardless of mode */
    .stTable { 
        background-color: #161b22 !important; 
        color: #f0f6fc !important; 
        border: 1px solid #30363d !important;
    }
    th { background-color: #0d1117 !important; color: #58a6ff !important; text-transform: uppercase; }
    td { border-bottom: 1px solid #30363d !important; color: #f0f6fc !important; }

    /* Button Styling */
    .stButton>button { 
        background-color: #238636; 
        color: white; 
        border-radius: 6px; 
        border: 1px solid rgba(240,246,242,0.1);
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2ea043; border-color: #8b949e; }

    /* Metric Card Styling */
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-family: monospace; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
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
    st.header("SYSTEM CONTROL")
    st.write("---")
    inspect_mode = st.selectbox("INSPECTION TARGET", ["STATIC FRAME ANALYSIS", "DYNAMIC VIDEO STREAM"])
    st.write("---")
    conf_level = st.slider("DETECTION SENSITIVITY (%)", 0, 100, 45)
    
    st.write("VIDEO OPTIMIZATION")
    sampling_rate = st.select_slider(
        "SAMPLING FREQUENCY",
        options=[1, 5, 15, 30, 60],
        value=15
    )
    st.write("---")
    st.caption("ITSOLERA ENGINEERING v3.2")

# --- 3. CORE ANALYTICS ENGINE ---
st.title("AUTONOMOUS INFRASTRUCTURE INSPECTION")
st.write("CORE STATUS: ACTIVE | ENGINE: YOLO11-SEGMENTATION")

if inspect_mode == "STATIC FRAME ANALYSIS":
    file = st.file_uploader("UPLOAD SOURCE IMAGE", type=['jpg', 'jpeg', 'png'])
    
    if file:
        col_in, col_out = st.columns(2)
        input_img = PIL.Image.open(file)
        
        with col_in:
            st.write("INPUT STREAM")
            st.image(input_img, use_container_width=True)

        if st.button("EXECUTE ANALYSIS"):
            with st.spinner("RUNNING INFERENCE..."):
                # Save to memory buffer for stability
                buf = io.BytesIO()
                input_img.save(buf, format="JPEG")
                input_img.save("static_buffer.jpg")
                
                prediction = model.predict("static_buffer.jpg", confidence=int(conf_level))
                prediction.save("static_result.jpg")
                
                with col_out:
                    st.write("ANOMALY MAPPING")
                    st.image("static_result.jpg", use_container_width=True)

                st.write("---")
                st.subheader("MAINTENANCE LOG")
                preds = prediction.json().get('predictions', [])
                if preds:
                    log = []
                    for p in preds:
                        size = p['width'] * p['height']
                        prio = "URGENT" if size > 12000 else "MONITOR"
                        log.append({
                            "TYPE": p['class'].upper(),
                            "CONFIDENCE": f"{p['confidence']:.1%}",
                            "AREA (PX)": f"{size:,}",
                            "PRIORITY": prio
                        })
                    st.table(log) # This table is now high-contrast via CSS
                else:
                    st.info("NO ANOMALIES IDENTIFIED.")

elif inspect_mode == "DYNAMIC VIDEO STREAM":
    video_file = st.file_uploader("UPLOAD DRONE FOOTAGE", type=['mp4', 'avi', 'mov'])
    
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        display_handle = st.empty()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        total_defects = kpi1.metric("DEFECTS FOUND", "0")
        processed_frames = kpi2.metric("FRAMES PROCESSED", "0")
        latency_metric = kpi3.metric("ENGINE LATENCY", "0ms")

        if st.button("START STREAM INSPECTION"):
            found_count = 0
            frame_ptr = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                if frame_ptr % sampling_rate == 0:
                    start_time = time.time()
                    cv2.imwrite("video_buffer.jpg", frame)
                    
                    prediction = model.predict("video_buffer.jpg", confidence=int(conf_level))
                    prediction.save("video_out.jpg")
                    
                    # Telemetry Update
                    current_batch = len(prediction.json().get('predictions', []))
                    found_count += current_batch
                    end_time = time.time()
                    
                    # Refresh UI
                    display_handle.image("video_out.jpg", caption=f"ANALYZING FRAME: {frame_ptr}", use_container_width=True)
                    total_defects.metric("DEFECTS FOUND", str(found_count))
                    processed_frames.metric("PROCESSED FRAMES", str(frame_ptr))
                    latency_metric.metric("ENGINE LATENCY", f"{int((end_time - start_time)*1000)}ms")

                frame_ptr += 1
            
            cap.release()
            st.success("STREAM ANALYSIS FINALIZED.")

st.write("---")
st.caption("ITSOLERA INFRASTRUCTURE OS | CORE v3.2 | NOVELTY-INTEGRATION READY")
