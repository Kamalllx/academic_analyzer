import os
import requests
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

class TutorAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        # Conversation memory for context
        self.conversation_history = {}
        
    def provide_explanation(self, question: str, answer: str, user_id: str = "default") -> str:
        """Provide additional explanation and educational context"""
        if not self.groq_api_key:
            return self._generate_fallback_explanation(question, answer)
        
        try:
            # Get conversation context
            context = self._get_conversation_context(user_id)
            
            prompt = f"""As an educational tutor, provide additional explanation and learning guidance.

Previous context: {context}

Student's question: {question}
System answer: {answer}

As a tutor, provide:
1. Additional clarification if needed
2. Related concepts the student should know
3. Suggested follow-up questions for deeper learning
4. Learning tips or study strategies

Keep your response educational, encouraging, and concise (max 3 paragraphs).

Tutor response:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an experienced educational tutor who helps students learn effectively."},
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
                tutor_response = result['choices'][0]['message']['content'].strip()
                
                # Update conversation history
                self._update_conversation_history(user_id, question, answer, tutor_response)
                
                return tutor_response
            else:
                logging.error(f"Groq API error: {response.status_code}")
                return self._generate_fallback_explanation(question, answer)
                
        except Exception as e:
            logging.error(f"Error in tutor explanation: {str(e)}")
            return self._generate_fallback_explanation(question, answer)
    
    def chat_with_student(self, message: str, user_id: str = "default") -> str:
        """Have a conversational interaction with the student"""
        if not self.groq_api_key:
            return self._generate_fallback_chat_response(message)
        
        try:
            context = self._get_conversation_context(user_id)
            
            prompt = f"""You are having a conversation with a student. Previous context: {context}

Student message: {message}

Respond as a helpful, encouraging tutor. If the student:
- Asks for help: Provide guidance and ask clarifying questions
- Shows confusion: Break down concepts into simpler parts
- Needs motivation: Provide encouragement and study tips
- Asks about study strategies: Give practical advice

Keep responses conversational and supportive.

Response:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a friendly, knowledgeable tutor who supports student learning."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.5
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                chat_response = result['choices'][0]['message']['content'].strip()
                
                # Update conversation history
                self._update_chat_history(user_id, message, chat_response)
                
                return chat_response
            else:
                return self._generate_fallback_chat_response(message)
                
        except Exception as e:
            logging.error(f"Error in tutor chat: {str(e)}")
            return self._generate_fallback_chat_response(message)
    
    def suggest_study_plan(self, topics: List[str], difficulty_level: str = "intermediate") -> Dict:
        """Generate a personalized study plan"""
        if not self.groq_api_key:
            return self._generate_fallback_study_plan(topics)
        
        try:
            topics_str = ", ".join(topics)
            
            prompt = f"""Create a structured study plan for these topics: {topics_str}
Difficulty level: {difficulty_level}

Provide a study plan with:
1. Learning sequence (order of topics)
2. Estimated time for each topic
3. Recommended activities (reading, practice, review)
4. Key milestones and checkpoints
5. Tips for effective learning

Format as a structured plan that's practical and achievable.

Study Plan:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an educational planning expert who creates effective study schedules."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                plan_text = result['choices'][0]['message']['content'].strip()
                
                return {
                    "study_plan": plan_text,
                    "topics": topics,
                    "difficulty_level": difficulty_level,
                    "created_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_study_plan(topics)
                
        except Exception as e:
            logging.error(f"Error generating study plan: {str(e)}")
            return self._generate_fallback_study_plan(topics)
    
    def _get_conversation_context(self, user_id: str) -> str:
        """Get recent conversation context for continuity"""
        if user_id not in self.conversation_history:
            return "This is the beginning of our conversation."
        
        history = self.conversation_history[user_id]
        if not history:
            return "This is the beginning of our conversation."
        
        # Get last 2 interactions for context
        recent_context = []
        for interaction in history[-2:]:
            recent_context.append(f"Q: {interaction['question'][:100]}...")
            recent_context.append(f"A: {interaction['answer'][:100]}...")
        
        return " ".join(recent_context)
    
    def _update_conversation_history(self, user_id: str, question: str, answer: str, tutor_response: str):
        """Update conversation history for context"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "question": question,
            "answer": answer,
            "tutor_response": tutor_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 interactions to manage memory
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def _update_chat_history(self, user_id: str, message: str, response: str):
        """Update chat history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "student_message": message,
            "tutor_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 interactions
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def _generate_fallback_explanation(self, question: str, answer: str) -> str:
        """Generate basic explanation when API is unavailable"""
        explanations = [
            f"This question about '{question[:50]}...' touches on important concepts. Consider exploring related topics to deepen your understanding.",
            f"Great question! The answer provided gives you the key information. Think about how this concept connects to other things you've learned.",
            f"This is a valuable learning opportunity. Try to think of examples or applications of this concept in real situations.",
            f"Excellent inquiry! Consider creating summary notes about this topic and reviewing similar concepts for better retention."
        ]
        
        import random
        return random.choice(explanations)
    
    def _generate_fallback_chat_response(self, message: str) -> str:
        """Generate basic chat response when API is unavailable"""
        if "help" in message.lower():
            return "I'm here to help! Can you tell me more specifically what you're struggling with? Breaking down problems into smaller parts often makes them easier to tackle."
        elif "study" in message.lower():
            return "For effective studying, I recommend: 1) Set clear goals, 2) Break sessions into focused chunks, 3) Take regular breaks, 4) Test yourself frequently. What subject are you studying?"
        elif any(word in message.lower() for word in ["confused", "don't understand", "unclear"]):
            return "It's completely normal to feel confused when learning something new! Let's break it down step by step. What specific part is unclear to you?"
        else:
            return "I'm here to support your learning journey! Feel free to ask me about any concepts you're studying, or let me know how I can help you learn more effectively."
    
    def _generate_fallback_study_plan(self, topics: List[str]) -> Dict:
        """Generate basic study plan when API is unavailable"""
        plan_text = f"""Basic Study Plan for {len(topics)} topics:

Week 1-2: Foundation Building
- Start with basic concepts in each topic
- Create summary notes
- Daily 30-minute study sessions

Week 3-4: Deep Dive
- Focus on more complex aspects
- Practice problems and exercises
- Weekly review sessions

Week 5-6: Integration and Review
- Connect concepts across topics
- Create mind maps
- Self-testing and assessment

Tips:
- Study consistently rather than cramming
- Take breaks every 25-30 minutes
- Teach concepts to others to reinforce learning
- Use multiple learning methods (reading, writing, discussing)
"""
        
        return {
            "study_plan": plan_text,
            "topics": topics,
            "difficulty_level": "adaptive",
            "created_at": datetime.now().isoformat()
        }
