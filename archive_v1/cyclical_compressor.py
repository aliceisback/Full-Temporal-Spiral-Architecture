# cyclical_compressor.py
from typing import List, Optional
import numpy as np
from core.temporal_memory import TemporalNode, calculate_gravity, SpiralCoordinate

class CyclicalCompressor:
    def __init__(self, similarity_threshold: float = 0.85, angular_threshold: float = 0.5):
        self.similarity_threshold = similarity_threshold
        self.angular_threshold = angular_threshold

    def process_node(self, new_node: TemporalNode, memory_bank: List[TemporalNode]) -> TemporalNode:
        """
        Обработва нов възел директно в банката с памет.
        Ако намери съвпадение, изтрива стария и добавя компресирания.
        Ако не, просто добавя новия.
        """
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
            # === Компресия ===
            merged_embedding = (new_node.semantic_embedding + best_match.semantic_embedding) / 2
            new_weight = best_match.weight + new_node.weight
            new_z = max(new_node.coordinates.z, best_match.coordinates.z)

            compressed_node = TemporalNode(
                text_content=best_match.text_content,  # Запазваме оригиналния корен
                semantic_embedding=merged_embedding,
                coordinates=SpiralCoordinate(
                    r=best_match.coordinates.r,           
                    theta=best_match.coordinates.theta,   
                    z=new_z
                ),
                weight=new_weight
            )
            
            # Подменяме възела в паметта
            memory_bank[:] = [n for n in memory_bank if n is not best_match]
            memory_bank.append(compressed_node)
            return compressed_node

        else:
            # Няма съвпадение → добавяме новия
            memory_bank.append(new_node)
            return new_node
