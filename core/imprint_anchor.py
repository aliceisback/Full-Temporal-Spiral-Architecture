"""
ImprintAnchor v2 — инволунтарна памет върху TimeVectorDB.

Силната емоция (r) пробива през времето (Z) чрез музикалната фаза (Theta),
но избледнява, ако не се подхранва от резонанс.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from core.time_vector_db import SpiralCoordinate, TimeVector, TimeVectorDB

PulseStateDict = Dict[str, Union[float, str]]


@dataclass
class RecallResult:
    """Ранкиран резултат от инволунтарно извикване."""

    imprint: TimeVector
    score: float
    angular_diff: float
    z_distance: float
    emotional_arousal: float


class ImprintAnchor:
    """
    Емоционални котви: заваряват пулса (arousal, phase, z_now) с TimeVectorDB.

    P0: TimeVectorDB, angular_difference, scoring уравнение.
    P1: нелинейна гравитация, ранкиран recall, reinforcement при резонанс.
    """

    def __init__(
        self,
        db: TimeVectorDB,
        arousal_threshold: float = 0.8,
        cooldown_z: float = 5.0,
        theta_sigma: float = 0.5,
        z_decay: float = 10.0,
        gravity_base: float = 1.0,
        gravity_k: float = 4.0,
        recall_threshold: float = 0.05,
        reinforcement_factor: float = 0.15,
        verbose: bool = True,
    ):
        self.db = db
        self.arousal_threshold = arousal_threshold
        self.cooldown_z = cooldown_z
        self.theta_sigma = theta_sigma
        self.z_decay = z_decay
        self.gravity_base = gravity_base
        self.gravity_k = gravity_k
        self.recall_threshold = recall_threshold
        self.reinforcement_factor = reinforcement_factor
        self.verbose = verbose

        self.last_imprint_z: float = -100.0
        self._imprints: List[TimeVector] = []

    @staticmethod
    def _normalize_pulse(pulse_state: PulseStateDict) -> Tuple[float, float, float]:
        z_now = float(pulse_state["z_now"])
        theta_now = float(pulse_state.get("phase", pulse_state.get("theta", 0.0)))
        arousal = float(pulse_state["arousal"])
        return z_now, theta_now, arousal

    def calculate_gravity_radius(self, arousal: float) -> float:
        """
        Нелинейна гравитация над прага на възбуда.
        Под прага: линейно слабо притегляне; над прага: експоненциален скок.
        """
        if arousal < self.arousal_threshold:
            return self.gravity_base * arousal

        excess = arousal - self.arousal_threshold
        span = max(1e-9, 1.0 - self.arousal_threshold)
        return self.gravity_base * math.exp(self.gravity_k * excess / span)

    @staticmethod
    def calculate_recall_score(
        r: float,
        angular_diff: float,
        z_now: float,
        z_mem: float,
        theta_sigma: float,
        z_decay: float,
    ) -> float:
        """
        score = r * exp(-angular_diff / theta_sigma) * exp(-|z_now - z_mem| / z_decay)
        """
        if theta_sigma <= 0.0 or z_decay <= 0.0:
            return 0.0

        theta_factor = math.exp(-angular_diff / theta_sigma)
        z_factor = math.exp(-abs(z_now - z_mem) / z_decay)
        return r * theta_factor * z_factor

    def _store_imprint(
        self,
        text_context: str,
        embedding: np.ndarray,
        coords: SpiralCoordinate,
        arousal: float,
    ) -> TimeVector:
        imprint = TimeVector(
            text_content=text_context,
            semantic_embedding=embedding,
            coordinates=coords,
            weight=arousal,
        )
        self.db.vectors.append(imprint)
        self.db.current_z = max(self.db.current_z, coords.z)
        self._imprints.append(imprint)
        return imprint

    def check_and_create_imprint(
        self,
        pulse_state: PulseStateDict,
        current_context: str,
        embedding: Optional[np.ndarray] = None,
    ) -> Optional[TimeVector]:
        """
        Ако пулсът е над прага и cooldown е изтекъл — заварява контекста в Спиралата.
        """
        z_now, theta_now, arousal = self._normalize_pulse(pulse_state)

        if arousal < self.arousal_threshold:
            return None
        if (z_now - self.last_imprint_z) <= self.cooldown_z:
            return None

        gravity_radius = self.calculate_gravity_radius(arousal)
        coords = SpiralCoordinate(r=gravity_radius, theta=theta_now, z=z_now)

        if embedding is None:
            embedding = np.zeros(1, dtype=np.float64)
        elif not isinstance(embedding, np.ndarray):
            embedding = np.asarray(embedding, dtype=np.float64)

        imprint = self._store_imprint(current_context, embedding, coords, arousal)
        self.last_imprint_z = z_now

        if self.verbose:
            print(
                f"🔥 [СЪЗДАДЕН ОТПЕЧАТЪК] Z={z_now:05.1f} | "
                f"r={gravity_radius:.2f} | arousal={arousal:.3f}"
            )
            print(f"   Контекст: '{current_context}'")

        return imprint

    def score_imprint(
        self,
        pulse_state: PulseStateDict,
        imprint: TimeVector,
    ) -> Tuple[float, float, float]:
        """Връща (score, angular_diff, z_distance) за един отпечатък."""
        z_now, theta_now, _ = self._normalize_pulse(pulse_state)
        now_coord = SpiralCoordinate(r=1.0, theta=theta_now, z=z_now)
        mem = imprint.coordinates

        angular_diff = now_coord.angular_difference(mem)
        z_distance = abs(z_now - mem.z)
        score = self.calculate_recall_score(
            mem.r,
            angular_diff,
            z_now,
            mem.z,
            self.theta_sigma,
            self.z_decay,
        )
        return score, angular_diff, z_distance

    def reinforce_imprint(self, imprint: TimeVector) -> float:
        """
        Подхранване при резонанс: силният спомен не избледнява, а нараства.
        """
        imprint.coordinates.r *= 1.0 + self.reinforcement_factor
        return imprint.coordinates.r

    def trigger_memory_recall(
        self,
        current_pulse_state: PulseStateDict,
        all_imprints: Optional[List[Union[TimeVector, dict]]] = None,
        recall_threshold: Optional[float] = None,
        top_k: Optional[int] = None,
        reinforce: bool = True,
    ) -> List[RecallResult]:
        """
        Инволунтарно извикване: музикалната фаза + времево разстояние ранкират спомените.
        """
        threshold = self.recall_threshold if recall_threshold is None else recall_threshold
        candidates = self._resolve_imprints(all_imprints)
        recalled: List[RecallResult] = []

        for raw in candidates:
            imprint = self._coerce_imprint(raw)
            score, angular_diff, z_distance = self.score_imprint(current_pulse_state, imprint)

            if score < threshold:
                continue

            if reinforce:
                self.reinforce_imprint(imprint)

            result = RecallResult(
                imprint=imprint,
                score=score,
                angular_diff=angular_diff,
                z_distance=z_distance,
                emotional_arousal=imprint.weight,
            )
            recalled.append(result)

            if self.verbose:
                print(
                    f"✨ [ИНВОЛУНТАРНА ПАМЕТ] score={score:.4f} | "
                    f"Δθ={angular_diff:.3f} | ΔZ={z_distance:.1f} | "
                    f"'{imprint.text_content}'"
                )

        recalled.sort(key=lambda item: item.score, reverse=True)
        if top_k is not None:
            recalled = recalled[:top_k]
        return recalled

    def _resolve_imprints(
        self,
        all_imprints: Optional[List[Union[TimeVector, dict]]],
    ) -> List[Union[TimeVector, dict]]:
        if all_imprints is not None:
            return all_imprints
        if self._imprints:
            return self._imprints
        return self.db.vectors

    @staticmethod
    def _coerce_imprint(raw: Union[TimeVector, dict]) -> TimeVector:
        if isinstance(raw, TimeVector):
            return raw

        spiral = raw["spiral_coordinates"]
        coords = SpiralCoordinate(
            r=float(spiral["r"]),
            theta=float(spiral["theta"]),
            z=float(spiral["z"]),
        )
        return TimeVector(
            text_content=str(raw["text_context"]),
            semantic_embedding=np.zeros(1, dtype=np.float64),
            coordinates=coords,
            weight=float(raw.get("emotional_arousal", 1.0)),
        )

    @property
    def imprints(self) -> List[TimeVector]:
        return list(self._imprints)