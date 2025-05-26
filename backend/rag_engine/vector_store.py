import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict, Any
import logging

class VectorStore:
    def __init__(self, dimension: int = 768, index_path: str = "data/faiss_index"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.metadata = []
        self.chunk_texts = []
        
        # Load existing index if available
        self._load_index()
    
    def add_vectors(self, vectors: np.ndarray, texts: List[str], metadata: List[Dict]):
        """Add vectors to the index with associated metadata"""
        try:
            # Normalize vectors for cosine similarity
            vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            
            # Add to FAISS index
            self.index.add(vectors.astype('float32'))
            
            # Store metadata and texts
            self.metadata.extend(metadata)
            self.chunk_texts.extend(texts)
            
            # Save updated index
            self._save_index()
            
            logging.info(f"Added {len(vectors)} vectors to index")
            
        except Exception as e:
            logging.error(f"Error adding vectors: {str(e)}")
            raise
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> Tuple[List[str], List[Dict], List[float]]:
        """Search for similar vectors"""
        try:
            if self.index.ntotal == 0:
                return [], [], []
            
            # Normalize query vector
            query_vector = query_vector / np.linalg.norm(query_vector, keepdims=True)
            
            # Search
            scores, indices = self.index.search(query_vector.astype('float32'), top_k)
            
            # Retrieve results
            results_texts = []
            results_metadata = []
            results_scores = []
            
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunk_texts):
                    results_texts.append(self.chunk_texts[idx])
                    results_metadata.append(self.metadata[idx])
                    results_scores.append(float(score))
            
            return results_texts, results_metadata, results_scores
            
        except Exception as e:
            logging.error(f"Error searching vectors: {str(e)}")
            return [], [], []
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Save metadata and texts
            with open(f"{self.index_path}_metadata.pkl", 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'chunk_texts': self.chunk_texts
                }, f)
                
        except Exception as e:
            logging.error(f"Error saving index: {str(e)}")
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                
                with open(f"{self.index_path}_metadata.pkl", 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data['metadata']
                    self.chunk_texts = data['chunk_texts']
                
                logging.info(f"Loaded index with {self.index.ntotal} vectors")
                
        except Exception as e:
            logging.error(f"Error loading index: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'total_documents': len(set(meta.get('document_id', '') for meta in self.metadata))
        }
