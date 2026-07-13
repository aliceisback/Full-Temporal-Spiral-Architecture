import json
import math
import wave
import struct
import argparse
from pathlib import Path

SAMPLE_RATE = 44100
AMPLITUDE = 8000

def generate_sine_wave(frequency, duration_seconds):
    frames = int(SAMPLE_RATE * duration_seconds)
    wave_data = bytearray()
    for i in range(frames):
        # Soft envelope (attack and decay) to mimic a distant bell
        envelope = 1.0
        if i < 0.1 * SAMPLE_RATE:
            envelope = i / (0.1 * SAMPLE_RATE)
        elif i > frames - 0.2 * SAMPLE_RATE:
            envelope = (frames - i) / (0.2 * SAMPLE_RATE)
            
        value = int(AMPLITUDE * envelope * math.sin(2.0 * math.pi * frequency * i / SAMPLE_RATE))
        wave_data.extend(struct.pack('<h', value))
    return wave_data

def play_audio_file(filepath):
    import os
    import platform
    import subprocess
    print(f"Playing {filepath}...")
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        elif platform.system() == "Darwin":
            subprocess.run(["afplay", filepath])
        else:
            subprocess.run(["aplay", filepath])
    except Exception as e:
        print(f"Could not play audio automatically: {e}")
        print("You can manually open the .wav file to listen.")

def main():
    parser = argparse.ArgumentParser(description="Generate and play 'Oste Nyakoi' or other Membrane music")
    parser.add_argument("--wav-only", action="store_true", help="Generate WAV without playing")
    parser.add_argument("--file", type=str, help="Path to the JSON music file", default="references/oste_nyakoi.json")
    args = parser.parse_args()

    skill_dir = Path(__file__).parent.parent
    
    # Handle absolute vs relative paths
    input_path = Path(args.file)
    if not input_path.is_absolute():
        music_file = skill_dir / input_path
    else:
        music_file = input_path

    output_file = music_file.with_suffix(".wav")

    if not music_file.exists():
        print(f"Error: Music file not found at {music_file}")
        return

    with open(music_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") == "SILENCE":
        print("The music has been destroyed by the Poison Pill. Silence remains.")
        return

    bpm = data["musical_identity"]["bpm"]
    beat_duration = 60.0 / bpm

    print(f"Generating music... (Z={data['melody_sequence'][-1]['spiral']['z']})")

    with wave.open(str(output_file), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        current_beat = 1
        
        for event in data["melody_sequence"]:
            # Add silence if there's a gap
            gap_beats = event["beat"] - current_beat
            if gap_beats > 0:
                silence_frames = int(gap_beats * beat_duration * SAMPLE_RATE)
                wav_file.writeframes(b'\x00\x00' * silence_frames)
            
            freq = event["frequency_hz"]
            dur = event["duration_beats"] * beat_duration
            
            # Very basic synthesis: just the main note. (A true synth would layer the harmony)
            wave_data = generate_sine_wave(freq, dur)
            wav_file.writeframes(wave_data)
            
            current_beat = event["beat"] + event["duration_beats"]

    print(f"WAV file generated at {output_file}")
    
    if not args.wav_only:
        play_audio_file(str(output_file))

if __name__ == "__main__":
    main()
