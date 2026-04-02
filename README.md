# Tapo Vision NVR

A lightweight, resilient Network Video Recorder (NVR) built with Python for TP-Link Tapo cameras. Designed to run on low-resource hardware (legacy PCs) using smart motion detection and efficient disk management.

## 🚀 Key features

- **Dual-stream logic**: Analyzes a low-res (360p) stream for motion detection while recording from high-res (1080p).
- **Smart recording**: Triggered only by motion, with a configurable cooldown period.
- **Circular buffer**: Automatically purges oldest files when a disk limit (e.g. 90 GB) is reached.
- **Auto-recovery**: Monitors RTSP health and reconnects after signal drops.
- **Zero re-encoding**: Uses FFmpeg stream copy to avoid heavy CPU use.

## 🛠️ Tech stack

- **Python 3.8+**
- **OpenCV**: Image processing and motion detection.
- **FFmpeg**: High-performance video muxing.
- **python-dotenv**: Environment variable management.

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/JoaoPedroCavalcanti/tapo-vision-nvr.git
   cd tapo-vision-nvr
   ```

2. **Create a virtual environment**

   **Windows**

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

   **macOS / Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install opencv-python python-dotenv
   ```

4. **Install FFmpeg**  
   Ensure `ffmpeg` is installed and available on your system `PATH`.

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
TAPO_USER=your_camera_user
TAPO_PASS=your_camera_password
TAPO_IP=192.168.x.x

# NVR settings
OUTPUT_DIR=recordings
LIMIT_GB=90
COOLDOWN_SECONDS=60
MIN_AREA=5000
```

## 🏃 Running

Start the monitor manually:

```bash
python monitor.py
```

On Windows, use `run_nvr.bat` for background execution (activates `.venv` and runs `pythonw monitor.py`).

## ✅ Pre-commit checklist

1. **Entry script**: Treat `monitor.py` as the canonical entry point; rename any legacy file (e.g. `camera_sala.py`) before `git add` if it still exists in your tree.
2. **Environment defaults**: Keep `os.getenv("OUTPUT_DIR", "recordings")` consistent with this README.
3. **Logs**: If log volume grows, consider moving `nvr_status.log` under a dedicated `logs/` directory.

## 🛡️ License

MIT
