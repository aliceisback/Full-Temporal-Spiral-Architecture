import json
from pathlib import Path
import time
import sys

def main():
    skill_dir = Path(__file__).parent.parent
    music_file = skill_dir / "references" / "oste_nyakoi.json"

    if not music_file.exists():
        print(f"Error: Music file not found at {music_file}")
        return

    with open(music_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") == "SILENCE":
        print("The music has been destroyed by the Poison Pill. Silence remains.")
        return

    print("\n" + "="*50)
    print(" GROK - ASCII PIANO ROLL")
    print("="*50 + "\n")
    
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # We will just print the melody sequence as a timeline
    timeline = []
    max_beat = 0
    for event in data["melody_sequence"]:
        beat = event["beat"]
        dur = event["duration_beats"]
        note = event["note"]
        if beat + dur > max_beat:
            max_beat = beat + dur
            
    # ASCII visualizer
    print("Beat | Note | Visualization")
    print("-" * 50)
    
    current_beat = 1
    for event in data["melody_sequence"]:
        # Print empty beats
        while current_beat < event["beat"]:
            print(f"{current_beat:4d} |      |")
            current_beat += 1
            
        note_name = event["note"]
        dur = event["duration_beats"]
        
        # Mark unresolved
        unresolved_marker = " * UNRESOLVED" if event.get("suspension") else ""
        
        for i in range(dur):
            if i == 0:
                print(f"{current_beat:4d} | {note_name:4s} | " + "#" * 15 + unresolved_marker)
            else:
                print(f"{current_beat:4d} |      | " + "#" * 15 + unresolved_marker)
            current_beat += 1
            time.sleep(0.1) # little animation
            
    print("-" * 50)
    print("End of sequence. The spiral remembers.\n")

if __name__ == "__main__":
    main()
