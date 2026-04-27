# 🚦 Traffic Monitoring System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-purple?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![ByteTrack](https://img.shields.io/badge/Tracking-ByteTrack-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Real-time road traffic object detection, tracking and counting system**

*Developed as part of the Computer Vision course — AIMS Senegal — April 2026*

[Demo](#demo) • [Installation](#installation) • [Usage](#usage) • [Structure](#project-structure) • [Results](#results)

</div>

---

## 📋 Table of Contents

- [Description](#description)
- [Features](#features)
- [Demo](#demo)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Model](#model)
- [Detected Classes](#detected-classes)
- [Log Format](#log-format)
- [Results](#results)
- [Authors](#authors)
- [License](#license)

---

## 📌 Description

This project implements a computer vision system dedicated to
**real-time road traffic monitoring**. It is capable of:

- **Detecting** vehicles and pedestrians in traffic videos
- **Tracking** each object uniquely using ByteTrack
- **Counting** the number of unique objects passing through the scene
- **Visualizing** results via an interactive web interface
- **Analyzing** data through a statistical dashboard

This system fits into a Senegalese national context where transport
authorities are looking for reliable and automated methods to understand
how traffic evolves across different regions and times of day.

---

## ✨ Features

- ✅ Real-time detection with fine-tuned **YOLOv11**
- ✅ Persistent tracking with **ByteTrack** (unique ID per object)
- ✅ **Unique object counting** (not just per-frame counting)
- ✅ Support for **local video upload** and **online URL**
- ✅ **Class selection** directly from the interface
- ✅ **Color-coded bounding boxes** per class with ID and confidence score
- ✅ **Visual alert** when no object is detected in the scene
- ✅ **Automatic logs** in CSV and JSON format
- ✅ **Interactive dashboard** with charts and statistics
- ✅ **CSV export** of filtered detection data
- ✅ **Frame-by-frame** processing with timestamps

---

## 🎬 Demo

| Page | Description |
|---|---|
| `localhost:5000/` | Home — video upload and configuration |
| `localhost:5000/live` | Real-time detection and tracking |
| `localhost:5000/dashboard` | Log analysis and visualization |

> 📸 *Screenshots available in the `results/images/` folder*

---

## 🏗️ Architecture

Video (local or URL)
│
▼
┌───────────────┐
│ Pre-processing│  OpenCV — frame-by-frame reading
└───────┬───────┘
│
▼
┌───────────────┐
│   Detection   │  YOLOv11 — object detection
│   (YOLOv11)   │  conf=0.3, iou=0.45
└───────┬───────┘
│
▼
┌───────────────┐
│   Tracking    │  ByteTrack — unique and persistent
│  (ByteTrack)  │  ID per object across frames
└───────┬───────┘
│
▼
┌───────────────┐
│   Counting    │  ObjectCounter — unique object
│               │  counting per class
└───────┬───────┘
│
▼
┌───────────────┐
│   Logging     │  CSV + JSON — timestamps,
│               │  classes, bbox, track IDs
└───────┬───────┘
│
▼
┌───────────────┐
│  Web Interface│  Flask — annotated video stream
│               │  + statistical dashboard
└───────────────┘

---

## ⚙️ Installation

### Prerequisites

- Python **3.10+**
- pip
- GPU recommended (CUDA 11.8+) — also works on CPU

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/your-username/traffic-monitoring-project.git
cd traffic-monitoring-project
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Place the trained model**
```bash
# Copy your fine-tuned model to:
models/yolo/traffic_yolo11_best.pt
```

> If you do not have a fine-tuned model, the pre-trained
> YOLOv11 model will be downloaded automatically.

**5. Launch the application**
```bash
python app.py
```

**6. Open in your browser**
```bash
Running on http://127.0.0.1:5000
Running on http://192.168.1.41:5000
```

---

## 🚀 Usage

### Via the web interface

1. Open `http://192.168.1.41:5000`
2. Choose a video source:
   - **Upload**: select a `.mp4`, `.avi`, or `.mov` file
   - **URL**: paste a link to an online video
3. Select the **classes to detect**
4. Enter a **scene identifier** (e.g. `dakar_intersection`)
5. Click **▶ Start Detection**
6. View real-time results at `/live`
7. Click **⏹ Stop** to save the logs
8. Open the **Dashboard** for analysis


### Available arguments

| Argument | Description | Default |
|---|---|---|
| `--video` | Video path or URL | required |
| `--model` | Path to `.pt` model file | `models/yolo/traffic_yolo11_best.pt` |
| `--classes` | Classes to detect | all |
| `--conf` | Confidence threshold | `0.3` |
| `--iou` | IoU threshold for NMS | `0.45` |
| `--scene-id` | Scene identifier | `scene_01` |
| `--output` | Output folder | `results/` |
| `--no-display` | Disable display window | `False` |

---

## 📁 Project Structure

traffic-monitoring-project/
│
├── 📂 data/
│   ├── raw_videos/          # Original raw videos
│   ├── processed_videos/    # Annotated output videos
│   ├── annotations/         # Annotations for fine-tuning
│   └── schema.json          # Shared log schema
│
├── 📂 models/
│    └── traffic_yolo11_best.pt   # Fine-tuned model
│
├── 📂 src/
│   ├── detector.py          # YOLOv11 detection
│   ├── tracker.py           # ByteTrack tracking
│   ├── counter.py           # Unique object counting
│   ├── logger.py            # Log generation
│ 
├── 📂 web_app/
│   ├── app.py               # Flask application
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html       # Home page
│   │   ├── live.html        # Real-time detection
│   │   └── dashboard.html   # Statistics
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── uploads/         # Uploaded videos
│
├── 📂 notebooks/
│   └── fine_tuning.ipynb    # Kaggle training notebook
│
├── 📂 results/
│   ├── videos/              # Annotated output videos
│   ├── images/              # Screenshots
│   └── plots/               # Exported charts
│
├── 📄 main.py               # Standalone CLI pipeline
├── 📄 requirements.txt      # Python dependencies
├── 📄 README.md             # This file
├── 📄 LICENSE               # MIT License
└── 📄 report.pdf            # Final report
