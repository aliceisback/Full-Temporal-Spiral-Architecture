# test_temporal_spiral.py
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

# ============================================================
# 1. ОСНОВНИ КЛАСОВЕ
# ============================================================

@dataclass
class SpiralCoordinate:
    r: float      # Радиус / интензитет
    theta: float  # Ъгъл във времето (в радиани)
    z: float      # Време

    def angular_difference(self, other: 'SpiralCoordinate') -> float:
        diff = abs(self.theta - other.theta)
        return min(diff, 2 * np.pi - diff)


@dataclass
class TemporalNode:
    text_content: str
    semantic_embedding: np.ndarray
    coordinates: SpiralCoordinate
    weight: float = 1.0


def calculate_gravity(node_a: TemporalNode, node_b: TemporalNode) -> float:
    """Изчислява гравитация между два възела"""
    # Семантична близост
    cosine_sim = np.dot(node_a.semantic_embedding, node_b.semantic_embedding) / (
        np.linalg.norm(node_a.semantic_embedding) * np.linalg.norm(node_b.semantic_embedding)
    )

    # Спирална близост
    angular_diff = node_a.coordinates.angular_difference(node_b.coordinates)
    time_diff = abs(node_a.coordinates.z - node_b.coordinates.z)

    # Комбинирано разстояние
    distance = np.sqrt(angular_diff**2 + (time_diff * 0.05)**2)

    gravity = cosine_sim / (1 + distance)
    return max(0.0, gravity)


# ============================================================
# 2. ТЕСТ 1: РЪЧНО ЗАДАДЕНИ ВЕКТОРИ (Контролиран)
# ============================================================

def test_manual_vectors():
    print("\n=== ТЕСТ 1: Ръчно зададени вектори ===\n")

    # Създаваме embedding-и (опростено - случайни, но контролирани)
    emb1 = np.array([0.8, 0.6, 0.0])
    emb2 = np.array([0.75, 0.65, 0.1])   # Много близък до emb1
    emb3 = np.array([0.1, 0.2, 0.9])     # Съвсем различен

    node1 = TemporalNode(
        text_content="Какво е диабет?",
        semantic_embedding=emb1,
        coordinates=SpiralCoordinate(r=1.0, theta=0.5, z=10)
    )

    node2 = TemporalNode(
        text_content="Какво представлява диабет тип 2?",
        semantic_embedding=emb2,
        coordinates=SpiralCoordinate(r=1.0, theta=0.6, z=15)  # близък ъгъл и време
    )

    node3 = TemporalNode(
        text_content="Какво време ще има утре?",
        semantic_embedding=emb3,
        coordinates=SpiralCoordinate(r=1.0, theta=3.0, z=100)  # далечен ъгъл и време
    )

    print(f"Гравитация между node1 и node2 (близки): {calculate_gravity(node1, node2):.4f}")
    print(f"Гравитация между node1 и node3 (далечни): {calculate_gravity(node1, node3):.4f}")


# ============================================================
# 3. ТЕСТ 2: ОПИТ ЗА "ИНТУИЦИЯ" (по-свободен)
# ============================================================

def test_intuition():
    print("\n=== ТЕСТ 2: Опит за интуиция на модела ===\n")
    print("Този тест е предназначен да се пусне с Ollama.")
    print("Засега тук само показваме структурата.\n")

    # Тук по-късно ще добавим промпт към Ollama
    print("TODO: Тук ще сложим промпт към модела, за да видим дали сам разпознава идеята за спирала.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    test_manual_vectors()
    test_intuition()
