import numpy as np
from core.time_vector_db import TimeVectorDB

def simulate_embedding(theme: str) -> np.ndarray:
    """Генерира фалшив (Mock) вектор, за да тестваме сходството без да зареждаме тежък AI модел."""
    np.random.seed(hash(theme) % (2**32))
    return np.random.rand(10)

def main():
    print("=== NOA Temporal Vector DB V2: Тест на Ядрото ===")
    
    db = TimeVectorDB(base_step=1.0, k_change_factor=10.0)
    
    # 1. Създаване на Времева Епоха (Маркер)
    print("\n1. Създаване на времеви период 'Бременност'...")
    db.add(text="Начало на бременност", embedding=simulate_embedding("Бременност"), item_type="marker", marker_name="Бременност")
    print(f"-> Текущо време (Z): {db.current_z:.4f}")
    
    # 2. Добавяне на обичайни, подобни спомени (Малка промяна -> Бързо време)
    print("\n2. Рутинни дни (Сходни събития -> Бързо изкачване по спиралата):")
    for i in range(3):
        # Добавяме много сходни вектори
        emb = simulate_embedding("Рутина") + np.random.rand(10)*0.1 
        vec = db.add(text=f"Спокоен ден {i+1}", embedding=emb)
        print(f"   [Ден {i+1}] Добавен. Ново Z: {db.current_z:.4f}, Theta: {vec.coordinates.theta:.4f}")
        
    # 3. Внезапна промяна (Голяма делта -> Забавяне на времето / Висока резолюция)
    print("\n3. Внезапно събитие (Коренна промяна -> Времето се 'разтяга' за висока резолюция):")
    emb_shock = simulate_embedding("Стрес или Раждане")
    vec_shock = db.add(text="Внезапни контракции!", embedding=emb_shock)
    print(f"   [Събитие] Добавено. Ново Z: {db.current_z:.4f} (Стъпката е много малка!)")
    
    # 4. Търсене в паметта
    print("\n4. Търсене в паметта за маркера 'Бременност':")
    query = simulate_embedding("Бременност")
    results = db.find(query, threshold=0.7)
    for res_type, sim, item in results:
        if res_type == "marker":
            print(f"   -> Намерен маркер: '{item.name}' (Сходство: {sim:.2f}, Активен: {item.is_active(db.current_z)})")
        else:
            print(f"   -> Намерен спомен: '{item.text_content}' (Сходство: {sim:.2f})")

if __name__ == "__main__":
    main()
