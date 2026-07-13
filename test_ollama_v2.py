import ollama
import numpy as np
from sentence_transformers import SentenceTransformer
from core.time_vector_db import TimeVectorDB
import time

def main():
    print("=== NOA Temporal Vector DB V2: Интеграция с Ollama ===")
    
    # 1. Инициализация на модела за Embedding
    print("[1] Зареждане на SentenceTransformer (може да отнеме няколко секунди)...")
    try:
        embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    except Exception as e:
        print(f"Грешка при зареждане на embedder: {e}")
        return

    # 2. Инициализация на Базата
    print("[2] Инициализиране на Спиралата на Времето (TimeVectorDB)...")
    db = TimeVectorDB(base_step=1.0, k_change_factor=10.0)

    # 3. Дефиниране на въпроси (Симулация на поток от време)
    questions = [
        "Какво представлява слънчевата система?",
        "Кои са планетите в слънчевата система?",
        "Коя е най-голямата планета?",
        "Как се прави мусака?" # Внезапна промяна на темата (Trauma / High Delta)
    ]

    print("\n[3] Стартиране на теста...")
    for i, q in enumerate(questions):
        print(f"\n--- Стъпка {i+1} ---")
        print(f"Потребител: {q}")
        
        # Генериране на вектор
        emb_tensor = embedder.encode(q, convert_to_tensor=False)
        emb_np = np.array(emb_tensor)

        # Добавяне в базата (Динамично изчисляване на Z)
        vec = db.add(text=q, embedding=emb_np)
        
        print(f"-> Записано в Спиралата. Текущо Z: {db.current_z:.4f}, Theta: {vec.coordinates.theta:.4f}")
        
        # Търсене за стар контекст (ако Z > 1)
        if len(db.vectors) > 1:
            results = db.find(emb_np, threshold=0.75)
            # Филтрираме себе си
            past_results = [r for r in results if r[2].text_content != q]
            if past_results:
                print("-> Намерена връзка с миналото:")
                for r_type, sim, item in past_results[:2]:
                    print(f"   [Сходство: {sim:.2f}] {item.text_content}")
            else:
                print("-> Няма близка връзка с миналото (Нова тема).")

        # Питаме Ollama (Използвай qwen2.5:7b или qwen2.5:32b според това кое ти е заредено)
        try:
            print("-> Мислене (Ollama)...")
            start_time = time.time()
            res = ollama.chat(model='qwen2.5:7b', messages=[{'role': 'user', 'content': q}])
            end_time = time.time()
            print(f"Ollama отговор (за {end_time - start_time:.2f} сек): {res['message']['content'][:150]}...")
        except Exception as e:
            print(f"Грешка при връзка с Ollama: {e}")

    print("\n=== Тестът приключи. Времевата спирала работи. ===")

if __name__ == "__main__":
    main()
