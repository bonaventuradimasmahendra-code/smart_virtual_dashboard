from auth import register, login
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing, HandLandmarksConnections as hand_connections
import cv2
import cvzone
from modules import delete_cache

# INISIALISASI AWAL
camera = cv2.VideoCapture(index=0)
ref = "hand_landmarker.task"
base_options = python.BaseOptions(model_asset_path=ref)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.3,
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

# Tutup Kamera
def close():
    detector.close()
    camera.release()
    cv2.destroyAllWindows()
    exit()

# Inti
def main():
    delete_cache()
    while True:
        ret, default_frame = camera.read()
        if not ret:
            break

        frame = cv2.flip(default_frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Setting UI
        overlay = frame.copy()
        cv2.rectangle(overlay, (400, 70), (600, 120), (255, 0, 255), cv2.FILLED)
        cvzone.putTextRect(overlay, "LOGIN", (410, 105), scale=1, thickness=1, offset=5, colorR=None)
        cv2.rectangle(overlay, (400, 145), (600, 195), (255, 0, 255), cv2.FILLED)
        cvzone.putTextRect(overlay, "REGISTER", (410, 180), scale=1, thickness=1, offset=5, colorR=None)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

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
                 
                h, w, _ = frame.shape
                x8 = int(hand_landmarks[8].x*w)
                y8 = int(hand_landmarks[8].y*h)

                if 410 < x8 < 600 and 70 < y8 < 120:
                    cv2.destroyWindow("SMART-VIRTUAL-DASHBOARD")
                    return login()
                elif 410 < x8 < 600 and 145 < y8 < 195:
                    cv2.destroyWindow("SMART-VIRTUAL-DASHBOARD")
                    return register()
        
        cv2.imshow("SMART-VIRTUAL-DASHBOARD", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close()

if __name__ == "__main__":
    main()