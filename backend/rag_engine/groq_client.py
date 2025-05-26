import os
import requests
import json
import logging
from typing import Optional

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        if not self.api_key:
            logging.warning("GROQ_API_KEY not found. Responses will be basic.")
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate an answer using Groq's Llama model"""
        if not self.api_key:
            return self._generate_fallback_answer(question, context)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Based on the following context, answer the question accurately and concisely.

Context:
{context}

Question: {question}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain enough information, say so
- Provide a clear, well-structured answer
- Include relevant details from the context

Answer:"""

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3,
                "top_p": 0.9
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                return answer
            else:
                logging.error(f"Groq API error: {response.status_code} - {response.text}")
                return self._generate_fallback_answer(question, context)
                
        except Exception as e:
            logging.error(f"Error calling Groq API: {str(e)}")
            return self._generate_fallback_answer(question, context)
    
    def _generate_fallback_answer(self, question: str, context: str) -> str:
        """Generate a basic answer when Groq API is not available"""
        # Simple keyword matching approach
        question_words = set(question.lower().split())
        context_sentences = context.split('.')
        
        # Find most relevant sentences
        relevant_sentences = []
        for sentence in context_sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0:
                relevant_sentences.append((sentence.strip(), overlap))
        
        # Sort by relevance
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            # Combine top relevant sentences
            answer_parts = [sent[0] for sent in relevant_sentences[:2]]
            answer = ". ".join(answer_parts)
            return f"Based on the available context: {answer}"
        else:
            return "I found some potentially relevant information, but cannot provide a specific answer to your question based on the available context."
    
    def generate_explanation(self, topic: str, complexity_level: str = "intermediate") -> str:
        """Generate an educational explanation"""
        if not self.api_key:
            return f"Here's a basic explanation of {topic}. For more detailed information, please ensure your Groq API key is configured."
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Provide a clear, educational explanation of "{topic}" at a {complexity_level} level.

Requirements:
- Make it accessible and easy to understand
- Include key concepts and principles
- Use examples when helpful
- Structure the response logically
- Keep it concise but informative

Explanation:"""

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.4
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Here's a basic explanation of {topic}. For more detailed information, please check your API configuration."
                
        except Exception as e:
            logging.error(f"Error generating explanation: {str(e)}")
            return f"Unable to generate explanation for {topic} at this time."
