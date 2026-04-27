import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision import HandLandmarksConnections as hand_connections
import cv2
import cvzone
from modules import dashboard_apps, get_time, time_check, open_chrome, open_spotify, generate_audio, import_and_play_audio, kill_latest_process, kill_spotify_web_tab
from pc_info import get_computer_info
import threading
import time
import os
import psutil

# Setting awal dan inisialisasi
ref = "hand_landmarker.task"
base_options = python.BaseOptions(model_asset_path=ref)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.3,
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)
camera = cv2.VideoCapture(index=0)
thread_time = None
thread_info = None
info_list = []

AUDIO_PATH = r'D:\programmer\New folder\audio\public\menu'

# Tutup Kamera
def close():
    detector.close()
    camera.release()
    cv2.destroyAllWindows()
    exit()

# Threading info PC
def thread_info_pc():
    global info_list
    global start_time
    disk_usage, ram_usage, total_disk, space, gpu, cpu_name, core = get_computer_info()
    info_list = [
        str(f"CPU : {cpu_name} ({core} Cores)"),
        str(f"GPU : {gpu}"),
        str(f"Disk Usage : {disk_usage}"),
        str(f"Space : {space}"),
        str(f"RAM Usage : {ram_usage}")
    ]
    start_time = time.time()

# Threading audio
def audio(filename, text):
    if not os.path.exists(os.path.join(AUDIO_PATH, filename)):
        generate_audio(AUDIO_PATH, text, filename)
    import_and_play_audio(os.path.join(AUDIO_PATH, f"{filename}.mp3"))

# Hapus Audio (Cache)
def delete_audio(filename):
    if not os.path.exists(AUDIO_PATH):
        return
    os.remove(os.path.join(AUDIO_PATH, filename))

def sv_dashboard(name):
    global thread_time
    global thread_info
    global info_list
    global start_time
    processing_music = False
    processing_browser = False
    popup_text = False
    start_time = None
    show_info = False
    play_audio = False

    # filename = "welcome"
    # text = f"Selamat datang, {name}"
    # thread_audio = threading.Thread(target=audio, args=(filename, text))
    # thread_audio.daemon = True
    # thread_audio.start()

    while True:
        # Open cam
        ret, default_frame = camera.read()
        if not ret:
            break
        
        # Inisialisai frame
        frame = cv2.flip(default_frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Gambar dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (400, 370), (600, 420), (255, 0, 255), cv2.FILLED)
        cv2.rectangle(overlay, (400, 295), (600, 345), (255, 0, 255), cv2.FILLED)
        cv2.rectangle(overlay, (400, 220), (600, 270), (255, 0, 255), cv2.FILLED)
        cv2.rectangle(overlay, (400, 145), (600, 195), (255, 0, 255), cv2.FILLED)
        cv2.rectangle(overlay, (400, 70), (600, 120), (255, 0, 255), cv2.FILLED)

        cvzone.putTextRect(overlay, "CEK JAM", (410, 105), scale=1, thickness=1, offset=5, colorR=None)
        cvzone.putTextRect(overlay, "INFO PC", (410, 180), scale=1, thickness=1, offset=5, colorR=None)
        cvzone.putTextRect(overlay, "BROWSER", (410, 255), scale=1, thickness=1, offset=5, colorR=None)
        cvzone.putTextRect(overlay, "MUSIC", (410, 330), scale=1, thickness=1, offset=5, colorR=None)
        cvzone.putTextRect(overlay, "EXIT", (410, 405), scale=1, thickness=1, offset=5, colorR=None)

        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # Detect tangan
        result = detector.detect(mp_image)
        
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                mp_drawing.draw_landmarks(
                    image = frame, 
                    landmark_list = hand_landmarks, 
                    connections=hand_connections.HAND_CONNECTIONS, 
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 0), 
                    thickness=2, 
                    circle_radius=4))
        
        # Logika ganti halaman
                h, w, _ = frame.shape
                x8 = int(hand_landmarks[8].x * w)
                y8 = int(hand_landmarks[8].y * h)

                # Cek Jam
                if 410 < x8 < 600 and 70 < y8 < 120:
                    if thread_time is None or not thread_time.is_alive():
                        time_now = get_time()

                        thread_time = threading.Thread(target=time_check, args=[time_now])
                        thread_time.daemon = True
                        popup_text = True
                        start_popup = time.time()
                        thread_time.start()

                # Info PC
                elif 410 < x8 < 600 and 145 < y8 < 195:
                    if thread_info is None or not thread_info.is_alive():
                        if not play_audio:
                            filename = "info_pc"
                            text = "Menampilkan info PC"
                            thread_audio = threading.Thread(target=audio, args=(filename, text))
                            thread_audio.daemon = True
                            thread_audio.start()
                            play_audio = True
                        
                        thread_info = threading.Thread(target=thread_info_pc)
                        thread_info.daemon = True
                        thread_info.start()

                        if start_time is None:
                            show_info = True
                            start_time = time.time()

                # Browser
                elif 410 < x8 < 600 and 220 < y8 < 270:
                    if not dashboard_apps["chrome"] or not psutil.pid_exists(dashboard_apps["chrome"]):
                        if not processing_browser:
                            processing_browser = True
                            if not play_audio:
                                filename = "open_chrome"
                                text = "Membuka Chrome"
                                thread_audio = threading.Thread(target=audio, args=(filename, text))
                                thread_audio.daemon = True
                                thread_audio.start()
                                play_audio = True

                            thread = threading.Thread(target=open_chrome)
                            thread.daemon = True
                            thread.start()

                # Spotify
                elif 410 < x8 < 600 and 295 < y8 < 345:
                    if not dashboard_apps["spotify"] or not psutil.pid_exists(dashboard_apps["spotify"]):
                        if not processing_music:
                            processing_music = True
                            if not play_audio:
                                filename = "open_spotify"
                                text = "Membuka Spotify"
                                thread_audio = threading.Thread(target=audio, args=(filename, text))
                                thread_audio.daemon = True
                                thread_audio.start()
                                play_audio = True
                            
                            thread = threading.Thread(target=open_spotify)
                            thread.daemon = True
                            thread.start()

                # Exit
                elif 410 < x8 < 600 and 370 < y8 < 420:
                    close()
                    return

                if not (410 < x8 < 600 and 220 < y8 < 270) or not result.hand_landmarks:
                    processing_browser = False
                
                if not (410 < x8 < 600 and 295 < y8 < 345) or not result.hand_landmarks:
                    processing_music = False

                if not (410 < x8 < 600 and 145 < y8 < 195) and not (410 < x8 < 600 and 220 < y8 < 270) and not (410 < x8 < 600 and 295 < y8 < 345):
                    play_audio = False

        # Output text info
        if show_info and start_time is not None:
            elapsed = time.time() - start_time
            
            if elapsed < 5:
                y_offset = 100
                for line in info_list:
                    cv2.putText(frame, line, (50,y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    y_offset += 40
            else: 
                start_time = None
                info_list = []
                show_info = False
        
        if popup_text:
            if time.time() - start_popup <= 2:
                cvzone.putTextRect(frame, time_now, (50,50), scale=1, thickness=1, offset=5, colorR=None)
            else:
                popup_text = False

        cv2.imshow("Smart Virtual Dashboard", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    close()
    # delete_audio(f"{filename}.mp3")
    return

sv_dashboard(name='')