import os
from dotenv import load_dotenv
import cv2
import subprocess
import time
import threading
import logging

load_dotenv()

# --- CONFIGURAÇÕES ---
USER = os.getenv("TAPO_USER")
PASS = os.getenv("TAPO_PASS")
IP = os.getenv("TAPO_IP")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "recordings")
MIN_AREA = int(os.getenv("MIN_AREA", 5000))
LIMIT_MB = int(os.getenv("LIMIT_GB", 90)) * 1024
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 60))    

URL_DETECCAO = f"rtsp://{USER}:{PASS}@{IP}:554/stream2"
URL_GRAVACAO = f"rtsp://{USER}:{PASS}@{IP}:554/stream1"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("nvr_status.log"), logging.StreamHandler()]
)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class TapoNVR:
    def __init__(self):
        self.is_recording = False
        self.last_motion_time = 0
        self.ffmpeg_process = None

    def get_folder_size_mb(self):
        total = 0
        try:
            for f in os.listdir(OUTPUT_DIR):
                fp = os.path.join(OUTPUT_DIR, f)
                if os.path.isfile(fp): total += os.path.getsize(fp)
        except Exception: return 0
        return total / (1024 * 1024)

    def janitor_loop(self):
        while True:
            try:
                size = self.get_folder_size_mb()
                if size > LIMIT_MB:
                    files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith('.mkv')]
                    files.sort(key=os.path.getmtime)
                    if len(files) > 2:
                        file_to_del = files[0]
                        logging.info(f"Expurgo: {os.path.basename(file_to_del)} | Total: {size/1024:.2f}GB")
                        os.remove(file_to_del)
            except Exception as e:
                logging.error(f"Erro no Zelador: {e}")
            time.sleep(10)

    def start_ffmpeg(self):
        filename_pattern = os.path.join(OUTPUT_DIR, "tapo_%Y%m%d_%H%M%S.mkv")
        cmd = [
            'ffmpeg', '-hide_banner', '-loglevel', 'error',
            '-i', URL_GRAVACAO,
            '-c', 'copy', '-map', '0',
            '-f', 'segment', '-segment_time', '60',
            '-reset_timestamps', '1', '-strftime', '1',
            filename_pattern
        ]
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def stop_ffmpeg(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5) # Aguarda o encerramento gracioso
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill() # Força se travar
            self.ffmpeg_process = None

    def run(self):
        threading.Thread(target=self.janitor_loop, daemon=True).start()
        logging.info("NVR Iniciado. Monitorando...")

        while True:
            cap = cv2.VideoCapture(URL_DETECCAO)
            avg = None

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logging.warning("Sinal perdido. Reconectando...")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if avg is None:
                    avg = gray.copy().astype("float")
                    continue

                # AJUSTE: Cast explícito para float32 para evitar erro no accumulateWeighted
                cv2.accumulateWeighted(gray.astype("float"), avg, 0.02)
                
                frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
                thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                motion_detected = any(cv2.contourArea(c) > MIN_AREA for c in cnts)
                now = time.time()

                if motion_detected:
                    self.last_motion_time = now
                    if not self.is_recording:
                        logging.info("MOVIMENTO! Iniciando gravação.")
                        self.is_recording = True
                        self.ffmpeg_process = self.start_ffmpeg()

                if self.is_recording and (now - self.last_motion_time > COOLDOWN_SECONDS):
                    logging.info("Cooldown atingido. Finalizando arquivos.")
                    self.is_recording = False
                    self.stop_ffmpeg()

                time.sleep(0.05)

            cap.release()
            self.stop_ffmpeg() # Garante que para de gravar se a conexão cair
            time.sleep(5)

if __name__ == "__main__":
    nvr = TapoNVR()
    try:
        nvr.run()
    except KeyboardInterrupt:
        logging.info("Desligamento manual.")
        nvr.stop_ffmpeg()