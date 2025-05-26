import os
import numpy as np
from typing import List, Tuple, Dict, Any
import logging

from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .groq_client import GroqClient

class QueryEngine:
    def __init__(self, mongo_handler):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.mongo_handler = mongo_handler
        self.groq_client = GroqClient()
    
    def add_document(self, doc_id: str, text_chunks: List[str], metadata: Dict):
        """Add a document to the vector store"""
        try:
            # Generate embeddings for all chunks
            embeddings = self.embedding_generator.generate_embeddings_batch(text_chunks)
            
            # Create metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(text_chunks):
                chunk_meta = metadata.copy()
                chunk_meta.update({
                    'document_id': doc_id,
                    'chunk_id': f"{doc_id}_{i}",
                    'chunk_index': i,
                    'chunk_text': chunk[:200] + "..." if len(chunk) > 200 else chunk
                })
                chunk_metadata.append(chunk_meta)
            
            # Add to vector store
            self.vector_store.add_vectors(embeddings, text_chunks, chunk_metadata)
            
            logging.info(f"Added document {doc_id} with {len(text_chunks)} chunks")
            
        except Exception as e:
            logging.error(f"Error adding document: {str(e)}")
            raise
    
    def process_query(self, question: str, document_id: str = 'all') -> Tuple[str, List[Dict]]:
        """Process a user query and return answer with sources"""
        try:
            # Generate embedding for the question
            query_embedding = self.embedding_generator.generate_embedding(question)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search for relevant chunks
            relevant_texts, metadata, scores = self.vector_store.search(
                query_embedding, top_k=5
            )
            
            if not relevant_texts:
                return "I couldn't find relevant information to answer your question. Please try rephrasing or upload more documents.", []
            
            # Filter by document_id if specified
            if document_id != 'all':
                filtered_data = []
                for text, meta, score in zip(relevant_texts, metadata, scores):
                    if meta.get('document_id') == document_id:
                        filtered_data.append((text, meta, score))
                
                if filtered_data:
                    relevant_texts, metadata, scores = zip(*filtered_data)
                else:
                    return f"No relevant information found in the specified document.", []
            
            # Create context from relevant chunks
            context = "\n\n".join(relevant_texts[:3])  # Use top 3 chunks
            
            # Generate answer using Groq
            answer = self.groq_client.generate_answer(question, context)
            
            # Prepare source information
            sources = []
            for meta, score in zip(metadata[:3], scores[:3]):
                sources.append({
                    'document': meta.get('filename', 'Unknown'),
                    'chunk_id': meta.get('chunk_id', 'Unknown'),
                    'relevance_score': round(score, 3),
                    'preview': meta.get('chunk_text', 'No preview available')
                })
            
            return answer, sources
            
        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return f"An error occurred while processing your question: {str(e)}", []
    
    def get_document_stats(self) -> Dict:
        """Get statistics about indexed documents"""
        return self.vector_store.get_stats()
