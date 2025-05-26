import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from bson import ObjectId

class MongoDBHandler:
    def __init__(self, connection_string: str, db_name: str):
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            
            # Initialize collections
            self.documents = self.db.documents
            self.interactions = self.db.user_interactions
            self.feedback = self.db.feedback
            self.learning_sessions = self.db.learning_sessions
            self.analytics = self.db.analytics
            
            # Create indexes for better performance
            self._create_indexes()
            
            logging.info(f"Connected to MongoDB database: {db_name}")
            
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # User interactions indexes
            self.interactions.create_index([("user_id", 1), ("timestamp", -1)])
            self.interactions.create_index([("document_id", 1)])
            self.interactions.create_index([("timestamp", -1)])
            
            # Documents indexes
            self.documents.create_index([("user_id", 1)])
            self.documents.create_index([("subject", 1)])
            self.documents.create_index([("upload_date", -1)])
            
            # Feedback indexes
            self.feedback.create_index([("interaction_id", 1)])
            self.feedback.create_index([("timestamp", -1)])
            
            logging.info("Database indexes created successfully")
            
        except Exception as e:
            logging.warning(f"Could not create indexes: {str(e)}")
    
    def store_document_metadata(self, doc_id: str, filename: str, subject: str, 
                              user_id: str, chunk_count: int, complexity_score: float) -> bool:
        """Store document metadata"""
        try:
            document = {
                "document_id": doc_id,
                "filename": filename,
                "subject": subject,
                "user_id": user_id,
                "chunk_count": chunk_count,
                "complexity_score": complexity_score,
                "upload_date": datetime.now(),
                "status": "active"
            }
            
            result = self.documents.insert_one(document)
            logging.info(f"Stored document metadata: {doc_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing document metadata: {str(e)}")
            return False
    
    def store_user_interaction(self, interaction_id: str, user_id: str, question: str, 
                             answer: str, document_id: str, sources: List[Dict], 
                             timestamp: datetime) -> bool:
        """Store user interaction data"""
        try:
            interaction = {
                "interaction_id": interaction_id,
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "document_id": document_id,
                "sources": sources,
                "timestamp": timestamp,
                "question_length": len(question),
                "answer_length": len(answer),
                "source_count": len(sources)
            }
            
            result = self.interactions.insert_one(interaction)
            logging.info(f"Stored user interaction: {interaction_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing user interaction: {str(e)}")
            return False
    
    def store_feedback(self, interaction_id: str, rating: int, comments: str, timestamp: datetime) -> bool:
        """Store user feedback"""
        try:
            feedback = {
                "interaction_id": interaction_id,
                "rating": rating,
                "comments": comments,
                "timestamp": timestamp
            }
            
            result = self.feedback.insert_one(feedback)
            logging.info(f"Stored feedback for interaction: {interaction_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing feedback: {str(e)}")
            return False
    
    def get_user_interactions(self, user_id: str, start_date: datetime = None) -> List[Dict]:
        """Get user interactions within a date range"""
        try:
            query = {"user_id": user_id}
            if start_date:
                query["timestamp"] = {"$gte": start_date}
            
            interactions = list(self.interactions.find(query).sort("timestamp", -1))
            
            # Convert ObjectId to string for JSON serialization
            for interaction in interactions:
                interaction["_id"] = str(interaction["_id"])
            
            return interactions
            
        except Exception as e:
            logging.error(f"Error getting user interactions: {str(e)}")
            return []
    
    def get_recent_interactions(self, limit: int = 100) -> List[Dict]:
        """Get recent interactions across all users"""
        try:
            interactions = list(self.interactions.find().sort("timestamp", -1).limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for interaction in interactions:
                interaction["_id"] = str(interaction["_id"])
            
            return interactions
            
        except Exception as e:
            logging.error(f"Error getting recent interactions: {str(e)}")
            return []
    
    def get_user_documents(self, user_id: str) -> List[Dict]:
        """Get all documents uploaded by a user"""
        try:
            documents = list(self.documents.find({"user_id": user_id}).sort("upload_date", -1))
            
            # Convert ObjectId to string
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
            
        except Exception as e:
            logging.error(f"Error getting user documents: {str(e)}")
            return []
    
    def get_document_analytics(self, document_id: str) -> Dict:
        """Get analytics for a specific document"""
        try:
            # Get interactions for this document
            interactions = list(self.interactions.find({"document_id": document_id}))
            
            if not interactions:
                return {"message": "No interactions found for this document"}
            
            # Calculate analytics
            total_questions = len(interactions)
            unique_users = len(set(interaction["user_id"] for interaction in interactions))
            
            # Question complexity analysis
            avg_question_length = sum(interaction["question_length"] for interaction in interactions) / total_questions
            
            # Time-based patterns
            interaction_times = [interaction["timestamp"] for interaction in interactions]
            
            # Most common question patterns
            questions = [interaction["question"] for interaction in interactions]
            
            return {
                "document_id": document_id,
                "total_questions": total_questions,
                "unique_users": unique_users,
                "avg_question_length": round(avg_question_length, 2),
                "first_interaction": min(interaction_times).isoformat() if interaction_times else None,
                "last_interaction": max(interaction_times).isoformat() if interaction_times else None,
                "sample_questions": questions[:5]  # First 5 questions as samples
            }
            
        except Exception as e:
            logging.error(f"Error getting document analytics: {str(e)}")
            return {"error": str(e)}
    
    def store_learning_session(self, user_id: str, session_data: Dict) -> bool:
        """Store learning session data"""
        try:
            session = {
                "user_id": user_id,
                "start_time": session_data.get("start_time"),
                "end_time": session_data.get("end_time"),
                "duration_minutes": session_data.get("duration_minutes"),
                "questions_count": session_data.get("questions_count"),
                "documents_accessed": session_data.get("documents_accessed", []),
                "topics_covered": session_data.get("topics_covered", []),
                "session_type": session_data.get("session_type", "study"),
                "created_at": datetime.now()
            }
            
            result = self.learning_sessions.insert_one(session)
            logging.info(f"Stored learning session for user: {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing learning session: {str(e)}")
            return False
    
    def get_user_learning_sessions(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user's learning sessions"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            sessions = list(self.learning_sessions.find({
                "user_id": user_id,
                "created_at": {"$gte": start_date}
            }).sort("created_at", -1))
            
            # Convert ObjectId to string
            for session in sessions:
                session["_id"] = str(session["_id"])
            
            return sessions
            
        except Exception as e:
            logging.error(f"Error getting learning sessions: {str(e)}")
            return []
    
    def store_analytics_data(self, analytics_type: str, data: Dict) -> bool:
        """Store computed analytics data for caching"""
        try:
            analytics_record = {
                "analytics_type": analytics_type,
                "data": data,
                "computed_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=24)  # Cache for 24 hours
            }
            
            # Remove existing analytics of the same type
            self.analytics.delete_many({"analytics_type": analytics_type})
            
            # Insert new analytics
            result = self.analytics.insert_one(analytics_record)
            logging.info(f"Stored analytics data: {analytics_type}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing analytics data: {str(e)}")
            return False
    
    def get_analytics_data(self, analytics_type: str) -> Optional[Dict]:
        """Get cached analytics data"""
        try:
            analytics_record = self.analytics.find_one({
                "analytics_type": analytics_type,
                "expires_at": {"$gt": datetime.now()}
            })
            
            if analytics_record:
                return analytics_record["data"]
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error getting analytics data: {str(e)}")
            return None
    
    def get_database_stats(self) -> Dict:
        """Get overall database statistics"""
        try:
            stats = {
                "total_documents": self.documents.count_documents({}),
                "total_interactions": self.interactions.count_documents({}),
                "total_feedback_entries": self.feedback.count_documents({}),
                "total_learning_sessions": self.learning_sessions.count_documents({}),
                "unique_users": len(self.interactions.distinct("user_id")),
                "last_activity": None
            }
            
            # Get last activity
            last_interaction = self.interactions.find_one({}, sort=[("timestamp", -1)])
            if last_interaction:
                stats["last_activity"] = last_interaction["timestamp"].isoformat()
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def export_user_data(self, user_id: str) -> Dict:
        """Export all data for a specific user"""
        try:
            user_data = {
                "user_id": user_id,
                "documents": self.get_user_documents(user_id),
                "interactions": self.get_user_interactions(user_id),
                "learning_sessions": self.get_user_learning_sessions(user_id),
                "exported_at": datetime.now().isoformat()
            }
            
            return user_data
            
        except Exception as e:
            logging.error(f"Error exporting user data: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> Dict:
        """Clean up old data beyond specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old interactions
            old_interactions = self.interactions.delete_many({"timestamp": {"$lt": cutoff_date}})
            
            # Delete old learning sessions
            old_sessions = self.learning_sessions.delete_many({"created_at": {"$lt": cutoff_date}})
            
            # Delete expired analytics
            expired_analytics = self.analytics.delete_many({"expires_at": {"$lt": datetime.now()}})
            
            cleanup_stats = {
                "interactions_deleted": old_interactions.deleted_count,
                "sessions_deleted": old_sessions.deleted_count,
                "analytics_deleted": expired_analytics.deleted_count,
                "cleanup_date": datetime.now().isoformat()
            }
            
            logging.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
            return {"error": str(e)}
