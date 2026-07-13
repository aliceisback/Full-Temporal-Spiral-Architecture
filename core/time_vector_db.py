import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class SpiralCoordinate:
    """3D координата в Спиралата на Времето"""
    r: float      # Важност на спомена (0.0 - ∞)
    theta: float  # Ъглова фаза в радиани (0 до 2π)
    z: float      # Времева координата (непрекъснато нараства)

    def angular_difference(self, other: 'SpiralCoordinate') -> float:
        """Изчислява най-късото разстояние между два ъгъла в спиралата."""
        diff = abs(self.theta - other.theta)
        return min(diff, 2 * np.pi - diff)

@dataclass
class TimeMarker:
    """Маркер за Времеви Период / Епоха (напр. Война, Бременност)"""
    name: str
    start_z: float
    embedding: np.ndarray
    weight: float = 1.0
    end_z: Optional[float] = None
    
    def is_active(self, current_z: float) -> bool:
        """Проверява дали периодът покрива текущото време."""
        if self.end_z is None:
            return current_z >= self.start_z
        return self.start_z <= current_z <= self.end_z

@dataclass
class TimeVector:
    """Носител на Делта промяната във времето, не на дублирана информация."""
    text_content: str
    semantic_embedding: np.ndarray
    coordinates: SpiralCoordinate
    weight: float = 1.0


class TimeVectorDB:
    def __init__(self, base_step: float = 1.0, k_change_factor: float = 10.0):
        self.vectors: List[TimeVector] = []
        self.markers: Dict[str, TimeMarker] = {}
        self.loops: Dict[str, Any] = {}  # За бъдещо проследяване на повторяемост
        
        self.current_z: float = 0.0
        self.base_step = base_step
        self.k_change_factor = k_change_factor

    def _calculate_step_size(self, change_intensity: float) -> float:
        """
        Динамична стъпка:
        Малко промяна (change_intensity близко до 0) -> step_size клони към base_step (бързо изкачване)
        Голяма промяна (change_intensity голямо) -> step_size става много малко (висока резолюция)
        """
        return self.base_step / (1.0 + self.k_change_factor * change_intensity)

    def add(self, text: str, embedding: np.ndarray, item_type: str = "vector", marker_name: Optional[str] = None):
        """
        Добавя нов вектор или маркер, изчислявайки динамичната времева стъпка (z) 
        базирана на делта промяната спрямо предишния спомен.
        """
        change_intensity = 0.0
        
        # Ако има предишен вектор, изчисляваме косинусовото сходство за да намерим разликата (делтата)
        if self.vectors:
            last_vector = self.vectors[-1]
            norm_new = np.linalg.norm(embedding)
            norm_last = np.linalg.norm(last_vector.semantic_embedding)
            
            if norm_new > 0 and norm_last > 0:
                cosine_sim = np.dot(embedding, last_vector.semantic_embedding) / (norm_new * norm_last)
                cosine_sim = np.clip(cosine_sim, -1.0, 1.0)
                # Разликата (intensity) е обратното на сходството
                change_intensity = max(0.0, 1.0 - cosine_sim)
                
        # Изчисляване на новото време Z
        step_size = self._calculate_step_size(change_intensity)
        self.current_z += step_size
        
        # Изчисляване на нов ъгъл (Theta) - примерно: движи се заедно със Z, създавайки цикли
        new_theta = (self.current_z % (2 * np.pi))
        
        if item_type == "marker" and marker_name:
            new_marker = TimeMarker(
                name=marker_name,
                start_z=self.current_z,
                embedding=embedding
            )
            self.markers[marker_name] = new_marker
            return new_marker
            
        elif item_type == "end_marker" and marker_name:
            if marker_name in self.markers:
                self.markers[marker_name].end_z = self.current_z
            return self.markers.get(marker_name)
            
        else:
            # Създаване на стандартен делта вектор
            coords = SpiralCoordinate(r=1.0, theta=new_theta, z=self.current_z)
            new_vector = TimeVector(text_content=text, semantic_embedding=embedding, coordinates=coords)
            self.vectors.append(new_vector)
            return new_vector

    def find(self, query_embedding: np.ndarray, threshold: float = 0.78) -> List[Any]:
        """
        Търси през всички вектори и маркери. Връща тези, които минават прага на сходство.
        """
        results = []
        norm_q = np.linalg.norm(query_embedding)
        if norm_q == 0:
            return results

        # Търсене в TimeVectors
        for vec in self.vectors:
            norm_v = np.linalg.norm(vec.semantic_embedding)
            if norm_v > 0:
                sim = np.dot(query_embedding, vec.semantic_embedding) / (norm_q * norm_v)
                if sim >= threshold:
                    results.append(("vector", sim, vec))

        # Търсене в TimeMarkers
        for name, marker in self.markers.items():
            norm_m = np.linalg.norm(marker.embedding)
            if norm_m > 0:
                sim = np.dot(query_embedding, marker.embedding) / (norm_q * norm_m)
                if sim >= threshold:
                    results.append(("marker", sim, marker))
                    
        # Сортиране по сходство низходящо
        results.sort(key=lambda x: x[1], reverse=True)
        return results
