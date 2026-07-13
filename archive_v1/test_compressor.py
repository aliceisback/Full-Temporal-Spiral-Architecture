# test_compressor.py
import numpy as np
from dataclasses import dataclass
from typing import List

# ============================================================
# 1. ОСНОВНИ КЛАСОВЕ (от temporal_memory.py)
# ============================================================

@dataclass
class SpiralCoordinate:
    r: float
    theta: float
    z: float

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
    cosine_sim = np.dot(node_a.semantic_embedding, node_b.semantic_embedding) / (
        np.linalg.norm(node_a.semantic_embedding) * np.linalg.norm(node_b.semantic_embedding)
    )
    angular_diff = node_a.coordinates.angular_difference(node_b.coordinates)
    time_diff = abs(node_a.coordinates.z - node_b.coordinates.z)
    distance = np.sqrt(angular_diff**2 + (time_diff * 0.05)**2)
    gravity = cosine_sim / (1 + distance)
    return max(0.0, gravity)


# ============================================================
# 2. ЦИКЛИЧЕН КОМПРЕСОР
# ============================================================

class CyclicalCompressor:
    def __init__(self, similarity_threshold: float = 0.85, angular_threshold: float = 0.5):
        self.similarity_threshold = similarity_threshold
        self.angular_threshold = angular_threshold

    def compress(self, new_node: TemporalNode, memory_bank: List[TemporalNode]) -> TemporalNode:
        best_match = None
        best_similarity = 0.0

        for existing_node in memory_bank:
            cosine_sim = np.dot(new_node.semantic_embedding, existing_node.semantic_embedding) / (
                np.linalg.norm(new_node.semantic_embedding) * np.linalg.norm(existing_node.semantic_embedding)
            )
            angular_diff = new_node.coordinates.angular_difference(existing_node.coordinates)

            if cosine_sim > self.similarity_threshold and angular_diff < self.angular_threshold:
                if cosine_sim > best_similarity:
                    best_similarity = cosine_sim
                    best_match = existing_node

        if best_match:
            # Компресия
            merged_embedding = (new_node.semantic_embedding + best_match.semantic_embedding) / 2
            new_weight = best_match.weight + new_node.weight
            new_z = max(new_node.coordinates.z, best_match.coordinates.z)

            return TemporalNode(
                text_content=new_node.text_content,
                semantic_embedding=merged_embedding,
                coordinates=SpiralCoordinate(
                    r=best_match.coordinates.r,
                    theta=best_match.coordinates.theta,
                    z=new_z
                ),
                weight=new_weight
            )
        else:
            return new_node


# ============================================================
# 3. ТЕСТ
# ============================================================

if __name__ == "__main__":
    compressor = CyclicalCompressor()

    # Създаваме два много близки възела
    emb1 = np.array([0.8, 0.6, 0.0])
    emb2 = np.array([0.78, 0.62, 0.05])

    node1 = TemporalNode(
        text_content="Какво е диабет?",
        semantic_embedding=emb1,
        coordinates=SpiralCoordinate(r=1.0, theta=0.5, z=10),
        weight=1.0
    )

    node2 = TemporalNode(
        text_content="Какво е диабет тип 2?",
        semantic_embedding=emb2,
        coordinates=SpiralCoordinate(r=1.0, theta=0.55, z=12),
        weight=1.0
    )

    memory = [node1]

    print("Преди компресия: memory има", len(memory), "възел(а)")

    compressed_node = compressor.compress(node2, memory)

    if compressed_node.weight > 1.0:
        print("✅ Компресията СРАБОТИ!")
        print(f"   Ново тегло: {compressed_node.weight}")
        print(f"   Ново време (z): {compressed_node.coordinates.z}")
    else:
        print("❌ Компресията НЕ сработи. Възелът не беше обединен.")
