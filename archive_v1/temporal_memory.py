# temporal_memory.py
from dataclasses import dataclass
import numpy as np
from typing import Optional

@dataclass
class SpiralCoordinate:
    """3D координата върху спиралата във времето"""
    r: float      # Радиус / интензитет на спомена
    theta: float  # Ъгъл (фаза на цикъла) в радиани
    z: float      # Абсолютно време

    def angular_difference(self, other: 'SpiralCoordinate') -> float:
        """
        Връща най-късото ъглово разстояние между два ъгъла (0 до π).
        """
        diff = abs(self.theta - other.theta)
        return min(diff, 2 * np.pi - diff)


@dataclass
class TemporalNode:
    """Единичен възел в темпоралната спирала"""
    text_content: str
    semantic_embedding: np.ndarray
    coordinates: SpiralCoordinate
    weight: float = 1.0  # Колко "тежък" е този спомен (за компресия)


def calculate_gravity(node_a: TemporalNode, node_b: TemporalNode) -> float:
    """
    Изчислява 'гравитацията' между два възела (Експоненциален decay).
    Комбинира семантична близост с времева/спирална близост.
    """
    # Семантична близост
    norm_a = np.linalg.norm(node_a.semantic_embedding)
    norm_b = np.linalg.norm(node_b.semantic_embedding)
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    cosine_sim = np.dot(node_a.semantic_embedding, node_b.semantic_embedding) / (norm_a * norm_b)
    cosine_sim = max(0.0, cosine_sim) # Защита от отрицателни стойности

    # Времева/спирална близост
    angular_diff = node_a.coordinates.angular_difference(node_b.coordinates)
    
    # Точка 5: Спиралата се затваря в кръг (Минал живот/Отпечатък).
    time_diff = abs(node_a.coordinates.z - node_b.coordinates.z)

    # Пространствено разстояние
    spatial_distance = np.sqrt(angular_diff**2 + (time_diff * 0.05)**2)

    # Точка 1: Експоненциален decay вместо делене
    decay_factor = 1.0
    gravity = cosine_sim * np.exp(-decay_factor * spatial_distance)

    # Влияние на тежестта (важността) върху притеглянето
    return gravity * (node_a.weight * node_b.weight)
