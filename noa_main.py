# noa_core.py
import numpy as np
import ollama
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
from typing import List

# ============================================================
# 1. ОСНОВНИ КЛАСОВЕ
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
# 2. ГЛАВЕН КЛАС - NOA CORE
# ============================================================

class NOACore:
    def __init__(self, model_name: str = "qwen2.5:7b"):
        self.model_name = model_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.memory_bank: List[TemporalNode] = []
        self.compressor = CyclicalCompressor()
        self.step = 0

    def _get_spiral_coordinate(self) -> SpiralCoordinate:
        """Симулира спирална координата"""
        z = self.step
        theta = (self.step % 10) * (2 * np.pi / 10)   # увива се на всеки 10 стъпки
        return SpiralCoordinate(r=1.0, theta=theta, z=z)

    def process_input(self, user_input: str):
        self.step += 1

        # 1. Семантичен embedding
        embedding = self.encoder.encode(user_input)

        # 2. Създаваме нов възел
        new_node = TemporalNode(
            text_content=user_input,
            semantic_embedding=embedding,
            coordinates=self._get_spiral_coordinate()
        )

        # 3. Компресия
        compressed_node = self.compressor.compress(new_node, self.memory_bank)

        # 4. Ако е бил компресиран, обновяваме паметта
        if compressed_node.weight > new_node.weight:
            # Премахваме стария възел и добавяме компресирания
            self.memory_bank = [n for n in self.memory_bank if n.text_content != compressed_node.text_content]
            self.memory_bank.append(compressed_node)
        else:
            self.memory_bank.append(compressed_node)

        # 5. Намираме възела с най-висока гравитация
        best_context = ""
        if len(self.memory_bank) > 1:
            best_gravity = 0
            best_node = None
            for node in self.memory_bank[:-1]:  # без последния
                gravity = calculate_gravity(compressed_node, node)
                if gravity > best_gravity:
                    best_gravity = gravity
                    best_node = node
            if best_node:
                best_context = best_node.text_content

        # 6. Изпращаме към Ollama
        prompt = user_input
        if best_context:
            prompt = f"Previous relevant context: {best_context}\n\nCurrent question: {user_input}"

        response = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        print(f"\n>>> Потребител: {user_input}")
        print(f">>> Контекст: {best_context if best_context else 'Няма'}")
        print(f">>> Отговор: {response['message']['content']}\n")

        return response['message']['content']


# ============================================================
# 3. ТЕСТ
# ============================================================

if __name__ == "__main__":
    noa = NOACore(model_name="qwen2.5:7b")

    print("=== NOA Core Test ===\n")
    noa.process_input("Какво е диабет?")
    noa.process_input("Какво е диабет тип 2?")
    noa.process_input("Какви са симптомите на диабет?")
