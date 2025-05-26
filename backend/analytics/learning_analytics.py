import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from collections import Counter, defaultdict

class LearningAnalytics:
    def __init__(self, mongo_handler):
        self.mongo_handler = mongo_handler
    
    def analyze_learning_progress(self, user_id: str, time_range: str = "30days") -> Dict:
        """Analyze user's learning progress over time"""
        try:
            # Get user interactions
            days = self._parse_time_range(time_range)
            start_date = datetime.now() - timedelta(days=days)
            
            interactions = self.mongo_handler.get_user_interactions(user_id, start_date)
            
            if not interactions:
                return {"message": "No interactions found for analysis"}
            
            df = pd.DataFrame(interactions)
            
            # Calculate metrics
            total_questions = len(df)
            unique_documents = df['document_id'].nunique()
            avg_questions_per_day = total_questions / days
            
            # Question complexity analysis
            complexity_scores = self._analyze_question_complexity(df['question'].tolist())
            avg_complexity = np.mean(complexity_scores)
            complexity_trend = self._calculate_trend(complexity_scores)
            
            # Topic analysis
            topics = self._extract_topics_from_questions(df['question'].tolist())
            
            # Learning sessions analysis
            sessions = self._identify_learning_sessions(df)
            
            # Comprehension analysis (based on follow-up questions)
            comprehension_score = self._calculate_comprehension_score(df)
            
            return {
                "user_id": user_id,
                "time_range": time_range,
                "total_questions": total_questions,
                "unique_documents": unique_documents,
                "avg_questions_per_day": round(avg_questions_per_day, 2),
                "avg_question_complexity": round(avg_complexity, 2),
                "complexity_trend": complexity_trend,
                "comprehension_score": round(comprehension_score, 2),
                "main_topics": topics[:5],
                "learning_sessions": len(sessions),
                "avg_session_length": round(np.mean([s['duration'] for s in sessions]), 2) if sessions else 0,
                "progress_metrics": self._calculate_progress_metrics(df)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing learning progress: {str(e)}")
            return {"error": str(e)}
    
    def detect_query_patterns(self, limit: int = 100) -> Dict:
        """Detect common query patterns across all users"""
        try:
            interactions = self.mongo_handler.get_recent_interactions(limit)
            
            if not interactions:
                return {"message": "No interactions found"}
            
            df = pd.DataFrame(interactions)
            
            # Question type classification
            question_types = self._classify_question_types(df['question'].tolist())
            
            # Common topics
            all_topics = []
            for questions in df.groupby('user_id')['question'].apply(list):
                topics = self._extract_topics_from_questions(questions)
                all_topics.extend(topics)
            
            topic_frequency = Counter(all_topics)
            
            # Time-based patterns
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            hourly_activity = df.groupby('hour').size().to_dict()
            
            # Document popularity
            doc_popularity = df['document_id'].value_counts().head(10).to_dict()
            
            return {
                "question_types": dict(Counter(question_types)),
                "popular_topics": dict(topic_frequency.most_common(10)),
                "hourly_activity": hourly_activity,
                "popular_documents": doc_popularity,
                "total_analyzed": len(df)
            }
            
        except Exception as e:
            logging.error(f"Error detecting patterns: {str(e)}")
            return {"error": str(e)}
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to days"""
        if time_range.endswith('days'):
            return int(time_range.replace('days', ''))
        elif time_range.endswith('weeks'):
            return int(time_range.replace('weeks', '')) * 7
        elif time_range.endswith('months'):
            return int(time_range.replace('months', '')) * 30
        else:
            return 30  # default to 30 days
    
    def _analyze_question_complexity(self, questions: List[str]) -> List[float]:
        """Analyze complexity of questions"""
        complexity_scores = []
        
        for question in questions:
            score = 0.0
            
            # Length factor
            score += min(len(question.split()) / 20.0, 1.0)
            
            # Question words that indicate complexity
            complex_words = ['analyze', 'compare', 'evaluate', 'explain', 'why', 'how', 'relationship']
            simple_words = ['what', 'when', 'where', 'who', 'is', 'are']
            
            question_lower = question.lower()
            for word in complex_words:
                if word in question_lower:
                    score += 0.3
            
            for word in simple_words:
                if word in question_lower:
                    score += 0.1
            
            # Technical terms (simplified detection)
            if any(char.isupper() for char in question) and len(question.split()) > 3:
                score += 0.2
            
            complexity_scores.append(min(score, 1.0))
        
        return complexity_scores
    
    def _extract_topics_from_questions(self, questions: List[str]) -> List[str]:
        """Extract topics from questions using simple keyword analysis"""
        # Common academic topics/keywords
        topic_keywords = {
            'machine learning': ['machine learning', 'ml', 'algorithm', 'model', 'training'],
            'data science': ['data', 'dataset', 'analysis', 'statistics', 'visualization'],
            'programming': ['code', 'function', 'variable', 'loop', 'programming'],
            'mathematics': ['equation', 'formula', 'calculate', 'math', 'theorem'],
            'research': ['study', 'research', 'paper', 'methodology', 'findings'],
            'business': ['business', 'market', 'strategy', 'management', 'finance']
        }
        
        topics = []
        for question in questions:
            question_lower = question.lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    topics.append(topic)
                    break
            else:
                topics.append('general')
        
        return topics
    
    def _classify_question_types(self, questions: List[str]) -> List[str]:
        """Classify questions by type"""
        types = []
        
        for question in questions:
            question_lower = question.lower().strip()
            
            if question_lower.startswith(('what', 'who', 'when', 'where')):
                types.append('factual')
            elif question_lower.startswith(('how', 'why')):
                types.append('explanatory')
            elif question_lower.startswith(('compare', 'contrast', 'difference')):
                types.append('comparative')
            elif question_lower.startswith(('analyze', 'evaluate', 'assess')):
                types.append('analytical')
            elif '?' not in question:
                types.append('statement')
            else:
                types.append('other')
        
        return types
    
    def _identify_learning_sessions(self, df: pd.DataFrame) -> List[Dict]:
        """Identify learning sessions based on time gaps"""
        df_sorted = df.sort_values('timestamp')
        sessions = []
        current_session = []
        
        for _, row in df_sorted.iterrows():
            if not current_session:
                current_session = [row]
            else:
                time_diff = (pd.to_datetime(row['timestamp']) - 
                           pd.to_datetime(current_session[-1]['timestamp'])).total_seconds() / 60
                
                if time_diff <= 30:  # 30 minutes gap threshold
                    current_session.append(row)
                else:
                    # End current session
                    if len(current_session) > 1:
                        sessions.append({
                            'start_time': current_session[0]['timestamp'],
                            'end_time': current_session[-1]['timestamp'],
                            'duration': (pd.to_datetime(current_session[-1]['timestamp']) - 
                                       pd.to_datetime(current_session[0]['timestamp'])).total_seconds() / 60,
                            'questions_count': len(current_session)
                        })
                    current_session = [row]
        
        # Add last session
        if len(current_session) > 1:
            sessions.append({
                'start_time': current_session[0]['timestamp'],
                'end_time': current_session[-1]['timestamp'],
                'duration': (pd.to_datetime(current_session[-1]['timestamp']) - 
                           pd.to_datetime(current_session[0]['timestamp'])).total_seconds() / 60,
                'questions_count': len(current_session)
            })
        
        return sessions
    
    def _calculate_comprehension_score(self, df: pd.DataFrame) -> float:
        """Calculate comprehension score based on interaction patterns"""
        # Simple heuristic: fewer follow-up questions on same topic = better comprehension
        topic_questions = defaultdict(int)
        
        for _, row in df.iterrows():
            topics = self._extract_topics_from_questions([row['question']])
            for topic in topics:
                topic_questions[topic] += 1
        
        # Lower repetition = higher comprehension
        if not topic_questions:
            return 0.5
        
        avg_questions_per_topic = np.mean(list(topic_questions.values()))
        comprehension_score = max(0.0, 1.0 - (avg_questions_per_topic - 1) / 10.0)
        
        return comprehension_score
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"
        
        first_half = np.mean(values[:len(values)//2])
        second_half = np.mean(values[len(values)//2:])
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_progress_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate various progress metrics"""
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_questions = df.groupby('date').size()
        
        return {
            "consistency_score": self._calculate_consistency_score(daily_questions),
            "engagement_trend": self._calculate_trend(daily_questions.tolist()),
            "peak_activity_day": str(daily_questions.idxmax()) if not daily_questions.empty else None,
            "most_productive_days": daily_questions.nlargest(3).to_dict()
        }
    
    def _calculate_consistency_score(self, daily_questions: pd.Series) -> float:
        """Calculate how consistent the learning pattern is"""
        if len(daily_questions) < 2:
            return 0.0
        
        # Coefficient of variation (lower = more consistent)
        cv = daily_questions.std() / daily_questions.mean() if daily_questions.mean() > 0 else 1
        consistency_score = max(0.0, 1.0 - cv)
        
        return round(consistency_score, 3)
