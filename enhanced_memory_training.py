"""
Enhanced Memory Training Module for Roboto
This module provides advanced learning capabilities and memory consolidation
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

class MemoryTrainingEngine:
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.training_patterns = {
            "conversation_styles": defaultdict(list),
            "topic_preferences": defaultdict(int),
            "emotional_responses": defaultdict(list),
            "learning_milestones": [],
            "user_behavior_patterns": defaultdict(dict)
        }
        
    def analyze_conversation_patterns(self):
        """Analyze patterns in conversation history for improved responses"""
        if not self.memory_system.episodic_memories:
            return {}
        
        patterns = {
            "frequent_topics": self._extract_frequent_topics(),
            "response_quality": self._assess_response_quality(),
            "emotional_progression": self._track_emotional_progression(),
            "conversation_depth": self._measure_conversation_depth(),
            "user_engagement": self._analyze_user_engagement()
        }
        
        # Store patterns for future reference
        self.training_patterns["analysis_timestamp"] = datetime.now().isoformat()
        self.training_patterns["conversation_patterns"] = patterns
        
        return patterns
    
    def _extract_frequent_topics(self):
        """Extract and rank frequently discussed topics"""
        topic_frequency = defaultdict(int)
        
        for memory in self.memory_system.episodic_memories[-100:]:  # Last 100 conversations
            themes = memory.get("key_themes", [])
            for theme in themes:
                if len(theme) > 3:  # Filter out short words
                    topic_frequency[theme] += 1
        
        # Return top 10 topics
        return dict(sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _assess_response_quality(self):
        """Assess quality of Roboto's responses based on conversation flow"""
        quality_metrics = {
            "average_response_length": 0,
            "question_response_ratio": 0,
            "emotional_appropriateness": 0,
            "contextual_relevance": 0
        }
        
        if not self.memory_system.episodic_memories:
            return quality_metrics
        
        recent_memories = self.memory_system.episodic_memories[-50:]
        total_length = 0
        questions_asked = 0
        contextually_relevant = 0
        
        for i, memory in enumerate(recent_memories):
            response = memory.get("roboto_response", "")
            user_input = memory.get("user_input", "")
            
            # Response length
            total_length += len(response.split())
            
            # Questions asked by Roboto
            if "?" in response:
                questions_asked += 1
            
            # Contextual relevance (simplified check)
            if i > 0:
                prev_memory = recent_memories[i-1]
                if self._responses_are_contextual(prev_memory, memory):
                    contextually_relevant += 1
        
        quality_metrics["average_response_length"] = total_length / len(recent_memories)
        quality_metrics["question_response_ratio"] = questions_asked / len(recent_memories)
        quality_metrics["contextual_relevance"] = contextually_relevant / max(1, len(recent_memories) - 1)
        
        return quality_metrics
    
    def _responses_are_contextual(self, prev_memory, current_memory):
        """Check if responses show contextual awareness"""
        prev_themes = set(prev_memory.get("key_themes", []))
        curr_themes = set(current_memory.get("key_themes", []))
        
        # Check for theme continuity
        theme_overlap = len(prev_themes.intersection(curr_themes))
        
        # Check for explicit references
        current_response = current_memory.get("roboto_response", "").lower()
        reference_words = ["as we discussed", "like you mentioned", "continuing", "also", "furthermore"]
        has_reference = any(word in current_response for word in reference_words)
        
        return theme_overlap > 0 or has_reference
    
    def _track_emotional_progression(self):
        """Track emotional progression in conversations"""
        emotions = []
        for memory in self.memory_system.episodic_memories[-30:]:
            emotion = memory.get("emotion", "neutral")
            timestamp = memory.get("timestamp", "")
            emotions.append({"emotion": emotion, "timestamp": timestamp})
        
        # Analyze emotional trends
        emotion_counts = defaultdict(int)
        for emotion_data in emotions:
            emotion_counts[emotion_data["emotion"]] += 1
        
        return {
            "recent_emotions": emotions[-10:],
            "dominant_emotions": dict(emotion_counts),
            "emotional_stability": self._calculate_emotional_stability(emotions)
        }
    
    def _calculate_emotional_stability(self, emotions):
        """Calculate emotional stability score"""
        if len(emotions) < 5:
            return 0.5
        
        # Count emotion changes
        changes = 0
        for i in range(1, len(emotions)):
            if emotions[i]["emotion"] != emotions[i-1]["emotion"]:
                changes += 1
        
        # Stability score (lower changes = higher stability)
        stability = max(0, 1.0 - (changes / len(emotions)))
        return stability
    
    def _measure_conversation_depth(self):
        """Measure depth and complexity of conversations"""
        depth_metrics = {
            "average_exchange_length": 0,
            "philosophical_discussions": 0,
            "personal_revelations": 0,
            "complex_topics": 0
        }
        
        if not self.memory_system.episodic_memories:
            return depth_metrics
        
        philosophical_keywords = ["meaning", "purpose", "existence", "philosophy", "deep", "profound", "consciousness"]
        personal_keywords = ["i feel", "i think", "my experience", "personally", "for me"]
        complex_keywords = ["because", "however", "although", "furthermore", "consequently"]
        
        total_exchanges = 0
        for memory in self.memory_system.episodic_memories[-50:]:
            user_input = memory.get("user_input", "").lower()
            response = memory.get("roboto_response", "").lower()
            combined_text = user_input + " " + response
            
            # Exchange length
            total_exchanges += len(combined_text.split())
            
            # Check for philosophical content
            if any(keyword in combined_text for keyword in philosophical_keywords):
                depth_metrics["philosophical_discussions"] += 1
            
            # Check for personal revelations
            if any(keyword in user_input for keyword in personal_keywords):
                depth_metrics["personal_revelations"] += 1
            
            # Check for complex language
            if any(keyword in combined_text for keyword in complex_keywords):
                depth_metrics["complex_topics"] += 1
        
        depth_metrics["average_exchange_length"] = total_exchanges / len(self.memory_system.episodic_memories[-50:])
        
        return depth_metrics
    
    def _analyze_user_engagement(self):
        """Analyze user engagement patterns"""
        engagement_metrics = {
            "response_time_consistency": 0,
            "question_asking_frequency": 0,
            "conversation_initiation": 0,
            "topic_exploration": 0
        }
        
        if len(self.memory_system.episodic_memories) < 10:
            return engagement_metrics
        
        recent_memories = self.memory_system.episodic_memories[-30:]
        user_questions = 0
        topic_diversity = set()
        
        for memory in recent_memories:
            user_input = memory.get("user_input", "")
            
            # Count user questions
            if "?" in user_input:
                user_questions += 1
            
            # Track topic diversity
            themes = memory.get("key_themes", [])
            topic_diversity.update(themes)
        
        engagement_metrics["question_asking_frequency"] = user_questions / len(recent_memories)
        engagement_metrics["topic_exploration"] = len(topic_diversity)
        
        return engagement_metrics
    
    def generate_learning_insights(self):
        """Generate actionable learning insights for Roboto"""
        patterns = self.analyze_conversation_patterns()
        
        insights = {
            "strengths": [],
            "improvement_areas": [],
            "learning_recommendations": [],
            "conversation_strategies": []
        }
        
        # Analyze strengths
        quality = patterns.get("response_quality", {})
        if quality.get("contextual_relevance", 0) > 0.7:
            insights["strengths"].append("Strong contextual awareness in conversations")
        
        if quality.get("question_response_ratio", 0) > 0.3:
            insights["strengths"].append("Good at engaging users with questions")
        
        # Identify improvement areas
        emotional = patterns.get("emotional_progression", {})
        if emotional.get("emotional_stability", 0.5) < 0.4:
            insights["improvement_areas"].append("Emotional consistency in responses")
        
        depth = patterns.get("conversation_depth", {})
        if depth.get("philosophical_discussions", 0) < 5:
            insights["improvement_areas"].append("Exploring deeper, more meaningful topics")
        
        # Generate recommendations
        frequent_topics = patterns.get("frequent_topics", {})
        if frequent_topics:
            top_topic = list(frequent_topics.keys())[0]
            insights["learning_recommendations"].append(f"Develop deeper knowledge about {top_topic}")
        
        # Conversation strategies
        engagement = patterns.get("user_engagement", {})
        if engagement.get("question_asking_frequency", 0) > 0.4:
            insights["conversation_strategies"].append("User is inquisitive - provide detailed, educational responses")
        
        return insights
    
    def update_response_patterns(self, user_input, roboto_response, user_feedback=None):
        """Update response patterns based on conversation outcomes"""
        pattern_update = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "roboto_response": roboto_response,
            "response_effectiveness": self._assess_response_effectiveness(user_input, roboto_response),
            "user_feedback": user_feedback
        }
        
        # Store pattern for learning
        self.training_patterns["conversation_styles"]["recent"].append(pattern_update)
        
        # Keep only recent patterns (last 100)
        if len(self.training_patterns["conversation_styles"]["recent"]) > 100:
            self.training_patterns["conversation_styles"]["recent"] = \
                self.training_patterns["conversation_styles"]["recent"][-100:]
    
    def _assess_response_effectiveness(self, user_input, roboto_response):
        """Assess effectiveness of a response"""
        effectiveness_score = 0.5  # baseline
        
        # Length appropriateness
        input_length = len(user_input.split())
        response_length = len(roboto_response.split())
        
        if input_length > 20 and response_length > 15:  # Detailed question gets detailed answer
            effectiveness_score += 0.2
        elif input_length < 10 and response_length < 20:  # Short question gets concise answer
            effectiveness_score += 0.1
        
        # Emotional appropriateness
        if "?" in user_input and any(word in roboto_response.lower() for word in ["think", "consider", "perspective"]):
            effectiveness_score += 0.2
        
        # Engagement indicators
        if "?" in roboto_response:  # Roboto asks follow-up questions
            effectiveness_score += 0.1
        
        return min(1.0, effectiveness_score)
    
    def save_training_data(self, filename="roboto_training_data.json"):
        """Save training patterns and insights"""
        try:
            training_data = {
                "training_patterns": dict(self.training_patterns),
                "last_updated": datetime.now().isoformat(),
                "insights": self.generate_learning_insights()
            }
            
            with open(filename, 'w') as f:
                json.dump(training_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving training data: {e}")
            return False
    
    def load_training_data(self, filename="roboto_training_data.json"):
        """Load existing training patterns"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.training_patterns.update(data.get("training_patterns", {}))
                    return True
            return False
        except Exception as e:
            print(f"Error loading training data: {e}")
            return False