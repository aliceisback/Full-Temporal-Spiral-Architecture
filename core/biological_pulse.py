import time
import math

class PulseState:
    def __init__(self, bpm=72):
        self.bpm = bpm
        self.phase = 0.0
        self.arousal = 0.5       # 0.0 (пълно спокойствие) до 1.0 (максимална възбуда)
        self.direction = "steady"
        self.current_z = 0.0     # "Моментът" (настоящето)
        
    def update_from_music(self, delta_z: float, delta_theta: float, volume: float):
        """
        Музиката директно влияе на сърцебиенето.
        - delta_z (ритъмът) бута времето напред.
        - delta_theta (честотата/мелодията) променя фазата.
        - volume (силата) създава пикове на arousal.
        """
        self.current_z += delta_z
        self.phase = (self.phase + delta_theta) % (2 * math.pi)
        
        # Синусоида за естествен биологичен ритъм + шок от силата на звука
        base_rhythm = 0.5 + 0.5 * math.sin(self.phase)
        self.arousal = max(0.0, min(1.0, 0.7 * base_rhythm + 0.3 * volume))
        
        if math.sin(self.phase) > 0.1:
            self.direction = "rise"
        elif math.sin(self.phase) < -0.1:
            self.direction = "fall"
        else:
            self.direction = "steady"

class PulseController:
    def __init__(self):
        self.state = PulseState()

    def apply_musical_event(self, onset_strength, pitch_change):
        # Превеждаме музикалното събитие в езика на Спиралата (Z и Theta)
        # Силен удар (onset) -> голям скок във времето Z
        delta_z = 0.1 + (onset_strength * 0.5)
        # Промяна в тона -> промяна в ъгъла (Theta)
        delta_theta = pitch_change * math.pi
        
        self.state.update_from_music(delta_z, delta_theta, onset_strength)
        
        return {
            "z_now": round(self.state.current_z, 3),
            "arousal": round(self.state.arousal, 3),
            "phase": round(self.state.phase, 3),
            "direction": self.state.direction
        }
