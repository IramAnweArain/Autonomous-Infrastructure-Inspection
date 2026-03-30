# 🏗️ Autonomous Infrastructure Inspection
### **Enterprise AI Pipeline for Structural Health Monitoring**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://autonomous-infrastructure-inspection-czhakwfenlkaodzhelhmgp.streamlit.app/)

## 🌐 Project Overview
This repository contains a production-ready **Computer Vision Pipeline** designed to automate the hazardous and labor-intensive process of infrastructure auditing. By utilizing **YOLO11-Instance Segmentation**, the system identifies and segments critical defects.

---

## 🧪 Data Engineering & Preprocessing
To achieve high recall on thin structural fractures, a rigorous **Data Augmentation & Engineering** strategy was implemented:

* **Spatial Tiling (2x2):** High-resolution survey images were tiled to preserve the aspect ratio of thin cracks, preventing feature loss during standard downsampling.
* **Class Balancing:** Applied **3x Oversampling** to the "Pothole" class to mitigate dataset skewness.
* **Augmentation Matrix:**
    * **Geometric:** $\pm15^\circ$ Rotation and Shearing to simulate non-orthogonal drone angles.
    * **Photometric:** 25% Salt-and-Pepper noise and Blur injection for robustness against motion blur.
    * **Color-Space:** Grayscale conversion (15%) to force the model to prioritize **Textural Deformities**.

---

## 📊 Model Performance & Metrics
The model was trained for **150 Epochs** using the **AdamW Optimizer**.

| Defect Class | mAP@50 | Recall | Strategic Engineering Note |
| :--- | :--- | :--- | :--- |
| **Corrosion** | **99.0%** | 98.4% | Near-perfect identification of oxidative decay. |
| **Pothole** | **44.0%** | 62.0% | Optimized for varied asphalt textures via oversampling. |
| **Crack** | **16.0%** | 53.8% | High sensitivity to structural fractures. |

---

## 🚀 System Integration Features
This project satisfies the **ITSOLERA v4.0** requirements for a "Complete Working System":

1. **Dual-Mode Diagnostic Suite:**
    * **Static Mode:** Precision analysis for high-resolution engineering stills.
    * **Video Mode:** Dynamic processing of drone MP4/AVI footage using an **Optimized Sampling Engine** (1 frame every 0.5s).
2. **Automated Maintenance Priority (AMP):**
    * A custom post-inference algorithm calculates the **Defect Magnitude**.
    * **Critical Alert:** Triggered when the segmentation mask area exceeds **12,000 pixels**.
3. **Production Resilience:**
    * **Theme-Stability:** Custom CSS injection forces a **High-Contrast Industrial UI**.
    * **Error Handling:** Implemented `safe_predict` wrappers to handle API rate-limits and automatic resizing of 4K drone imagery.

---

## 📂 Repository Structure
* `app.py` — Main Streamlit Production Application
* `requirements.txt` — Production dependencies
* `README.md` — Project Documentation

---

## 👤 Author
**Iram Anwer**
*AI/ML Enthusiast *
