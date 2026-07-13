import numpy as np
from sentence_transformers import SentenceTransformer
import time
from typing import List
import random
import os

from core.temporal_memory import TemporalNode, SpiralCoordinate
from core.cyclical_compressor import CyclicalCompressor

encoder = SentenceTransformer('all-MiniLM-L6-v2')

def run_compression_test(test_name: str, questions: List[str], iterations: int = 1):
    print(f"\n[{test_name}] - Входни въпроси: {len(questions)}")
    results = []
    
    for it in range(iterations):
        compressor = CyclicalCompressor(similarity_threshold=0.85, angular_threshold=0.5)
        memory_bank: List[TemporalNode] = []
        
        start_time = time.time()
        for i, q in enumerate(questions):
            emb = encoder.encode(q)
            # Всяка стъпка е "час" напред във времето. Завърта се след 10 стъпки.
            theta = (i % 10) * (2 * np.pi / 10)
            node = TemporalNode(
                text_content=q,
                semantic_embedding=emb,
                coordinates=SpiralCoordinate(r=1.0, theta=theta, z=float(i))
            )
            compressor.process_node(node, memory_bank)
            
        elapsed = time.time() - start_time
        
        total_in = len(questions)
        total_out = len(memory_bank)
        comp_ratio = ((total_in - total_out) / total_in) * 100 if total_in > 0 else 0
        max_weight = max([n.weight for n in memory_bank]) if memory_bank else 0
        
        res_str = f" Iteration {it+1}: In={total_in} | Out={total_out} | Compress={comp_ratio:.1f}% | MaxWeight={max_weight} | Time={elapsed:.2f}s"
        print(res_str)
        
        results.append({
            "test_name": test_name,
            "iteration": it + 1,
            "in": total_in,
            "out": total_out,
            "ratio": comp_ratio,
            "max_w": max_weight,
            "time": elapsed
        })
    return results

if __name__ == "__main__":
    print("=== TEMPORAL SPIRAL MASS COMPRESSION BENCHMARKS ===\n")
    
    # ТЕСТ 1: Точно еднакви въпроси
    exact_q = ["Как се лекува диабет?"] * 50
    run_compression_test("ТЕСТ 1: 50 Еднакви въпроса", exact_q, 1)
    
    # ТЕСТ 2: Сходни по смисъл
    semantic_base = [
        "Какво е кръвно налягане?",
        "Що е то артериално налягане?",
        "Обясни ми какво означава кръвно налягане.",
        "Можеш ли да дефинираш кръвно налягане?",
        "Какво представлява налягането на кръвта?"
    ]
    semantic_q = semantic_base * 10 # 50
    run_compression_test("ТЕСТ 2: 50 Сходни (5 вариации х 10)", semantic_q, 1)
    
    # ТЕСТ 3: Смесени (Хаос)
    chaos_base = [
        "Симптоми на диабет", "Главоболие и температура", 
        "Кога е открита Америка?", "Рецепта за мусака", 
        "Лечение на диабет тип 2", "Америка Кристофор Колумб", 
        "Как се прави мусака", "Настинка и грип"
    ]
    chaos_q = chaos_base * 6 # 48
    run_compression_test("ТЕСТ 3: 48 Смесени и сходни (Хаос)", chaos_q, 1)
    
    # ТЕСТ 4: Мащабен (500 въпроса, 5 итерации)
    random.seed(42)
    large_base = chaos_base + semantic_base + ["Какво е квантова физика?", "Теория на относителността"]
    large_q = [random.choice(large_base) for _ in range(500)]
    
    run_compression_test("ТЕСТ 4: Мащабен Хаос (500 въпроса, 5 итерации)", large_q, 5)

    print("\nБенчмарковете приключиха успешно.")
