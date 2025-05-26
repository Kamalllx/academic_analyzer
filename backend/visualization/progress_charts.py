import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class ProgressChartGenerator:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_learning_progress_chart(self, user_data: List[Dict]) -> Dict:
        """Create comprehensive learning progress visualization"""
        try:
            if not user_data:
                return {"message": "No learning data available"}
            
            df = pd.DataFrame(user_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['week'] = df['timestamp'].dt.isocalendar().week
            df['month'] = df['timestamp'].dt.to_period('M')
            
            # Create multi-panel progress chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Daily Question Count',
                    'Question Complexity Over Time',
                    'Weekly Learning Velocity',
                    'Subject Focus Distribution'
                ),
                specs=[
                    [{"type": "scatter"}, {"type": "scatter"}],
                    [{"type": "bar"}, {"type": "pie"}]
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Daily question count
            daily_counts = df.groupby('date').size().reset_index(name='count')
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])
            
            fig.add_trace(
                go.Scatter(
                    x=daily_counts['date'],
                    y=daily_counts['count'],
                    mode='lines+markers',
                    name='Daily Questions',
                    line=dict(color='#1f77b4', width=2),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            # Question complexity over time
            if 'complexity_score' in df.columns:
                daily_complexity = df.groupby('date')['complexity_score'].mean().reset_index()
                daily_complexity['date'] = pd.to_datetime(daily_complexity['date'])
                
                fig.add_trace(
                    go.Scatter(
                        x=daily_complexity['date'],
                        y=daily_complexity['complexity_score'],
                        mode='lines+markers',
                        name='Avg Complexity',
                        line=dict(color='#ff7f0e', width=2)
                    ),
                    row=1, col=2
                )
            
            # Weekly learning velocity
            weekly_data = df.groupby(['week']).agg({
                'timestamp': 'count',
                'complexity_score': 'mean' if 'complexity_score' in df.columns else lambda x: 0.5
            }).reset_index()
            weekly_data.columns = ['week', 'questions', 'avg_complexity']
            
            fig.add_trace(
                go.Bar(
                    x=weekly_data['week'],
                    y=weekly_data['questions'],
                    name='Weekly Questions',
                    marker_color='#2ca02c'
                ),
                row=2, col=1
            )
            
            # Subject distribution
            if 'subject' in df.columns:
                subject_counts = df['subject'].value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=subject_counts.index,
                        values=subject_counts.values,
                        name="Subject Focus",
                        textinfo='percent+label'
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(
                title='Learning Progress Dashboard',
                height=800,
                showlegend=False,
                template='plotly_white'
            )
            
            # Generate insights
            insights = self._analyze_progress_trends(df)
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "progress_dashboard",
                "insights": insights,
                "summary_metrics": self._calculate_progress_metrics(df)
            }
            
        except Exception as e:
            logging.error(f"Error creating learning progress chart: {str(e)}")
            return {"error": str(e)}
    
    def create_knowledge_growth_chart(self, assessment_data: List[Dict]) -> Dict:
        """Create knowledge growth over time chart"""
        try:
            if not assessment_data:
                return {"message": "No assessment data available"}
            
            df = pd.DataFrame(assessment_data)
            df['assessment_date'] = pd.to_datetime(df['assessment_date'])
            df = df.sort_values('assessment_date')
            
            # Calculate cumulative knowledge growth
            subjects = df['subject'].unique()
            
            fig = go.Figure()
            
            for subject in subjects:
                subject_data = df[df['subject'] == subject].copy()
                subject_data['cumulative_score'] = subject_data['score_percentage'].expanding().mean()
                
                fig.add_trace(
                    go.Scatter(
                        x=subject_data['assessment_date'],
                        y=subject_data['cumulative_score'],
                        mode='lines+markers',
                        name=subject,
                        line=dict(width=3)
                    )
                )
            
            fig.update_layout(
                title='Knowledge Growth by Subject',
                xaxis_title='Date',
                yaxis_title='Cumulative Average Score (%)',
                template='plotly_white',
                hovermode='x unified'
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "knowledge_growth",
                "insights": self._analyze_knowledge_growth(df)
            }
            
        except Exception as e:
            logging.error(f"Error creating knowledge growth chart: {str(e)}")
            return {"error": str(e)}
    
    def create_study_efficiency_chart(self, session_data: List[Dict]) -> Dict:
        """Create study efficiency analysis chart"""
        try:
            if not session_data:
                return {"message": "No session data available"}
            
            df = pd.DataFrame(session_data)
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['efficiency_score'] = df['questions_count'] / df['duration_minutes']
            
            # Create efficiency analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Study Efficiency Over Time',
                    'Session Duration vs Questions',
                    'Efficiency by Time of Day',
                    'Weekly Efficiency Pattern'
                ),
                specs=[
                    [{"type": "scatter"}, {"type": "scatter"}],
                    [{"type": "bar"}, {"type": "bar"}]
                ]
            )
            
            # Efficiency over time
            fig.add_trace(
                go.Scatter(
                    x=df['start_time'],
                    y=df['efficiency_score'],
                    mode='lines+markers',
                    name='Efficiency Score',
                    line=dict(color='#9467bd')
                ),
                row=1, col=1
            )
            
            # Duration vs Questions scatter
            fig.add_trace(
                go.Scatter(
                    x=df['duration_minutes'],
                    y=df['questions_count'],
                    mode='markers',
                    name='Session Data',
                    marker=dict(color='#17becf', size=8)
                ),
                row=1, col=2
            )
            
            # Efficiency by hour
            df['hour'] = df['start_time'].dt.hour
            hourly_efficiency = df.groupby('hour')['efficiency_score'].mean()
            
            fig.add_trace(
                go.Bar(
                    x=hourly_efficiency.index,
                    y=hourly_efficiency.values,
                    name='Hourly Efficiency',
                    marker_color='#bcbd22'
                ),
                row=2, col=1
            )
            
            # Weekly pattern
            df['day_of_week'] = df['start_time'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_efficiency = df.groupby('day_of_week')['efficiency_score'].mean().reindex(day_order)
            
            fig.add_trace(
                go.Bar(
                    x=weekly_efficiency.index,
                    y=weekly_efficiency.values,
                    name='Daily Efficiency',
                    marker_color='#ff7f0e'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Study Efficiency Analysis',
                height=800,
                template='plotly_white',
                showlegend=False
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "efficiency_analysis",
                "insights": self._analyze_study_efficiency(df),
                "efficiency_metrics": {
                    "avg_efficiency": round(df['efficiency_score'].mean(), 3),
                    "best_hour": hourly_efficiency.idxmax(),
                    "best_day": weekly_efficiency.idxmax(),
                    "peak_efficiency": round(df['efficiency_score'].max(), 3)
                }
            }
            
        except Exception as e:
            logging.error(f"Error creating study efficiency chart: {str(e)}")
            return {"error": str(e)}
    
    def create_goal_tracking_chart(self, goals: List[Dict], actual_data: List[Dict]) -> Dict:
        """Create goal tracking visualization"""
        try:
            # Simulate goal tracking (in real implementation, use actual goal data)
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            
            # Create sample goals and actual performance
            daily_goal = 5  # questions per day
            weekly_goal = 30  # questions per week
            
            df_actual = pd.DataFrame(actual_data)
            if not df_actual.empty:
                df_actual['timestamp'] = pd.to_datetime(df_actual['timestamp'])
                df_actual['date'] = df_actual['timestamp'].dt.date
                daily_actual = df_actual.groupby('date').size().reset_index(name='actual_questions')
                daily_actual['date'] = pd.to_datetime(daily_actual['date'])
            else:
                daily_actual = pd.DataFrame({'date': dates, 'actual_questions': np.random.randint(0, 10, len(dates))})
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Daily Goal vs Actual Performance', 'Weekly Progress'),
                vertical_spacing=0.15
            )
            
            # Daily goal tracking
            fig.add_trace(
                go.Scatter(
                    x=daily_actual['date'],
                    y=[daily_goal] * len(daily_actual),
                    mode='lines',
                    name='Daily Goal',
                    line=dict(color='red', dash='dash', width=2)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_actual['date'],
                    y=daily_actual['actual_questions'],
                    mode='lines+markers',
                    name='Actual Performance',
                    line=dict(color='green', width=2),
                    fill='tonexty'
                ),
                row=1, col=1
            )
            
            # Weekly progress
            daily_actual['week'] = daily_actual['date'].dt.isocalendar().week
            weekly_actual = daily_actual.groupby('week')['actual_questions'].sum().reset_index()
            
            fig.add_trace(
                go.Bar(
                    x=weekly_actual['week'],
                    y=weekly_actual['actual_questions'],
                    name='Weekly Actual',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=weekly_actual['week'],
                    y=[weekly_goal] * len(weekly_actual),
                    mode='lines',
                    name='Weekly Goal',
                    line=dict(color='red', dash='dash', width=3)
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title='Goal Tracking Dashboard',
                height=700,
                template='plotly_white'
            )
            
            # Calculate goal achievement
            goal_achievement = {
                "daily_goal_achievement": round((daily_actual['actual_questions'] >= daily_goal).mean() * 100, 1),
                "average_daily_performance": round(daily_actual['actual_questions'].mean(), 1),
                "weekly_goal_achievement": round((weekly_actual['actual_questions'] >= weekly_goal).mean() * 100, 1),
                "streak_days": self._calculate_streak(daily_actual, daily_goal)
            }
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "goal_tracking",
                "achievement_metrics": goal_achievement,
                "insights": self._analyze_goal_progress(daily_actual, daily_goal, weekly_actual, weekly_goal)
            }
            
        except Exception as e:
            logging.error(f"Error creating goal tracking chart: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_progress_trends(self, df: pd.DataFrame) -> List[str]:
        """Analyze learning progress trends"""
        insights = []
        
        if df.empty:
            return ["No data available for analysis"]
        
        # Activity trend
        df_sorted = df.sort_values('timestamp')
        recent_activity = df_sorted.tail(7)
        older_activity = df_sorted.head(7) if len(df_sorted) > 7 else df_sorted
        
        recent_avg = len(recent_activity) / 7
        older_avg = len(older_activity) / 7
        
        if recent_avg > older_avg * 1.2:
            insights.append("📈 Learning activity is trending upward")
        elif recent_avg < older_avg * 0.8:
            insights.append("📉 Learning activity has decreased recently")
        else:
            insights.append("📊 Learning activity is stable")
        
        # Complexity progression
        if 'complexity_score' in df.columns:
            complexity_trend = df['complexity_score'].rolling(window=5).mean()
            if complexity_trend.iloc[-1] > complexity_trend.iloc[0]:
                insights.append("🎯 Question complexity is increasing over time")
            else:
                insights.append("📚 Maintaining consistent complexity level")
        
        # Consistency analysis
        daily_counts = df.groupby(df['timestamp'].dt.date).size()
        consistency_score = 1 - (daily_counts.std() / daily_counts.mean()) if daily_counts.mean() > 0 else 0
        
        if consistency_score > 0.7:
            insights.append("✅ Very consistent learning pattern")
        elif consistency_score > 0.5:
            insights.append("🎯 Moderately consistent learning")
        else:
            insights.append("⚡ Learning pattern varies significantly")
        
        return insights
    
    def _analyze_knowledge_growth(self, df: pd.DataFrame) -> List[str]:
        """Analyze knowledge growth patterns"""
        insights = []
        
        if df.empty:
            return ["No assessment data available"]
        
        # Overall improvement
        first_scores = df.groupby('subject')['score_percentage'].first()
        last_scores = df.groupby('subject')['score_percentage'].last()
        improvements = last_scores - first_scores
        
        improving_subjects = improvements[improvements > 5].index.tolist()
        declining_subjects = improvements[improvements < -5].index.tolist()
        
        if improving_subjects:
            insights.append(f"📈 Strong improvement in: {', '.join(improving_subjects)}")
        
        if declining_subjects:
            insights.append(f"📉 Need attention in: {', '.join(declining_subjects)}")
        
        # Best performing subject
        avg_scores = df.groupby('subject')['score_percentage'].mean()
        best_subject = avg_scores.idxmax()
        insights.append(f"🏆 Strongest subject: {best_subject} ({avg_scores[best_subject]:.1f}% avg)")
        
        return insights
    
    def _analyze_study_efficiency(self, df: pd.DataFrame) -> List[str]:
        """Analyze study efficiency patterns"""
        insights = []
        
        if df.empty:
            return ["No session data available"]
        
        # Best time analysis
        hourly_efficiency = df.groupby(df['start_time'].dt.hour)['efficiency_score'].mean()
        best_hour = hourly_efficiency.idxmax()
        insights.append(f"🕐 Most efficient study time: {best_hour}:00-{best_hour+1}:00")
        
        # Session length optimization
        duration_efficiency = df.groupby(pd.cut(df['duration_minutes'], bins=5))['efficiency_score'].mean()
        optimal_duration = duration_efficiency.idxmax()
        insights.append(f"⏱️ Optimal session length: {optimal_duration}")
        
        # Efficiency trend
        if len(df) > 5:
            recent_efficiency = df.tail(5)['efficiency_score'].mean()
            older_efficiency = df.head(5)['efficiency_score'].mean()
            
            if recent_efficiency > older_efficiency * 1.1:
                insights.append("📈 Study efficiency is improving")
            elif recent_efficiency < older_efficiency * 0.9:
                insights.append("📉 Study efficiency has declined recently")
            else:
                insights.append("📊 Study efficiency is stable")
        
        return insights
    
    def _analyze_goal_progress(self, daily_data: pd.DataFrame, daily_goal: int, 
                             weekly_data: pd.DataFrame, weekly_goal: int) -> List[str]:
        """Analyze goal achievement progress"""
        insights = []
        
        # Daily goal analysis
        daily_achievement = (daily_data['actual_questions'] >= daily_goal).mean() * 100
        insights.append(f"🎯 Daily goal achievement: {daily_achievement:.1f}%")
        
        # Weekly goal analysis
        weekly_achievement = (weekly_data['actual_questions'] >= weekly_goal).mean() * 100
        insights.append(f"📅 Weekly goal achievement: {weekly_achievement:.1f}%")
        
        # Recent performance
        recent_performance = daily_data.tail(7)['actual_questions'].mean()
        if recent_performance >= daily_goal:
            insights.append("🔥 Recent performance exceeds daily goals")
        else:
            insights.append("💪 Need to increase daily activity to meet goals")
        
        # Streak analysis
        streak = self._calculate_streak(daily_data, daily_goal)
        if streak > 0:
            insights.append(f"🏃 Current goal achievement streak: {streak} days")
        else:
            insights.append("🎯 Focus on building a consistent achievement streak")
        
        return insights
    
    def _calculate_progress_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive progress metrics"""
        if df.empty:
            return {}
        
        return {
            "total_questions": len(df),
            "study_days": df['timestamp'].dt.date.nunique(),
            "avg_daily_questions": round(len(df) / max(df['timestamp'].dt.date.nunique(), 1), 2),
            "learning_velocity": round(len(df) / max((df['timestamp'].max() - df['timestamp'].min()).days, 1), 2),
            "complexity_progression": round(df['complexity_score'].tail(10).mean() - df['complexity_score'].head(10).mean(), 3) if 'complexity_score' in df.columns else 0,
            "consistency_score": round(1 - (df.groupby(df['timestamp'].dt.date).size().std() / df.groupby(df['timestamp'].dt.date).size().mean()), 3) if df.groupby(df['timestamp'].dt.date).size().mean() > 0 else 0
        }
    
    def _calculate_streak(self, daily_data: pd.DataFrame, goal: int) -> int:
        """Calculate current goal achievement streak"""
        if daily_data.empty:
            return 0
        
        daily_data_sorted = daily_data.sort_values('date', ascending=False)
        streak = 0
        
        for _, row in daily_data_sorted.iterrows():
            if row['actual_questions'] >= goal:
                streak += 1
            else:
                break
        
        return streak
