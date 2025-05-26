from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class Document:
    """Document data model"""
    document_id: str
    filename: str
    subject: str
    user_id: str
    upload_date: datetime
    complexity_score: float
    chunk_count: int
    file_size_mb: float
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "subject": self.subject,
            "user_id": self.user_id,
            "upload_date": self.upload_date.isoformat(),
            "complexity_score": self.complexity_score,
            "chunk_count": self.chunk_count,
            "file_size_mb": self.file_size_mb,
            "status": self.status,
            "metadata": self.metadata
        }

@dataclass
class UserInteraction:
    """User interaction data model"""
    interaction_id: str
    user_id: str
    question: str
    answer: str
    document_id: str
    timestamp: datetime
    question_type: str = "general"
    complexity_score: float = 0.5
    satisfaction_rating: Optional[int] = None
    response_time_seconds: Optional[int] = None
    sources: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "interaction_id": self.interaction_id,
            "user_id": self.user_id,
            "question": self.question,
            "answer": self.answer,
            "document_id": self.document_id,
            "timestamp": self.timestamp.isoformat(),
            "question_type": self.question_type,
            "complexity_score": self.complexity_score,
            "satisfaction_rating": self.satisfaction_rating,
            "response_time_seconds": self.response_time_seconds,
            "sources": self.sources
        }

@dataclass
class LearningSession:
    """Learning session data model"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    questions_count: int
    documents_accessed: List[str]
    subjects_studied: List[str]
    session_type: str = "study"
    productivity_score: float = 0.0
    engagement_score: float = 0.0
    
    @property
    def duration_minutes(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 60
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "questions_count": self.questions_count,
            "documents_accessed": self.documents_accessed,
            "subjects_studied": self.subjects_studied,
            "session_type": self.session_type,
            "productivity_score": self.productivity_score,
            "engagement_score": self.engagement_score
        }

@dataclass
class ConceptRelationship:
    """Concept relationship data model"""
    relationship_id: str
    concept_a: str
    concept_b: str
    relationship_type: str
    strength: float
    bidirectional: bool = False
    confidence_score: float = 0.5
    source: str = "analysis"
    
    def to_dict(self) -> Dict:
        return {
            "relationship_id": self.relationship_id,
            "concept_a": self.concept_a,
            "concept_b": self.concept_b,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "confidence_score": self.confidence_score,
            "source": self.source
        }

@dataclass
class KnowledgeAssessment:
    """Knowledge assessment data model"""
    assessment_id: str
    user_id: str
    subject: str
    assessment_type: str
    total_questions: int
    correct_answers: int
    assessment_date: datetime
    time_taken_minutes: int
    difficulty_level: str = "intermediate"
    topics_covered: List[str] = field(default_factory=list)
    
    @property
    def score_percentage(self) -> float:
        return (self.correct_answers / self.total_questions) * 100 if self.total_questions > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            "assessment_id": self.assessment_id,
            "user_id": self.user_id,
            "subject": self.subject,
            "assessment_type": self.assessment_type,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score_percentage": self.score_percentage,
            "assessment_date": self.assessment_date.isoformat(),
            "time_taken_minutes": self.time_taken_minutes,
            "difficulty_level": self.difficulty_level,
            "topics_covered": self.topics_covered
        }

@dataclass
class UserProfile:
    """User profile data model"""
    user_id: str
    username: str
    email: str
    created_date: datetime
    preferred_subjects: List[str] = field(default_factory=list)
    learning_style: str = "visual"
    difficulty_preference: str = "intermediate"
    daily_goal_minutes: int = 60
    total_study_time: int = 0
    documents_uploaded: int = 0
    questions_asked: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_date": self.created_date.isoformat(),
            "preferred_subjects": self.preferred_subjects,
            "learning_style": self.learning_style,
            "difficulty_preference": self.difficulty_preference,
            "daily_goal_minutes": self.daily_goal_minutes,
            "total_study_time": self.total_study_time,
            "documents_uploaded": self.documents_uploaded,
            "questions_asked": self.questions_asked
        }

@dataclass
class AnalyticsReport:
    """Analytics report data model"""
    report_id: str
    report_type: str
    user_id: Optional[str]
    date_range_start: datetime
    date_range_end: datetime
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "user_id": self.user_id,
            "date_range_start": self.date_range_start.isoformat(),
            "date_range_end": self.date_range_end.isoformat(),
            "metrics": self.metrics,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat()
        }

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_user_interaction(data: Dict) -> bool:
        """Validate user interaction data"""
        required_fields = ["user_id", "question", "answer", "document_id"]
        return all(field in data and data[field] for field in required_fields)
    
    @staticmethod
    def validate_document(data: Dict) -> bool:
        """Validate document data"""
        required_fields = ["filename", "subject", "user_id"]
        return all(field in data and data[field] for field in required_fields)
    
    @staticmethod
    def validate_learning_session(data: Dict) -> bool:
        """Validate learning session data"""
        required_fields = ["user_id", "start_time", "end_time"]
        return all(field in data and data[field] for field in required_fields)
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 1000) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            return ""
        
        # Remove potentially harmful characters
        sanitized = text.replace("<", "").replace(">", "").replace("&", "")
        
        # Truncate if too long
        return sanitized[:max_length] if len(sanitized) > max_length else sanitized
    
    @staticmethod
    def validate_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Validate and normalize score values"""
        try:
            score = float(score)
            return max(min_val, min(max_val, score))
        except (ValueError, TypeError):
            return (min_val + max_val) / 2  # Return midpoint if invalid

class DataTransformer:
    """Data transformation utilities"""
    
    @staticmethod
    def normalize_subject_name(subject: str) -> str:
        """Normalize subject names"""
        if not subject:
            return "General"
        
        # Capitalize first letter of each word
        return " ".join(word.capitalize() for word in subject.strip().split())
    
    @staticmethod
    def classify_question_complexity(question: str) -> str:
        """Classify question complexity level"""
        if not question:
            return "unknown"
        
        question_lower = question.lower()
        
        # Simple patterns for complexity classification
        if any(word in question_lower for word in ["what", "who", "when", "where"]):
            return "basic"
        elif any(word in question_lower for word in ["how", "why", "explain"]):
            return "intermediate"
        elif any(word in question_lower for word in ["analyze", "evaluate", "compare", "synthesize"]):
            return "advanced"
        else:
            return "intermediate"
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction (in a real implementation, use NLP libraries)
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "is", "are", "was", "were", "be", "been", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might",
            "a", "an", "this", "that", "these", "those"
        }
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return most frequent keywords (simplified)
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
