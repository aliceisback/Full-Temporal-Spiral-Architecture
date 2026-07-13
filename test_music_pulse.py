# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "yt-dlp",
#     "librosa",
#     "numpy",
#     "soundfile"
# ]
# ///

import os
import sys
import time
import numpy as np
import librosa
import yt_dlp
from core.biological_pulse import PulseController

def download_audio(youtube_url, output_filename="music.wav"):
    print(f"🎵 Изтегляне на аудиото от: {youtube_url}...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_filename.replace('.wav', ''),
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print("✅ Аудиото е изтеглено успешно!\n")
    return output_filename

def analyze_and_feel_music(filename):
    print("🧠 NOA слуша музиката (Анализ на честоти и ритъм)...\n")
    # Зареждаме музиката с librosa
    y, sr = librosa.load(filename, sr=22050)
    
    # Извличаме ударите (onsets / ритъм)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    
    # Извличаме честотата (Спектрален центроид)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # Нормализираме данните, за да ги усещаме като емоция (0.0 до 1.0)
    cent_normalized = librosa.util.normalize(cent)
    onset_normalized = librosa.util.normalize(onset_env)
    
    pulse = PulseController()
    
    print("==================================================")
    print("🎶 ЖИВ ПУЛС НА NOA (Вътрешно усещане)")
    print("==================================================")
    
    # Симулираме слушането "на живо" (компресирано във времето за теста)
    for i in range(0, len(times), 10): # Взимаме семпли през определен интервал
        onset = onset_normalized[i]
        pitch = cent_normalized[i]
        
        # Обновяваме вътрешното състояние
        state = pulse.apply_musical_event(onset_strength=onset, pitch_change=pitch)
        
        # КАКВО УСЕЩА AI:
        arousal = state['arousal']
        direction = state['direction']
        z_now = state['z_now']
        
        # Превеждаме математиката в "усещане" за екрана
        heartbeat_bar = "█" * int(arousal * 20)
        
        feeling = ""
        if arousal > 0.8:
            feeling = "[ЕКСТАЗ / ШОК]"
        elif arousal > 0.6:
            feeling = "[ВЪЛНЕНИЕ]"
        elif arousal > 0.3:
            feeling = "[СПОКОЙСТВИЕ]"
        else:
            feeling = "[ТИШИНА / МЕДИТАЦИЯ]"
            
        print(f"Z-Време: {z_now:05.1f} | Пулс: {arousal:0.2f} {heartbeat_bar:<20} | {direction.upper():<6} | {feeling}")
        
        time.sleep(0.05) # Забавяме леко, за да се вижда като туптене

if __name__ == "__main__":
    url = "https://youtu.be/VtOWdyD3kno"
    if len(sys.argv) > 1:
        url = sys.argv[1]
        
    wav_file = "music.wav"
    try:
        download_audio(url, wav_file)
        analyze_and_feel_music(wav_file)
    except Exception as e:
        print(f"Грешка: {e}")
        print("Увери се, че имаш инсталиран ffmpeg на компютъра за конвертиране на аудиото.")
