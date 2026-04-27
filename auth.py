import os
import sys
from modules import import_and_play_audio
from smart_virtual_dashboard import sv_dashboard

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import cv2
import customtkinter as ctk
import time
import mysql.connector
from deepface import DeepFace

face_ref = cv2.CascadeClassifier("face_ref.xml")
camera = cv2.VideoCapture(index=0)
REG_IMG = ""
AUDIO_PATH = r'D:\programmer\New folder\audio\public\auth'
FOLDER = "pict_data"

# INISIALISASI DB
def db_config():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='cam_py'
    )
    return db

# FRAME
def process_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_ref.detectMultiScale(gray_frame, scaleFactor=1.1)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 225), (3))
    return faces

# TUTUP KAMERA
def close():
    camera.release()
    cv2.destroyAllWindows()
    exit()

# REGISTER
def register():
    name = None
    def input_register():
        nonlocal name
        name = input_name.get().capitalize()
        if name:
            app.destroy()

    import_and_play_audio(os.path.join(AUDIO_PATH, "masukkan_nama_anda.mp3"))
    time.sleep(1)
    sys.stdin.flush()

    app = ctk.CTk()
    app.title("SVD - REGISTER")
    app.geometry("400x250")
    app.configure(bg='#1e1e26')
    
    label_title = ctk.CTkLabel(
        app, text="VERIFIKASI IDENTITAS",  
        font=("Helvetica", 14, "bold")
    )
    label_title.pack(pady=(30, 10))

    input_name = ctk.CTkEntry(
        app, font=("Helvetica", 12)
    )
    input_name.pack(pady=10, padx=50, fill="x")
    input_name.focus_set()

    btn_submit = ctk.CTkButton(
        app, text="KONFIRMASI", 
        command=input_register,
        font=("Helvetica", 10, "bold"),
    )
    btn_submit.pack(pady=20)

    app.mainloop()

    time.sleep(0.5)

    start_time = None
    last_status = None

    db = db_config()
    cursor = db.cursor()

    while True:
        result, default_frame = camera.read()
        if not result:
            break

        frame = cv2.flip(default_frame, 1)
        faces = process_frame(frame)
        
        if len(faces) > 0:
            if start_time is None:
                start_time = time.time()

            if last_status != "ada":
                import_and_play_audio(os.path.join(AUDIO_PATH, "wajah_terdeteksi.mp3"))
                last_status = "ada"
            
            elapsed_time = time.time() - start_time
            countdown = 3 - int(elapsed_time)

            if countdown > 0:
                cv2.putText(frame, f"Simpan dalam: {countdown}s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                (x, y, w, h) = faces[0]
                face_crop = frame[y:y+h, x:x+w]
                face_resized = cv2.resize(face_crop, (200, 200), interpolation=cv2.INTER_AREA)
                img_path = os.path.join(FOLDER, f"{name}.png")
                cv2.imwrite(img_path, face_resized)
                print(f"Foto berhasil disimpan di: {img_path}")
                import_and_play_audio(os.path.join(AUDIO_PATH, "foto_berhasil_disimpan.mp3"))
                time.sleep(1)
                cursor.execute('INSERT INTO db_cam (name, path, status) VALUES (%s, %s, %s)', (name, img_path, False))
                db.commit()
                cv2.destroyWindow('REGISTER')
                return login()
        else:
            if last_status != "tidak ada":
                import_and_play_audio(os.path.join(AUDIO_PATH, "wajah_tidak_terdeteksi.mp3"))
                last_status = "tidak ada"
            start_time = None

        cv2.imshow("REGISTER", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            close()

    db.close()
    close()

# LOGIN
def login():
    name = None
    def input_login():
        nonlocal name
        name = input_name.get().capitalize()
        if name :
            app.destroy()

    import_and_play_audio(os.path.join(AUDIO_PATH, "masukkan_nama_anda.mp3"))
    time.sleep(1.5)
    sys.stdin.flush()

    app = ctk.CTk()
    app.title("SVD - LOGIN")
    app.geometry("400x250")
    app.configure(bg='#1e1e26')
    
    label_title = ctk.CTkLabel(
        app, text="VERIFIKASI IDENTITAS", 
        font=("Helvetica", 14, "bold")
    )
    label_title.pack(pady=(30, 10))

    input_name = ctk.CTkEntry(
        app, font=("Helvetica", 12), 
    )
    input_name.pack(pady=10, padx=50, fill="x")
    input_name.focus_set()

    btn_submit = ctk.CTkButton(
        app, text="KONFIRMASI", 
        command=input_login,
        font=("Helvetica", 10, "bold"),
    )
    btn_submit.pack(pady=20)

    app.mainloop()

    time.sleep(5)

    start_time = None
    last_status = None

    db = db_config()
    cursor = db.cursor(buffered=True)
    cursor.execute('SELECT path FROM db_cam WHERE name=%s', (name, ))
    result_db = cursor.fetchone()

    if not result_db:
        print('NAMA MASIH BELUM TERDAFTAR DI DATABASE, SILAHKAN REGISTER!')
        import_and_play_audio(os.path.join(AUDIO_PATH, "NAMA MASIH BELUM TERDAFTAR DI DATABASE, SILAHKAN REGISTER.mp3"))
        register()
        return
    
    face_data = result_db[0]

    while True:
        result, default_frame = camera.read()
        if not result:
            break

        frame =  cv2.flip(default_frame, 1)
        faces = process_frame(frame)

        if len(faces) > 0:
            if start_time is None:
                start_time = time.time()
            
            if last_status != "ada":
                import_and_play_audio(os.path.join(AUDIO_PATH, "wajah_terdeteksi.mp3"))
                last_status = "ada"

            elapsed_time = time.time() - start_time
            countdown = 5 - int(elapsed_time)

            if countdown <= 0:
                (x, y, w, h) = faces[0]
                face_crop = frame[y:y+h, x:x+w]
                face_resized = cv2.resize(face_crop, (200, 200), interpolation=cv2.INTER_AREA)

                temp_filename = 'temp_pic.png'
                cache_folder = r'D:\programmer\New folder\cache'
                temp_file = os.path.join(cache_folder, temp_filename)
                check = cv2.imwrite(temp_file, face_resized)

                if not check:
                    return register()

                try:
                    obj = DeepFace.verify(
                        face_data,
                        temp_file,
                        model_name="VGG-Face",
                        enforce_detection=False
                    )

                    if obj['verified']:
                        print("Login Berhasil!")
                        import_and_play_audio(os.path.join(AUDIO_PATH, "login_berhasil.mp3"))
                        time.sleep(0.5)
                        cursor.execute("UPDATE db_cam SET status = %s WHERE name = %s", (True, name))
                        db.commit()
                        break
                    else:
                        print('Login gagal!')
                        import_and_play_audio(os.path.join(AUDIO_PATH, "login_gagal.mp3"))

                except Exception as e:
                    print (f"ERROR : {e}")

                finally:
                    os.remove(temp_file)
        
        else:
            if last_status != "tidak ada":
                import_and_play_audio(os.path.join(AUDIO_PATH, "wajah_tidak_terdeteksi.mp3"))
                last_status = "tidak ada"
            start_time = None

        cv2.imshow('LOGIN', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            close()

    db.close()
    cv2.destroyWindow('LOGIN')
    return sv_dashboard(name=name)