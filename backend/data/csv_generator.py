import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import logging

class CSVDatasetGenerator:
    def __init__(self):
        self.academic_subjects = [
            "Machine Learning", "Data Science", "Computer Science", "Mathematics",
            "Physics", "Chemistry", "Biology", "Psychology", "Economics", "Business",
            "Literature", "History", "Philosophy", "Engineering", "Medicine"
        ]
        
        self.question_templates = {
            "factual": [
                "What is {concept}?",
                "Define {concept}.",
                "Who invented {concept}?",
                "When was {concept} discovered?",
                "Where is {concept} used?"
            ],
            "explanatory": [
                "How does {concept} work?",
                "Why is {concept} important?",
                "Explain the process of {concept}.",
                "How do you implement {concept}?",
                "What are the steps in {concept}?"
            ],
            "analytical": [
                "Analyze the impact of {concept}.",
                "Compare {concept} with alternatives.",
                "Evaluate the effectiveness of {concept}.",
                "What are the advantages of {concept}?",
                "Assess the limitations of {concept}."
            ],
            "application": [
                "How can {concept} be applied in {domain}?",
                "Give examples of {concept} in practice.",
                "What are real-world uses of {concept}?",
                "How is {concept} implemented in industry?",
                "What are case studies of {concept}?"
            ]
        }
        
        self.concepts = {
            "Machine Learning": ["neural networks", "decision trees", "clustering", "regression", "classification"],
            "Data Science": ["data visualization", "statistical analysis", "data cleaning", "feature engineering", "hypothesis testing"],
            "Computer Science": ["algorithms", "data structures", "programming", "databases", "software engineering"],
            "Mathematics": ["calculus", "linear algebra", "statistics", "probability", "differential equations"],
            "Physics": ["quantum mechanics", "thermodynamics", "electromagnetism", "relativity", "mechanics"],
            "Chemistry": ["organic chemistry", "chemical bonding", "reaction kinetics", "thermochemistry", "electrochemistry"],
            "Biology": ["genetics", "evolution", "cell biology", "ecology", "molecular biology"],
            "Psychology": ["cognitive psychology", "behavioral psychology", "developmental psychology", "social psychology", "neuropsychology"],
            "Economics": ["microeconomics", "macroeconomics", "econometrics", "game theory", "behavioral economics"],
            "Business": ["marketing", "finance", "operations management", "strategic planning", "human resources"]
        }
    
    def generate_user_interactions_dataset(self, num_records: int = 1000, output_path: str = "data/user_interactions.csv") -> str:
        """Generate synthetic user interactions dataset"""
        try:
            interactions = []
            
            # Generate user IDs
            user_ids = [f"user_{i:04d}" for i in range(1, min(num_records // 10, 100) + 1)]
            document_ids = [f"doc_{i:04d}" for i in range(1, min(num_records // 20, 50) + 1)]
            
            for i in range(num_records):
                user_id = random.choice(user_ids)
                document_id = random.choice(document_ids)
                subject = random.choice(self.academic_subjects)
                
                # Generate question
                question_type = random.choice(list(self.question_templates.keys()))
                template = random.choice(self.question_templates[question_type])
                concept = random.choice(self.concepts.get(subject, ["general concept"]))
                domain = random.choice(self.academic_subjects)
                
                question = template.format(concept=concept, domain=domain)
                
                # Generate answer (simplified)
                answer = f"Based on the available information, {concept} refers to..."
                
                # Generate timestamp (last 90 days)
                timestamp = datetime.now() - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Generate metrics
                question_length = len(question)
                answer_length = len(answer)
                complexity_score = random.uniform(0.2, 0.9)
                satisfaction_rating = random.choice([1, 2, 3, 4, 5])
                
                interaction = {
                    "interaction_id": f"int_{i:06d}",
                    "user_id": user_id,
                    "document_id": document_id,
                    "subject": subject,
                    "question": question,
                    "answer": answer,
                    "question_type": question_type,
                    "question_length": question_length,
                    "answer_length": answer_length,
                    "complexity_score": round(complexity_score, 3),
                    "satisfaction_rating": satisfaction_rating,
                    "timestamp": timestamp.isoformat(),
                    "response_time_seconds": random.randint(2, 30)
                }
                
                interactions.append(interaction)
            
            # Create DataFrame and save
            df = pd.DataFrame(interactions)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logging.info(f"Generated {num_records} user interactions and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error generating user interactions dataset: {str(e)}")
            raise
    
    def generate_document_metadata_dataset(self, num_documents: int = 100, output_path: str = "data/document_metadata.csv") -> str:
        """Generate synthetic document metadata dataset"""
        try:
            documents = []
            
            for i in range(num_documents):
                doc_id = f"doc_{i:04d}"
                subject = random.choice(self.academic_subjects)
                
                # Generate realistic document names
                doc_types = ["Research Paper", "Textbook Chapter", "Lecture Notes", "Technical Manual", "Case Study"]
                doc_type = random.choice(doc_types)
                
                filename = f"{subject.replace(' ', '_')}_{doc_type.replace(' ', '_')}_{i+1}.pdf"
                
                # Generate metadata
                upload_date = datetime.now() - timedelta(days=random.randint(1, 365))
                complexity_score = random.uniform(0.3, 0.9)
                page_count = random.randint(10, 200)
                word_count = random.randint(5000, 50000)
                chunk_count = random.randint(20, 100)
                
                # Generate user assignment
                user_id = f"user_{random.randint(1, 50):04d}"
                
                document = {
                    "document_id": doc_id,
                    "filename": filename,
                    "subject": subject,
                    "document_type": doc_type,
                    "user_id": user_id,
                    "upload_date": upload_date.isoformat(),
                    "complexity_score": round(complexity_score, 3),
                    "page_count": page_count,
                    "word_count": word_count,
                    "chunk_count": chunk_count,
                    "file_size_mb": round(random.uniform(1.0, 50.0), 2),
                    "language": "English",
                    "status": random.choice(["active", "archived"]),
                    "download_count": random.randint(0, 100),
                    "avg_rating": round(random.uniform(3.0, 5.0), 1)
                }
                
                documents.append(document)
            
            # Create DataFrame and save
            df = pd.DataFrame(documents)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logging.info(f"Generated {num_documents} document metadata records and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error generating document metadata dataset: {str(e)}")
            raise
    
    def generate_learning_sessions_dataset(self, num_sessions: int = 500, output_path: str = "data/learning_sessions.csv") -> str:
        """Generate synthetic learning sessions dataset"""
        try:
            sessions = []
            
            user_ids = [f"user_{i:04d}" for i in range(1, 51)]
            
            for i in range(num_sessions):
                user_id = random.choice(user_ids)
                
                # Generate session timing
                start_time = datetime.now() - timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                duration_minutes = random.randint(15, 180)  # 15 minutes to 3 hours
                end_time = start_time + timedelta(minutes=duration_minutes)
                
                # Generate session metrics
                questions_count = random.randint(1, 20)
                documents_accessed = random.randint(1, 5)
                subjects = random.sample(self.academic_subjects, random.randint(1, 3))
                
                session = {
                    "session_id": f"session_{i:06d}",
                    "user_id": user_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_minutes": duration_minutes,
                    "questions_count": questions_count,
                    "documents_accessed": documents_accessed,
                    "subjects_studied": ", ".join(subjects),
                    "session_type": random.choice(["study", "research", "homework", "exam_prep"]),
                    "productivity_score": round(random.uniform(0.4, 1.0), 3),
                    "engagement_score": round(random.uniform(0.5, 1.0), 3),
                    "break_count": random.randint(0, 5),
                    "device_type": random.choice(["desktop", "laptop", "tablet", "mobile"]),
                    "completion_status": random.choice(["completed", "interrupted", "ongoing"])
                }
                
                sessions.append(session)
            
            # Create DataFrame and save
            df = pd.DataFrame(sessions)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logging.info(f"Generated {num_sessions} learning sessions and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error generating learning sessions dataset: {str(e)}")
            raise
    
    def generate_concept_relationships_dataset(self, num_relationships: int = 200, output_path: str = "data/concept_relationships.csv") -> str:
        """Generate synthetic concept relationships dataset"""
        try:
            relationships = []
            
            all_concepts = []
            for subject, concepts in self.concepts.items():
                for concept in concepts:
                    all_concepts.append((concept, subject))
            
            relationship_types = [
                "prerequisite", "related", "similar", "opposite", "component",
                "application", "extension", "alternative", "dependent"
            ]
            
            for i in range(num_relationships):
                concept_a, subject_a = random.choice(all_concepts)
                concept_b, subject_b = random.choice(all_concepts)
                
                # Avoid self-relationships
                while concept_a == concept_b:
                    concept_b, subject_b = random.choice(all_concepts)
                
                relationship_type = random.choice(relationship_types)
                strength = round(random.uniform(0.3, 1.0), 3)
                
                relationship = {
                    "relationship_id": f"rel_{i:06d}",
                    "concept_a": concept_a,
                    "subject_a": subject_a,
                    "concept_b": concept_b,
                    "subject_b": subject_b,
                    "relationship_type": relationship_type,
                    "strength": strength,
                    "bidirectional": random.choice([True, False]),
                    "confidence_score": round(random.uniform(0.6, 1.0), 3),
                    "source": random.choice(["expert_knowledge", "data_analysis", "literature_review"]),
                    "created_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
                }
                
                relationships.append(relationship)
            
            # Create DataFrame and save
            df = pd.DataFrame(relationships)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logging.info(f"Generated {num_relationships} concept relationships and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error generating concept relationships dataset: {str(e)}")
            raise
    
    def generate_knowledge_assessments_dataset(self, num_assessments: int = 300, output_path: str = "data/knowledge_assessments.csv") -> str:
        """Generate synthetic knowledge assessments dataset"""
        try:
            assessments = []
            
            user_ids = [f"user_{i:04d}" for i in range(1, 51)]
            assessment_types = ["quiz", "practice_test", "homework", "project", "exam"]
            
            for i in range(num_assessments):
                user_id = random.choice(user_ids)
                subject = random.choice(self.academic_subjects)
                assessment_type = random.choice(assessment_types)
                
                # Generate assessment metrics
                total_questions = random.randint(10, 50)
                correct_answers = random.randint(0, total_questions)
                score_percentage = round((correct_answers / total_questions) * 100, 1)
                
                assessment_date = datetime.now() - timedelta(days=random.randint(1, 180))
                time_taken_minutes = random.randint(10, 120)
                
                assessment = {
                    "assessment_id": f"assess_{i:06d}",
                    "user_id": user_id,
                    "subject": subject,
                    "assessment_type": assessment_type,
                    "total_questions": total_questions,
                    "correct_answers": correct_answers,
                    "score_percentage": score_percentage,
                    "time_taken_minutes": time_taken_minutes,
                    "difficulty_level": random.choice(["beginner", "intermediate", "advanced"]),
                    "assessment_date": assessment_date.isoformat(),
                    "attempt_number": random.randint(1, 3),
                    "topics_covered": ", ".join(random.sample(self.concepts.get(subject, ["general"]), random.randint(1, 3))),
                    "completion_status": random.choice(["completed", "incomplete", "abandoned"]),
                    "feedback_score": random.randint(1, 5),
                    "improvement_areas": random.choice([
                        "concept understanding", "problem solving", "time management",
                        "application skills", "theoretical knowledge"
                    ])
                }
                
                assessments.append(assessment)
            
            # Create DataFrame and save
            df = pd.DataFrame(assessments)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)
            
            logging.info(f"Generated {num_assessments} knowledge assessments and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Error generating knowledge assessments dataset: {str(e)}")
            raise
    
    def generate_all_datasets(self, output_dir: str = "data") -> Dict[str, str]:
        """Generate all synthetic datasets"""
        try:
            generated_files = {}
            
            # Generate each dataset
            generated_files["user_interactions"] = self.generate_user_interactions_dataset(
                1000, f"{output_dir}/user_interactions.csv"
            )
            
            generated_files["document_metadata"] = self.generate_document_metadata_dataset(
                100, f"{output_dir}/document_metadata.csv"
            )
            
            generated_files["learning_sessions"] = self.generate_learning_sessions_dataset(
                500, f"{output_dir}/learning_sessions.csv"
            )
            
            generated_files["concept_relationships"] = self.generate_concept_relationships_dataset(
                200, f"{output_dir}/concept_relationships.csv"
            )
            
            generated_files["knowledge_assessments"] = self.generate_knowledge_assessments_dataset(
                300, f"{output_dir}/knowledge_assessments.csv"
            )
            
            logging.info(f"Generated all datasets in directory: {output_dir}")
            return generated_files
            
        except Exception as e:
            logging.error(f"Error generating all datasets: {str(e)}")
            raise

if __name__ == "__main__":
    # Generate sample datasets
    generator = CSVDatasetGenerator()
    files = generator.generate_all_datasets()
    print("Generated datasets:", files)
