import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import json

class DashboardGenerator:
    def __init__(self, mongo_handler):
        self.mongo_handler = mongo_handler
        self.color_palette = px.colors.qualitative.Set3
    
    def generate_user_dashboard(self, user_id: str) -> Dict:
        """Generate comprehensive dashboard data for a user"""
        try:
            # Get user data
            user_interactions = self.mongo_handler.get_user_interactions(user_id)
            user_documents = self.mongo_handler.get_user_documents(user_id)
            learning_sessions = self.mongo_handler.get_user_learning_sessions(user_id)
            
            if not user_interactions:
                return {"message": "No data available for dashboard generation"}
            
            # Generate dashboard components
            dashboard_data = {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "charts": {
                    "activity_timeline": self._create_activity_timeline(user_interactions),
                    "subject_distribution": self._create_subject_distribution(user_interactions),
                    "learning_progress": self._create_learning_progress_chart(user_interactions),
                    "question_complexity": self._create_complexity_analysis(user_interactions),
                    "study_patterns": self._create_study_patterns(learning_sessions),
                    "document_usage": self._create_document_usage_chart(user_interactions, user_documents),
                    "performance_metrics": self._create_performance_metrics(user_interactions)
                },
                "summary_stats": self._generate_summary_stats(user_interactions, user_documents, learning_sessions)
            }
            
            return dashboard_data
            
        except Exception as e:
            logging.error(f"Error generating user dashboard: {str(e)}")
            return {"error": str(e)}
    
    def _create_activity_timeline(self, interactions: List[Dict]) -> Dict:
        """Create activity timeline chart"""
        try:
            df = pd.DataFrame(interactions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # Daily activity counts
            daily_activity = df.groupby('date').size().reset_index(name='questions_count')
            daily_activity['date'] = pd.to_datetime(daily_activity['date'])
            
            fig = px.line(
                daily_activity, 
                x='date', 
                y='questions_count',
                title='Daily Learning Activity',
                labels={'questions_count': 'Questions Asked', 'date': 'Date'}
            )
            
            fig.update_traces(line_color='#1f77b4', line_width=3)
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Questions Asked",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "line",
                "insights": self._analyze_activity_pattern(daily_activity)
            }
            
        except Exception as e:
            logging.error(f"Error creating activity timeline: {str(e)}")
            return {"error": str(e)}
    
    def _create_subject_distribution(self, interactions: List[Dict]) -> Dict:
        """Create subject distribution pie chart"""
        try:
            df = pd.DataFrame(interactions)
            subject_counts = df['subject'].value_counts() if 'subject' in df.columns else pd.Series()
            
            if subject_counts.empty:
                return {"message": "No subject data available"}
            
            fig = px.pie(
                values=subject_counts.values,
                names=subject_counts.index,
                title='Study Focus by Subject',
                color_discrete_sequence=self.color_palette
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(template='plotly_white')
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "pie",
                "insights": [
                    f"Most studied subject: {subject_counts.index[0]} ({subject_counts.iloc[0]} questions)",
                    f"Total subjects covered: {len(subject_counts)}",
                    f"Study diversity score: {round(1 - (subject_counts.iloc[0] / subject_counts.sum()), 2)}"
                ]
            }
            
        except Exception as e:
            logging.error(f"Error creating subject distribution: {str(e)}")
            return {"error": str(e)}
    
    def _create_learning_progress_chart(self, interactions: List[Dict]) -> Dict:
        """Create learning progress over time"""
        try:
            df = pd.DataFrame(interactions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['year'] = df['timestamp'].dt.year
            df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
            
            # Weekly complexity progression
            weekly_complexity = df.groupby('year_week')['complexity_score'].mean().reset_index()
            weekly_questions = df.groupby('year_week').size().reset_index(name='question_count')
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Question Complexity Over Time', 'Questions Asked Per Week'),
                vertical_spacing=0.1
            )
            
            # Complexity trend
            fig.add_trace(
                go.Scatter(
                    x=weekly_complexity['year_week'],
                    y=weekly_complexity['complexity_score'],
                    mode='lines+markers',
                    name='Avg Complexity',
                    line=dict(color='#ff7f0e', width=3)
                ),
                row=1, col=1
            )
            
            # Question count bars
            fig.add_trace(
                go.Bar(
                    x=weekly_questions['year_week'],
                    y=weekly_questions['question_count'],
                    name='Questions Count',
                    marker_color='#2ca02c'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title='Learning Progress Analysis',
                template='plotly_white',
                height=600
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "subplot",
                "insights": self._analyze_learning_progress(weekly_complexity, weekly_questions)
            }
            
        except Exception as e:
            logging.error(f"Error creating learning progress chart: {str(e)}")
            return {"error": str(e)}
    
    def _create_complexity_analysis(self, interactions: List[Dict]) -> Dict:
        """Create question complexity analysis"""
        try:
            df = pd.DataFrame(interactions)
            
            if 'complexity_score' not in df.columns:
                return {"message": "No complexity data available"}
            
            # Complexity distribution histogram
            fig = px.histogram(
                df,
                x='complexity_score',
                nbins=20,
                title='Question Complexity Distribution',
                labels={'complexity_score': 'Complexity Score', 'count': 'Number of Questions'}
            )
            
            fig.update_traces(marker_color='#9467bd', opacity=0.7)
            fig.update_layout(
                xaxis_title="Complexity Score (0-1)",
                yaxis_title="Number of Questions",
                template='plotly_white'
            )
            
            # Add average line
            avg_complexity = df['complexity_score'].mean()
            fig.add_vline(
                x=avg_complexity,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Average: {avg_complexity:.2f}"
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "histogram",
                "insights": [
                    f"Average complexity: {avg_complexity:.2f}",
                    f"Complexity range: {df['complexity_score'].min():.2f} - {df['complexity_score'].max():.2f}",
                    f"Most common complexity level: {self._get_complexity_level(avg_complexity)}"
                ]
            }
            
        except Exception as e:
            logging.error(f"Error creating complexity analysis: {str(e)}")
            return {"error": str(e)}
    
    def _create_study_patterns(self, sessions: List[Dict]) -> Dict:
        """Create study patterns analysis"""
        try:
            if not sessions:
                return {"message": "No learning session data available"}
            
            df = pd.DataFrame(sessions)
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['hour'] = df['start_time'].dt.hour
            df['day_of_week'] = df['start_time'].dt.day_name()
            
            # Hourly patterns
            hourly_pattern = df.groupby('hour').size().reset_index(name='session_count')
            
            # Day of week patterns
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_pattern = df.groupby('day_of_week').size().reindex(day_order).reset_index(name='session_count')
            
            # Create combined chart
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Study Hours Pattern', 'Weekly Study Pattern'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Hourly pattern
            fig.add_trace(
                go.Bar(
                    x=hourly_pattern['hour'],
                    y=hourly_pattern['session_count'],
                    name='Sessions by Hour',
                    marker_color='#17becf'
                ),
                row=1, col=1
            )
            
            # Daily pattern
            fig.add_trace(
                go.Bar(
                    x=daily_pattern['day_of_week'],
                    y=daily_pattern['session_count'],
                    name='Sessions by Day',
                    marker_color='#bcbd22'
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title='Study Patterns Analysis',
                template='plotly_white',
                showlegend=False
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "study_patterns",
                "insights": self._analyze_study_patterns(hourly_pattern, daily_pattern)
            }
            
        except Exception as e:
            logging.error(f"Error creating study patterns: {str(e)}")
            return {"error": str(e)}
    
    def _create_document_usage_chart(self, interactions: List[Dict], documents: List[Dict]) -> Dict:
        """Create document usage analysis"""
        try:
            df_interactions = pd.DataFrame(interactions)
            df_documents = pd.DataFrame(documents)
            
            if df_interactions.empty or df_documents.empty:
                return {"message": "Insufficient document data"}
            
            # Document usage frequency
            doc_usage = df_interactions['document_id'].value_counts().head(10)
            
            # Map document IDs to filenames
            doc_mapping = dict(zip(df_documents['document_id'], df_documents['filename']))
            doc_names = [doc_mapping.get(doc_id, doc_id)[:30] + "..." if len(doc_mapping.get(doc_id, doc_id)) > 30 else doc_mapping.get(doc_id, doc_id) for doc_id in doc_usage.index]
            
            fig = px.bar(
                x=doc_usage.values,
                y=doc_names,
                orientation='h',
                title='Most Used Documents',
                labels={'x': 'Number of Questions', 'y': 'Documents'}
            )
            
            fig.update_traces(marker_color='#e377c2')
            fig.update_layout(
                template='plotly_white',
                yaxis={'categoryorder': 'total ascending'}
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "horizontal_bar",
                "insights": [
                    f"Most used document: {doc_names[0] if doc_names else 'N/A'}",
                    f"Total documents accessed: {len(doc_usage)}",
                    f"Average questions per document: {doc_usage.mean():.1f}"
                ]
            }
            
        except Exception as e:
            logging.error(f"Error creating document usage chart: {str(e)}")
            return {"error": str(e)}
    
    def _create_performance_metrics(self, interactions: List[Dict]) -> Dict:
        """Create performance metrics gauge charts"""
        try:
            df = pd.DataFrame(interactions)
            
            # Calculate metrics
            avg_complexity = df['complexity_score'].mean() if 'complexity_score' in df.columns else 0.5
            avg_satisfaction = df['satisfaction_rating'].mean() if 'satisfaction_rating' in df.columns else 3.5
            engagement_score = min(len(df) / 100, 1.0)  # Normalize by expected activity
            
            # Create gauge charts
            fig = make_subplots(
                rows=1, cols=3,
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=("Question Complexity", "Satisfaction Rating", "Engagement Level")
            )
            
            # Complexity gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=avg_complexity,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Complexity"},
                    gauge={
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.3], 'color': "lightgray"},
                            {'range': [0.3, 0.7], 'color': "gray"},
                            {'range': [0.7, 1], 'color': "darkgray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.8
                        }
                    }
                ),
                row=1, col=1
            )
            
            # Satisfaction gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=avg_satisfaction,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Satisfaction"},
                    gauge={
                        'axis': {'range': [None, 5]},
                        'bar': {'color': "green"},
                        'steps': [
                            {'range': [0, 2], 'color': "lightgray"},
                            {'range': [2, 4], 'color': "gray"},
                            {'range': [4, 5], 'color': "darkgray"}
                        ]
                    }
                ),
                row=1, col=2
            )
            
            # Engagement gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=engagement_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Engagement"},
                    gauge={
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "orange"},
                        'steps': [
                            {'range': [0, 0.3], 'color': "lightgray"},
                            {'range': [0.3, 0.7], 'color': "gray"},
                            {'range': [0.7, 1], 'color': "darkgray"}
                        ]
                    }
                ),
                row=1, col=3
            )
            
            fig.update_layout(height=400, template='plotly_white')
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "gauges",
                "metrics": {
                    "complexity_score": round(avg_complexity, 2),
                    "satisfaction_score": round(avg_satisfaction, 2),
                    "engagement_score": round(engagement_score, 2)
                }
            }
            
        except Exception as e:
            logging.error(f"Error creating performance metrics: {str(e)}")
            return {"error": str(e)}
    
    def _generate_summary_stats(self, interactions: List[Dict], documents: List[Dict], sessions: List[Dict]) -> Dict:
        """Generate summary statistics"""
        try:
            return {
                "total_questions": len(interactions),
                "total_documents": len(documents),
                "total_sessions": len(sessions),
                "avg_questions_per_session": round(len(interactions) / max(len(sessions), 1), 1),
                "study_streak_days": self._calculate_study_streak(interactions),
                "most_active_day": self._get_most_active_day(interactions),
                "learning_velocity": self._calculate_learning_velocity(interactions)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_activity_pattern(self, daily_activity: pd.DataFrame) -> List[str]:
        """Analyze activity patterns"""
        insights = []
        
        if daily_activity.empty:
            return ["No activity data available"]
        
        max_day = daily_activity.loc[daily_activity['questions_count'].idxmax()]
        avg_questions = daily_activity['questions_count'].mean()
        
        insights.append(f"Most active day: {max_day['date'].strftime('%Y-%m-%d')} ({max_day['questions_count']} questions)")
        insights.append(f"Average daily questions: {avg_questions:.1f}")
        
        # Trend analysis
        recent_avg = daily_activity.tail(7)['questions_count'].mean()
        if recent_avg > avg_questions * 1.2:
            insights.append("📈 Activity trending upward recently")
        elif recent_avg < avg_questions * 0.8:
            insights.append("📉 Activity has decreased recently")
        else:
            insights.append("➡️ Activity level is stable")
        
        return insights
    
    def _analyze_learning_progress(self, complexity_data: pd.DataFrame, question_data: pd.DataFrame) -> List[str]:
        """Analyze learning progress"""
        insights = []
        
        if not complexity_data.empty:
            complexity_trend = complexity_data['complexity_score'].iloc[-3:].mean() - complexity_data['complexity_score'].iloc[:3].mean()
            if complexity_trend > 0.1:
                insights.append("🎓 Question complexity is increasing - showing learning progression")
            elif complexity_trend < -0.1:
                insights.append("📚 Focusing on foundational concepts recently")
            else:
                insights.append("📊 Consistent complexity level maintained")
        
        if not question_data.empty:
            avg_questions = question_data['question_count'].mean()
            recent_questions = question_data.tail(4)['question_count'].mean()
            
            if recent_questions > avg_questions * 1.3:
                insights.append("🔥 High engagement period - excellent study momentum")
            elif recent_questions < avg_questions * 0.7:
                insights.append("😴 Lower activity recently - consider setting study goals")
        
        return insights
    
    def _analyze_study_patterns(self, hourly: pd.DataFrame, daily: pd.DataFrame) -> List[str]:
        """Analyze study patterns"""
        insights = []
        
        if not hourly.empty:
            peak_hour = hourly.loc[hourly['session_count'].idxmax(), 'hour']
            insights.append(f"Peak study time: {peak_hour}:00 - {peak_hour+1}:00")
        
        if not daily.empty:
            peak_day = daily.loc[daily['session_count'].idxmax(), 'day_of_week']
            insights.append(f"Most productive day: {peak_day}")
            
            weekend_study = daily[daily['day_of_week'].isin(['Saturday', 'Sunday'])]['session_count'].sum()
            weekday_study = daily[~daily['day_of_week'].isin(['Saturday', 'Sunday'])]['session_count'].sum()
            
            if weekend_study > weekday_study:
                insights.append("🏠 Prefers weekend study sessions")
            else:
                insights.append("📅 More active during weekdays")
        
        return insights
    
    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level description"""
        if score < 0.3:
            return "Basic"
        elif score < 0.7:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _calculate_study_streak(self, interactions: List[Dict]) -> int:
        """Calculate current study streak in days"""
        if not interactions:
            return 0
        
        df = pd.DataFrame(interactions)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        unique_dates = sorted(df['date'].unique(), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for date in unique_dates:
            if date == current_date or (current_date - date).days == streak + 1:
                streak += 1
                current_date = date
            else:
                break
        
        return streak
    
    def _get_most_active_day(self, interactions: List[Dict]) -> str:
        """Get most active day of the week"""
        if not interactions:
            return "No data"
        
        df = pd.DataFrame(interactions)
        df['day'] = pd.to_datetime(df['timestamp']).dt.day_name()
        return df['day'].mode().iloc[0] if not df['day'].mode().empty else "No data"
    
    def _calculate_learning_velocity(self, interactions: List[Dict]) -> float:
        """Calculate learning velocity (questions per day)"""
        if not interactions:
            return 0.0
        
        df = pd.DataFrame(interactions)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        date_range = (df['date'].max() - df['date'].min()).days + 1
        return round(len(interactions) / max(date_range, 1), 2)
