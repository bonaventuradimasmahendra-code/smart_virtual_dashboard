from gtts import gTTS
import os

PATH_FOLDER = r"D:\programmer\New folder\audio\public"

def add_audio():
    while True:
        text = input('Masukkan text anda : ')
        name = input('Masukkan nama file anda : ')

        tts = gTTS(text=text, lang='id')
        filename = f"{name}.mp3"

        audio_path = os.path.join(PATH_FOLDER, filename)

        tts.save(audio_path)

        lanjut = input('Lanjut? [y/n] ').lower()
        if 'n' in lanjut:
            break

if __name__ == "__main__":
    add_audio()