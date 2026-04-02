# Tapo Vision NVR

A lightweight, resilient Network Video Recorder (NVR) built with Python for TP-Link Tapo cameras. Designed to run on low-resource hardware (legacy PCs) using smart motion detection and efficient disk management.

## 🚀 Key Features

- **Dual-Stream Logic**: Analyzes low-res (360p) stream for motion detection while recording in high-res (1080p).
- **Smart Recording**: Triggered only by motion with a configurable cooldown period.
- **Circular Buffer**: Automatically purges oldest files when disk limit (e.g., 90GB) is reached.
- **Auto-Recovery**: Monitors RTSP connection health and reconnects automatically on signal drops.
- **Zero Re-encoding**: Uses FFmpeg stream copy to save video without hitting the CPU.

## 🛠️ Tech Stack

- **Python 3.8+**
- **OpenCV**: Image processing and motion detection.
- **FFmpeg**: High-performance video muxing.
- **Python-Dotenv**: Environment variable management.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/tapo-vision-nvr.git](https://github.com/your-username/tapo-vision-nvr.git)
   cd tapo-vision-nvr