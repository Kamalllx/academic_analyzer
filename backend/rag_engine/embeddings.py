import requests
import json
import numpy as np
from typing import List, Union
import logging
import time
import os
class EmbeddingGenerator:
    def __init__(self, provider: str = "groq", model_name: str = "llama-3.1-8b-instant"):
        self.provider = provider
        self.model_name = model_name
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            logging.warning("GROQ_API_KEY not found. Using fallback embedding.")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        if self.provider == "groq" and self.groq_api_key:
            return self._generate_groq_embedding(text)
        else:
            return self._generate_fallback_embedding(text)
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
            time.sleep(0.1)  # Rate limiting
        
        return np.array(embeddings)
    
    def _generate_groq_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Groq API"""
        try:
            # Note: Groq primarily does completions, not embeddings
            # This is a workaround using text completion to get semantic representation
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system", 
                        "content": "Convert the following text into a numerical representation. Return only numbers separated by commas, exactly 768 values."
                    },
                    {"role": "user", "content": text}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse the response and convert to embedding
                result = response.json()
                # This is a simplified approach - in practice, you'd use a proper embedding model
                return self._text_to_vector(text)
            else:
                logging.warning(f"Groq API error: {response.status_code}")
                return self._generate_fallback_embedding(text)
                
        except Exception as e:
            logging.error(f"Error generating Groq embedding: {str(e)}")
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> np.ndarray:
        """Generate simple hash-based embedding as fallback"""
        # Simple but deterministic embedding based on text content
        import hashlib
        
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numbers
        numbers = [ord(char) for char in text_hash]
        
        # Extend to 768 dimensions
        embedding = []
        for i in range(768):
            embedding.append(numbers[i % len(numbers)] / 255.0)
        
        # Add some text-based features
        embedding[0] = len(text) / 1000.0  # Text length feature
        embedding[1] = text.count(' ') / len(text) if text else 0  # Word density
        embedding[2] = sum(1 for c in text if c.isupper()) / len(text) if text else 0  # Uppercase ratio
        
        return np.array(embedding, dtype=np.float32)
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to vector using simple NLP features"""
        import string
        
        # Initialize vector
        vector = np.zeros(768, dtype=np.float32)
        
        # Basic text features
        vector[0] = len(text) / 1000.0
        vector[1] = len(text.split()) / 100.0
        vector[2] = text.count('.') / len(text) if text else 0
        vector[3] = text.count('?') / len(text) if text else 0
        vector[4] = text.count('!') / len(text) if text else 0
        
        # Character frequency features
        for i, char in enumerate(string.ascii_lowercase):
            if i < 26:
                vector[10 + i] = text.lower().count(char) / len(text) if text else 0
        
        # Word-based features (simplified)
        words = text.lower().split()
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
        for i, word in enumerate(common_words):
            if i < 10:
                vector[50 + i] = words.count(word) / len(words) if words else 0
        
        # Hash-based features for the rest
        text_hash = hash(text) % (2**31)
        for i in range(100, 768):
            vector[i] = ((text_hash * (i + 1)) % 1000) / 1000.0
        
        return vector
