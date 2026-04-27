import cv2
import os
import pygame
from gtts import gTTS
import subprocess
from datetime import datetime
import time
import shutil
import pygetwindow as gw
import psutil

camera = cv2.VideoCapture(index=0)

dashboard_apps = {"chrome": None, "spotify": None}

# AUDIO (NAME)
def generate_audio(AUDIO_PATH, text, name):
    if not os.path.exists(AUDIO_PATH):
        os.makedirs(AUDIO_PATH)

    tts = gTTS(text=text, lang='id')

    filename = f"{name}.mp3"

    audio_path = os.path.join(AUDIO_PATH, filename)

    tts.save(audio_path)

# AUDIO (DARI FILE)
def import_and_play_audio(file_path):
    if os.path.exists(file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
    else:
        print('Audio tidak ditemukan!')

# Buka Chrome dan Spotify
def open_chrome():
    global dashboard_apps
    
    if dashboard_apps["chrome"] and psutil.pid_exists(dashboard_apps["chrome"]):
        try:
            win = gw.getWindowsWithTitle("Google")[0]
            if win.isMinimized: win.restore()
            win.activate()
            return
        except Exception:
            pass

    url = "https://www.google.com"
    cmd = f'start chrome --app="{url}" --window-size=600,400 --window-position=50,50'
    subprocess.Popen(cmd, shell=True)
    
    time.sleep(1.5)
    
    try:
        jendela_baru = gw.getWindowsWithTitle("Google")[0]
        for p in psutil.process_iter(['pid', 'name']):
            if p.info['name'] == 'chrome.exe':
                dashboard_apps["chrome"] = p.info['pid']
                print(dashboard_apps)
                break
    except Exception:
        pass


def open_spotify():
    global dashboard_apps
    
    if dashboard_apps["spotify"] and psutil.pid_exists(dashboard_apps["spotify"]):
        try:
            win = [w for w in gw.getAllWindows() if 'Spotify' in w.title][0]
            if win.isMinimized: win.restore()
            win.activate()
            return
        except Exception:
            pass

    url = "https://open.spotify.com"
    cmd = f'start chrome --app="{url}" --no-default-browser-check --window-size=600,400 --window-position=100,100'
    subprocess.Popen(cmd, shell=True)
    time.sleep(1.5)
    
    try:
        new_windows = [w for w in gw.getAllWindows() if 'Spotify' in w.title][0]
        for p in psutil.process_iter(['pid', 'name']):
            if p.info['name'] == 'chrome.exe':
                dashboard_apps["spotify"] = p.info['pid']
                print(dashboard_apps)
                break
    except Exception:
        pass

# Deteksi Jam
def get_time():
    time_now = datetime.now()
    time_now = time_now.strftime('%H:%M')
    return time_now

def time_check(time_now):
    AUDIO_PATH = r'D:\programmer\New folder\cache'
    if not os.path.exists(AUDIO_PATH):
        return
    
    filename = 'timenow'
    generate_audio(AUDIO_PATH, time_now, filename)
    time.sleep(0.5)

    return import_and_play_audio(os.path.join(AUDIO_PATH, f'{filename}.mp3'))

# Hapus cache waktu
def delete_cache():
    AUDIO_PATH = r'D:\programmer\New folder\cache'
    if not os.path.exists(AUDIO_PATH):
        return
    shutil.rmtree(AUDIO_PATH)
    os.makedirs(AUDIO_PATH)

# Kill spotify
def kill_spotify_web_tab():
    process_name = "chrome.exe"
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if len(processes) > 1:
        processes.sort(key=lambda x: x['create_time'], reverse=True)
        
        latest_pid = processes[0]['pid']
        
        try:
            p = psutil.Process(latest_pid)
            p.terminate() 
        except:
            print("Gagal")

# Kill Chrome
def kill_latest_process(process_name):
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if len(processes) > 1:
        processes.sort(key=lambda x: x['create_time'], reverse=True)
        
        latest_pid = processes[0]['pid']
        print(f"Mateni {process_name} sing paling anyar (PID: {latest_pid})")
        
        try:
            p = psutil.Process(latest_pid)
            p.terminate()
        except:
            print("Gagal")