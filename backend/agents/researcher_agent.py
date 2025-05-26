import os
import requests
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import re

class ResearcherAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        
        # Research databases and sources
        self.research_sources = {
            "academic": ["Google Scholar", "PubMed", "IEEE Xplore", "ACM Digital Library"],
            "educational": ["Khan Academy", "Coursera", "edX", "MIT OpenCourseWare"],
            "technical": ["Stack Overflow", "GitHub", "Documentation sites", "Technical blogs"],
            "general": ["Wikipedia", "Britannica", "Educational websites"]
        }
    
    def suggest_related_resources(self, topic: str, source_preference: str = "mixed") -> Dict:
        """Suggest related research resources and papers"""
        if not self.groq_api_key:
            return self._generate_fallback_resources(topic)
        
        try:
            prompt = f"""As a research assistant, suggest valuable resources for studying: "{topic}"

Provide:
1. Key subtopics to explore
2. Recommended academic papers or publications (include realistic titles and authors)
3. Online courses or tutorials
4. Practical applications or case studies
5. Related concepts worth investigating

Format your response as structured recommendations that would help a student research this topic thoroughly.

Research Suggestions:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a knowledgeable research assistant who helps students find relevant academic resources."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
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
                suggestions = result['choices'][0]['message']['content'].strip()
                
                return {
                    "topic": topic,
                    "suggestions": suggestions,
                    "research_sources": self._get_relevant_sources(topic),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_resources(topic)
                
        except Exception as e:
            logging.error(f"Error generating research suggestions: {str(e)}")
            return self._generate_fallback_resources(topic)
    
    def analyze_research_gaps(self, existing_knowledge: List[str], target_topic: str) -> Dict:
        """Identify knowledge gaps and suggest research directions"""
        if not self.groq_api_key:
            return self._generate_fallback_gap_analysis(existing_knowledge, target_topic)
        
        try:
            knowledge_summary = ", ".join(existing_knowledge)
            
            prompt = f"""Analyze knowledge gaps for research planning.

Current knowledge areas: {knowledge_summary}
Target research topic: {target_topic}

Identify:
1. Knowledge gaps that need to be filled
2. Prerequisites that should be studied first
3. Advanced areas to explore later
4. Interdisciplinary connections
5. Practical applications to investigate

Provide a structured analysis for effective research planning.

Gap Analysis:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a research strategist who helps identify knowledge gaps and plan learning paths."},
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
                analysis = result['choices'][0]['message']['content'].strip()
                
                return {
                    "target_topic": target_topic,
                    "current_knowledge": existing_knowledge,
                    "gap_analysis": analysis,
                    "priority_areas": self._extract_priority_areas(analysis),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_gap_analysis(existing_knowledge, target_topic)
                
        except Exception as e:
            logging.error(f"Error in gap analysis: {str(e)}")
            return self._generate_fallback_gap_analysis(existing_knowledge, target_topic)
    
    def generate_research_methodology(self, research_question: str, domain: str) -> Dict:
        """Suggest research methodology for a given question"""
        if not self.groq_api_key:
            return self._generate_fallback_methodology(research_question, domain)
        
        try:
            prompt = f"""Design a research methodology for this question:
Research Question: {research_question}
Domain: {domain}

Provide:
1. Research approach (qualitative, quantitative, mixed methods)
2. Data collection methods
3. Analysis techniques
4. Timeline and milestones
5. Potential challenges and solutions
6. Expected outcomes

Create a practical methodology that a student could follow.

Research Methodology:"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a research methodology expert who designs practical research approaches for students."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
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
                methodology = result['choices'][0]['message']['content'].strip()
                
                return {
                    "research_question": research_question,
                    "domain": domain,
                    "methodology": methodology,
                    "research_type": self._classify_research_type(research_question),
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return self._generate_fallback_methodology(research_question, domain)
                
        except Exception as e:
            logging.error(f"Error generating methodology: {str(e)}")
            return self._generate_fallback_methodology(research_question, domain)
    
    def find_similar_studies(self, topic: str, keywords: List[str]) -> List[Dict]:
        """Find similar studies and related work (simulated)"""
        # This would integrate with real academic databases in a production system
        similar_studies = []
        
        # Generate plausible study suggestions based on topic and keywords
        study_templates = [
            {
                "title": f"A Comprehensive Analysis of {topic} in Modern Applications",
                "authors": "Smith, J., Johnson, M., & Williams, R.",
                "year": 2023,
                "abstract": f"This study examines various aspects of {topic} with focus on {', '.join(keywords[:2])}...",
                "relevance_score": 0.95
            },
            {
                "title": f"Comparative Study of {topic} Methodologies",
                "authors": "Brown, A., Davis, L., & Miller, K.",
                "year": 2022,
                "abstract": f"An empirical comparison of different approaches to {topic}...",
                "relevance_score": 0.88
            },
            {
                "title": f"Recent Advances in {topic}: A Survey",
                "authors": "Wilson, T., Anderson, P., & Taylor, S.",
                "year": 2024,
                "abstract": f"This survey covers recent developments in {topic} research...",
                "relevance_score": 0.92
            }
        ]
        
        for template in study_templates:
            # Customize based on keywords
            for keyword in keywords:
                if keyword.lower() in topic.lower():
                    template["relevance_score"] += 0.05
        
        return study_templates
    
    def _get_relevant_sources(self, topic: str) -> List[str]:
        """Get relevant research sources based on topic"""
        topic_lower = topic.lower()
        sources = []
        
        # Academic sources for research topics
        if any(word in topic_lower for word in ['machine learning', 'artificial intelligence', 'computer science']):
            sources.extend(self.research_sources["technical"])
            sources.extend(["arXiv", "NeurIPS", "ICML"])
        
        # Medical/health topics
        if any(word in topic_lower for word in ['health', 'medicine', 'biology']):
            sources.extend(["PubMed", "Nature", "Science"])
        
        # Business/economics topics
        if any(word in topic_lower for word in ['business', 'economics', 'finance']):
            sources.extend(["Harvard Business Review", "Journal of Finance", "Economic Journal"])
        
        # Default academic sources
        sources.extend(self.research_sources["academic"][:2])
        sources.extend(self.research_sources["educational"][:2])
        
        return list(set(sources))  # Remove duplicates
    
    def _extract_priority_areas(self, analysis_text: str) -> List[str]:
        """Extract priority areas from gap analysis"""
        # Simple extraction based on common patterns
        priority_indicators = ["priority", "important", "essential", "critical", "key", "fundamental"]
        
        sentences = analysis_text.split('.')
        priority_areas = []
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in priority_indicators):
                # Extract the main concept from the sentence
                words = sentence.strip().split()
                if len(words) > 3:
                    priority_areas.append(sentence.strip())
        
        return priority_areas[:5]  # Return top 5
    
    def _classify_research_type(self, research_question: str) -> str:
        """Classify the type of research based on the question"""
        question_lower = research_question.lower()
        
        if any(word in question_lower for word in ['how many', 'what percentage', 'measure', 'count']):
            return "quantitative"
        elif any(word in question_lower for word in ['why', 'how', 'experience', 'understand']):
            return "qualitative"
        elif any(word in question_lower for word in ['compare', 'relationship', 'correlation']):
            return "comparative"
        elif any(word in question_lower for word in ['predict', 'forecast', 'model']):
            return "predictive"
        else:
            return "exploratory"
    
    def _generate_fallback_resources(self, topic: str) -> Dict:
        """Generate basic research suggestions when API is unavailable"""
        suggestions = f"""Research Resources for {topic}:

Key Areas to Explore:
- Fundamental concepts and definitions
- Current trends and developments
- Historical background and evolution
- Practical applications and case studies
- Future directions and challenges

Recommended Source Types:
- Academic journals and papers
- Educational courses and tutorials
- Professional documentation
- Industry reports and whitepapers
- Expert interviews and presentations

Research Strategy:
1. Start with broad overview sources
2. Identify key researchers and institutions
3. Focus on recent publications (last 2-3 years)
4. Look for systematic reviews and meta-analyses
5. Explore interdisciplinary connections
"""
        
        return {
            "topic": topic,
            "suggestions": suggestions,
            "research_sources": self._get_relevant_sources(topic),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_fallback_gap_analysis(self, existing_knowledge: List[str], target_topic: str) -> Dict:
        """Generate basic gap analysis when API is unavailable"""
        analysis = f"""Knowledge Gap Analysis for {target_topic}:

Current Knowledge Areas: {', '.join(existing_knowledge)}

Identified Gaps:
1. Missing foundational concepts that bridge current knowledge to target topic
2. Lack of practical application examples
3. Limited understanding of advanced concepts
4. Need for current industry perspectives
5. Insufficient hands-on experience

Recommended Learning Path:
1. Review and strengthen foundational concepts
2. Study connecting theories and principles
3. Explore practical applications and case studies
4. Investigate advanced topics and cutting-edge research
5. Engage in hands-on projects and exercises

Priority Areas:
- Strengthen weak foundational areas first
- Focus on practical applications
- Stay updated with recent developments
"""
        
        return {
            "target_topic": target_topic,
            "current_knowledge": existing_knowledge,
            "gap_analysis": analysis,
            "priority_areas": ["Foundational concepts", "Practical applications", "Recent developments"],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_fallback_methodology(self, research_question: str, domain: str) -> Dict:
        """Generate basic methodology when API is unavailable"""
        methodology = f"""Research Methodology for: {research_question}

1. Research Approach:
   - Exploratory study to understand the topic comprehensively
   - Mixed methods approach combining literature review and analysis

2. Data Collection:
   - Literature review of relevant sources
   - Analysis of existing case studies
   - Collection of current examples and applications

3. Analysis Techniques:
   - Thematic analysis of collected information
   - Comparative analysis of different approaches
   - Synthesis of findings and insights

4. Timeline:
   - Week 1-2: Literature review and background research
   - Week 3-4: Data collection and analysis
   - Week 5-6: Synthesis and conclusion development

5. Expected Outcomes:
   - Comprehensive understanding of the research question
   - Identification of key factors and relationships
   - Practical insights and recommendations
"""
        
        return {
            "research_question": research_question,
            "domain": domain,
            "methodology": methodology,
            "research_type": self._classify_research_type(research_question),
            "generated_at": datetime.now().isoformat()
        }
