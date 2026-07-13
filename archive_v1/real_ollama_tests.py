import numpy as np
import ollama
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
from typing import List
import time
import os
import random

# ============================================================
# 1. ОСНОВНИ КЛАСОВЕ (Спирала и Компресия)
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

    def process_node(self, new_node: TemporalNode, memory_bank: List[TemporalNode]) -> TemporalNode:
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

            compressed_node = TemporalNode(
                text_content=best_match.text_content,
                semantic_embedding=merged_embedding,
                coordinates=SpiralCoordinate(
                    r=best_match.coordinates.r,
                    theta=best_match.coordinates.theta,
                    z=new_z
                ),
                weight=new_weight
            )
            memory_bank[:] = [n for n in memory_bank if n is not best_match]
            memory_bank.append(compressed_node)
            return compressed_node
        else:
            memory_bank.append(new_node)
            return new_node

# ============================================================
# 2. РЕАЛЕН ТЕЖЪК ТЕСТ КЪМ OLLAMA
# ============================================================

def log_result(filename: str, text: str):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)

def run_heavy_real_test(models: List[str], questions: List[str], log_file: str):
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    log_result(log_file, f"\n{'='*50}\nСВРЪХ-ТЕЖЪК РЕАЛЕН ТЕСТ ЗА АРХИТЕКТА (1-2 ЧАСА)\n{'='*50}")
    
    for model_name in models:
        log_result(log_file, f"\n>>> СТАРТИРАНЕ С МОДЕЛ: {model_name} (Въпроси: {len(questions)})")
        memory_bank: List[TemporalNode] = []
        compressor = CyclicalCompressor()
        
        for i, q in enumerate(questions):
            # 1. Спирала
            emb = encoder.encode(q)
            theta = (i % 10) * (2 * np.pi / 10)
            new_node = TemporalNode(text_content=q, semantic_embedding=emb, coordinates=SpiralCoordinate(r=1.0, theta=theta, z=float(i)))
            
            # 2. Компресия
            compressed = compressor.process_node(new_node, memory_bank)
            
            # 3. Намиране на най-силен спомен
            best_context = ""
            best_gravity = 0
            if len(memory_bank) > 1:
                for past_node in memory_bank:
                    if past_node is compressed: continue
                    grav = calculate_gravity(compressed, past_node)
                    if grav > best_gravity:
                        best_gravity = grav
                        best_context = past_node.text_content
            
            # 4. Реално извикване към Ollama
            prompt = f"Контекст от Спиралата: {best_context}\n\nМоля, отговори кратко на въпроса: {q}" if best_context else f"Моля, отговори кратко на въпроса: {q}"
                
            start_time = time.time()
            try:
                response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
                answer = response['message']['content'].replace('\n', ' ')[:100] + "..."
                elapsed = time.time() - start_time
                log_result(log_file, f"[{i+1}/{len(questions)}] {model_name} ({elapsed:.1f}s) -> ВЪПРОС: {q[:30]}... | СПОМЕН: {best_context[:30]}")
            except Exception as e:
                log_result(log_file, f"ГРЕШКА ПРИ СВЪРЗВАНЕ С OLLAMA: {e}")
                
        log_result(log_file, f"\n=== КРАЙ НА ТЕСТА С {model_name} ===")
        log_result(log_file, f"Паметта задържа {len(memory_bank)} възела след {len(questions)} въпроса.")

if __name__ == "__main__":
    LOG_FILE = "HEAVY_REAL_OLLAMA_TEST_RESULTS.txt"
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        
    models_to_test = ["qwen2.5:7b", "qwen2.5:32b", "llava:latest"]
    
    base_questions = [
        "Какво е квантова физика?", "Как се готви мусака?", "Защо небето е синьо?",
        "Симптоми на диабет", "Откриването на Америка", "Теория на относителността",
        "Що е то кръвно налягане?", "Рецепта за шопска салата", "Кой е Айнщайн?"
    ]
    random.seed(42)
    heavy_questions = [random.choice(base_questions) for _ in range(150)]
    
    run_heavy_real_test(models_to_test, heavy_questions, LOG_FILE)
