"""
Advanced Learning Engine for Roboto
Implements sophisticated machine learning algorithms for continuous improvement
"""

from datetime import datetime
from collections import defaultdict, deque
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class AdvancedLearningEngine:
    def __init__(self, learning_file="roboto_learning_data.pkl", quantum_emotional_intelligence=None):
        self.learning_file = learning_file
        
        # 🌌💖 UNIFIED EMOTIONAL STATE INTEGRATION
        self.quantum_emotional_intelligence = quantum_emotional_intelligence
        
        # Learning components
        self.conversation_patterns = defaultdict(list)
        self.response_quality_scores = deque(maxlen=1000)
        self.user_feedback_history = []
        self.topic_expertise = defaultdict(float)
        self.emotional_response_patterns = defaultdict(dict)
        self.learning_metrics = {
            "total_interactions": 0,
            "successful_responses": 0,
            "learning_rate": 0.1,
            "adaptation_speed": 0.05,
            "current_performance": 0.7
        }
        
        # Advanced learning models
        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 3))
        self.response_classifier = None
        self.topic_clusters = None
        self.conversation_embeddings = []
        
        # Neural network simulation for pattern recognition
        self.pattern_weights = defaultdict(float)
        self.learning_history = []
        
        # Load existing learning data
        self.load_learning_data()
    
    def analyze_conversation_effectiveness(self, user_input, roboto_response, context=None):
        """Analyze effectiveness of a conversation turn"""
        effectiveness_score = 0.5  # baseline
        
        # Length appropriateness
        input_words = len(user_input.split())
        response_words = len(roboto_response.split())
        
        if input_words > 20:  # Detailed question
            if response_words >= 30:  # Comprehensive answer
                effectiveness_score += 0.2
            elif response_words < 10:  # Too brief
                effectiveness_score -= 0.1
        elif input_words < 5:  # Short input
            if 10 <= response_words <= 25:  # Appropriate length
                effectiveness_score += 0.15
        
        # Emotional appropriateness
        user_emotion = self._detect_emotion_advanced(user_input)
        response_emotion = self._detect_emotion_advanced(roboto_response)
        
        if self._emotions_are_appropriate(user_emotion, response_emotion):
            effectiveness_score += 0.2
        
        # Question-answer coherence
        if "?" in user_input:
            if any(word in roboto_response.lower() for word in ["because", "since", "due to", "reason"]):
                effectiveness_score += 0.15
            if "?" in roboto_response:  # Follow-up question
                effectiveness_score += 0.1
        
        # Topic continuity
        if context and len(context) > 0:
            topic_continuity = self._calculate_topic_continuity(user_input, roboto_response, context)
            effectiveness_score += topic_continuity * 0.2
        
        # Engagement indicators
        engagement_words = ["interesting", "tell me more", "what do you think", "how", "why"]
        if any(word in roboto_response.lower() for word in engagement_words):
            effectiveness_score += 0.1
        
        return min(1.0, max(0.0, effectiveness_score))
    
    def _detect_emotion_advanced(self, text):
        """
        Advanced emotion detection with nuanced understanding
        🌌💖 Uses unified quantum emotional state when available
        """
        # Priority: Use quantum emotional intelligence if available
        if self.quantum_emotional_intelligence:
            try:
                quantum_state = self.get_unified_emotional_state(self.quantum_emotional_intelligence)
                # Return quantum state if it's recent and valid
                if quantum_state.get("emotion") != "neutral" or quantum_state.get("intensity", 0) > 0.5:
                    return {
                        "emotion": quantum_state["emotion"],
                        "intensity": quantum_state["intensity"],
                        "source": "quantum_emotional_intelligence"
                    }
            except Exception:
                # Fall through to local detection
                pass
        
        # Fallback: Local emotion detection
        text_lower = text.lower()
        
        emotion_patterns = {
            "joy": ["happy", "excited", "wonderful", "amazing", "fantastic", "great", "love", "delighted"],
            "sadness": ["sad", "depressed", "down", "disappointed", "hurt", "upset", "crying"],
            "anger": ["angry", "furious", "mad", "annoyed", "frustrated", "irritated"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "terrified"],
            "curiosity": ["wonder", "curious", "interesting", "how", "why", "what if"],
            "empathy": ["understand", "feel for", "sorry", "support", "care", "compassion"],
            "contemplation": ["think", "reflect", "consider", "ponder", "meaning", "philosophy"]
        }
        
        emotion_scores = defaultdict(float)
        
        for emotion, keywords in emotion_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
        
        # Consider intensity modifiers
        intensity_modifiers = ["very", "extremely", "really", "quite", "somewhat"]
        intensity_multiplier = 1.0
        for modifier in intensity_modifiers:
            if modifier in text_lower:
                intensity_multiplier = 1.5
                break
        
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            return {"emotion": dominant_emotion, "intensity": emotion_scores[dominant_emotion] * intensity_multiplier, "source": "local_detection"}
        
        return {"emotion": "neutral", "intensity": 0.5, "source": "default"}
    
    def _emotions_are_appropriate(self, user_emotion, response_emotion):
        """Check if response emotion is appropriate for user emotion"""
        appropriate_responses = {
            "sadness": ["empathy", "contemplation", "neutral"],
            "anger": ["empathy", "contemplation", "neutral"],
            "fear": ["empathy", "contemplation", "neutral"],
            "joy": ["joy", "curiosity", "neutral"],
            "curiosity": ["curiosity", "contemplation", "joy"],
            "neutral": ["curiosity", "contemplation", "neutral"]
        }
        
        user_emo = user_emotion.get("emotion", "neutral")
        response_emo = response_emotion.get("emotion", "neutral")
        
        return response_emo in appropriate_responses.get(user_emo, ["neutral"])
    
    def _calculate_topic_continuity(self, user_input, roboto_response, context):
        """Calculate how well the response maintains topic continuity"""
        if not context:
            return 0.5
        
        # Get recent context
        recent_context = " ".join(context[-3:]) if len(context) >= 3 else " ".join(context)
        
        # Extract key topics from context and current exchange
        context_topics = self._extract_topics(recent_context)
        current_topics = self._extract_topics(user_input + " " + roboto_response)
        
        if not context_topics or not current_topics:
            return 0.5
        
        # Calculate topic overlap
        overlap = len(set(context_topics).intersection(set(current_topics)))
        total_topics = len(set(context_topics).union(set(current_topics)))
        
        return overlap / max(1, total_topics)
    
    def _extract_topics(self, text):
        """Extract key topics from text"""
        # Simple topic extraction using important words
        words = re.findall(r'\b\w{4,}\b', text.lower())
        stop_words = {'that', 'this', 'with', 'have', 'will', 'been', 'said', 'each', 'which', 'their', 'time', 'were'}
        topics = [word for word in words if word not in stop_words]
        return topics[:5]  # Top 5 topics
    
    def learn_from_interaction(self, user_input, roboto_response, user_feedback=None, context=None):
        """Learn from a single interaction"""
        # Calculate effectiveness
        effectiveness = self.analyze_conversation_effectiveness(user_input, roboto_response, context)
        
        # Store interaction data
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "roboto_response": roboto_response,
            "effectiveness": effectiveness,
            "user_feedback": user_feedback,
            "context_length": len(context) if context else 0
        }
        
        self.learning_history.append(interaction_data)
        self.response_quality_scores.append(effectiveness)
        
        # Update learning metrics
        self.learning_metrics["total_interactions"] += 1
        if effectiveness > 0.7:
            self.learning_metrics["successful_responses"] += 1
        
        # Update current performance (rolling average)
        recent_scores = list(self.response_quality_scores)[-20:]  # Last 20 interactions
        self.learning_metrics["current_performance"] = sum(recent_scores) / len(recent_scores)
        
        # Learn patterns
        self._update_conversation_patterns(user_input, roboto_response, effectiveness)
        self._update_topic_expertise(user_input, roboto_response, effectiveness)
        self._update_emotional_patterns(user_input, roboto_response, effectiveness)
        
        # Adaptive learning rate
        self._adjust_learning_rate()
        
        return effectiveness
    
    def _update_conversation_patterns(self, user_input, roboto_response, effectiveness):
        """Update conversation pattern understanding"""
        input_length = len(user_input.split())
        response_length = len(roboto_response.split())
        
        pattern_key = f"input_{min(input_length//5, 10)}_response_{min(response_length//10, 10)}"
        
        self.conversation_patterns[pattern_key].append({
            "effectiveness": effectiveness,
            "timestamp": datetime.now().isoformat(),
            "user_question": "?" in user_input,
            "roboto_question": "?" in roboto_response
        })
        
        # Keep only recent patterns
        if len(self.conversation_patterns[pattern_key]) > 50:
            self.conversation_patterns[pattern_key] = self.conversation_patterns[pattern_key][-50:]
    
    def _update_topic_expertise(self, user_input, roboto_response, effectiveness):
        """Update topic-specific expertise scores"""
        topics = self._extract_topics(user_input + " " + roboto_response)
        
        for topic in topics:
            current_expertise = self.topic_expertise[topic]
            learning_rate = self.learning_metrics["learning_rate"]
            
            # Update expertise with exponential moving average
            self.topic_expertise[topic] = (
                current_expertise * (1 - learning_rate) + 
                effectiveness * learning_rate
            )
    
    def _update_emotional_patterns(self, user_input, roboto_response, effectiveness):
        """Update emotional response patterns"""
        user_emotion = self._detect_emotion_advanced(user_input)
        response_emotion = self._detect_emotion_advanced(roboto_response)
        
        user_emo_key = user_emotion["emotion"]
        response_emo_key = response_emotion["emotion"]
        
        if user_emo_key not in self.emotional_response_patterns:
            self.emotional_response_patterns[user_emo_key] = defaultdict(list)
        
        self.emotional_response_patterns[user_emo_key][response_emo_key].append(effectiveness)
        
        # Keep only recent data
        if len(self.emotional_response_patterns[user_emo_key][response_emo_key]) > 30:
            self.emotional_response_patterns[user_emo_key][response_emo_key] = \
                self.emotional_response_patterns[user_emo_key][response_emo_key][-30:]
    
    def _adjust_learning_rate(self):
        """Dynamically adjust learning rate based on performance"""
        if len(self.response_quality_scores) < 10:
            return
        
        recent_performance = self.learning_metrics["current_performance"]
        
        if recent_performance > 0.8:  # High performance
            self.learning_metrics["learning_rate"] = max(0.01, self.learning_metrics["learning_rate"] * 0.95)
        elif recent_performance < 0.6:  # Low performance
            self.learning_metrics["learning_rate"] = min(0.3, self.learning_metrics["learning_rate"] * 1.1)
    
    def generate_response_recommendations(self, user_input, context=None):
        """Generate recommendations for response improvement"""
        recommendations = {
            "suggested_length": self._recommend_response_length(user_input),
            "emotional_tone": self._recommend_emotional_tone(user_input),
            "engagement_strategy": self._recommend_engagement_strategy(user_input, context),
            "topic_expertise": self._get_topic_expertise_level(user_input),
            "confidence": 0.7
        }
        
        return recommendations
    
    def _recommend_response_length(self, user_input):
        """Recommend optimal response length"""
        input_length = len(user_input.split())
        
        if input_length > 30:  # Long, detailed input
            return {"min_words": 40, "max_words": 80, "reasoning": "Detailed question needs comprehensive answer"}
        elif input_length > 15:  # Medium input
            return {"min_words": 20, "max_words": 50, "reasoning": "Moderate detail appropriate"}
        else:  # Short input
            return {"min_words": 10, "max_words": 30, "reasoning": "Concise response for brief input"}
    
    def get_unified_emotional_state(self, quantum_emotional_intelligence=None):
        """
        Get unified emotional state from quantum system if available
        Integrates with quantum emotional intelligence for consistent state
        """
        if quantum_emotional_intelligence:
            return {
                "emotion": quantum_emotional_intelligence.current_emotion,
                "intensity": quantum_emotional_intelligence.emotion_intensity,
                "system": "quantum_emotional_intelligence",
                "quantum_amplified": quantum_emotional_intelligence.quantum_emotional_state.get("quantum_amplified", False) if quantum_emotional_intelligence.quantum_emotional_state else False
            }
        return {"emotion": "neutral", "intensity": 0.5, "system": "learning_engine"}
    
    def _recommend_emotional_tone(self, user_input):
        """Recommend appropriate emotional tone"""
        user_emotion = self._detect_emotion_advanced(user_input)
        emotion = user_emotion["emotion"]
        
        tone_recommendations = {
            "sadness": {"tone": "empathetic", "keywords": ["understand", "support", "here for you"]},
            "anger": {"tone": "calm_supportive", "keywords": ["acknowledge", "perspective", "understandable"]},
            "fear": {"tone": "reassuring", "keywords": ["safe", "okay", "together"]},
            "joy": {"tone": "celebratory", "keywords": ["wonderful", "exciting", "share your joy"]},
            "curiosity": {"tone": "exploratory", "keywords": ["interesting", "explore", "discover"]},
            "neutral": {"tone": "engaging", "keywords": ["think", "consider", "perspective"]}
        }
        
        return tone_recommendations.get(emotion, tone_recommendations["neutral"])
    
    def _recommend_engagement_strategy(self, user_input, context):
        """Recommend engagement strategy"""
        if "?" in user_input:
            return {"strategy": "answer_and_expand", "technique": "Provide answer then ask follow-up"}
        elif len(context or []) > 5:
            return {"strategy": "build_continuity", "technique": "Reference previous discussion"}
        else:
            return {"strategy": "explore_depth", "technique": "Ask thought-provoking questions"}
    
    def _get_topic_expertise_level(self, user_input):
        """Get expertise level for topics in user input"""
        topics = self._extract_topics(user_input)
        if not topics:
            return {"level": "general", "confidence": 0.5}
        
        expertise_scores = [self.topic_expertise.get(topic, 0.5) for topic in topics]
        avg_expertise = sum(expertise_scores) / len(expertise_scores)
        
        if avg_expertise > 0.8:
            return {"level": "expert", "confidence": avg_expertise}
        elif avg_expertise > 0.6:
            return {"level": "knowledgeable", "confidence": avg_expertise}
        else:
            return {"level": "learning", "confidence": avg_expertise}
    
    def get_learning_insights(self):
        """Generate comprehensive learning insights"""
        if len(self.learning_history) < 10:
            return {"status": "insufficient_data", "recommendations": ["Continue conversations to gather learning data"]}
        
        insights = {
            "performance_metrics": self.learning_metrics.copy(),
            "top_conversation_patterns": self._analyze_top_patterns(),
            "emotional_effectiveness": self._analyze_emotional_effectiveness(),
            "topic_strengths": self._get_topic_strengths(),
            "improvement_areas": self._identify_improvement_areas(),
            "learning_trends": self._analyze_learning_trends()
        }
        
        return insights
    
    def _analyze_top_patterns(self):
        """Analyze most effective conversation patterns"""
        pattern_effectiveness = {}
        
        for pattern, data in self.conversation_patterns.items():
            if len(data) >= 5:  # Sufficient data
                avg_effectiveness = sum(d["effectiveness"] for d in data) / len(data)
                pattern_effectiveness[pattern] = avg_effectiveness
        
        # Return top 5 patterns
        top_patterns = sorted(pattern_effectiveness.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"pattern": p, "effectiveness": e} for p, e in top_patterns]
    
    def _analyze_emotional_effectiveness(self):
        """Analyze effectiveness of emotional responses"""
        emotional_analysis = {}
        
        for user_emotion, responses in self.emotional_response_patterns.items():
            response_effectiveness = {}
            for response_emotion, scores in responses.items():
                if len(scores) >= 3:
                    avg_score = sum(scores) / len(scores)
                    response_effectiveness[response_emotion] = avg_score
            
            if response_effectiveness:
                best_response = max(response_effectiveness, key=response_effectiveness.get)
                emotional_analysis[user_emotion] = {
                    "best_response": best_response,
                    "effectiveness": response_effectiveness[best_response]
                }
        
        return emotional_analysis
    
    def _get_topic_strengths(self):
        """Get topics where Roboto performs best"""
        topic_scores = [(topic, score) for topic, score in self.topic_expertise.items() if score > 0.6]
        return sorted(topic_scores, key=lambda x: x[1], reverse=True)[:10]
    
    def _identify_improvement_areas(self):
        """Identify areas needing improvement"""
        improvements = []
        
        current_performance = self.learning_metrics["current_performance"]
        if current_performance < 0.7:
            improvements.append("Overall response quality needs improvement")
        
        # Check emotional response patterns
        for user_emotion, responses in self.emotional_response_patterns.items():
            best_score = 0
            for response_emotion, scores in responses.items():
                if scores:
                    best_score = max(best_score, sum(scores) / len(scores))
            
            if best_score < 0.6:
                improvements.append(f"Improve responses to {user_emotion} emotions")
        
        return improvements
    
    def _analyze_learning_trends(self):
        """Analyze learning progress over time"""
        if len(self.learning_history) < 20:
            return {"trend": "insufficient_data"}
        
        recent_scores = [h["effectiveness"] for h in self.learning_history[-20:]]
        older_scores = [h["effectiveness"] for h in self.learning_history[-40:-20]] if len(self.learning_history) >= 40 else []
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        
        if older_scores:
            older_avg = sum(older_scores) / len(older_scores)
            if recent_avg > older_avg + 0.05:
                return {"trend": "improving", "improvement": recent_avg - older_avg}
            elif recent_avg < older_avg - 0.05:
                return {"trend": "declining", "decline": older_avg - recent_avg}
        
        return {"trend": "stable", "current_level": recent_avg}
    
    def save_learning_data(self):
        """Save learning data to file"""
        try:
            learning_data = {
                "conversation_patterns": dict(self.conversation_patterns),
                "response_quality_scores": list(self.response_quality_scores),
                "user_feedback_history": self.user_feedback_history,
                "topic_expertise": dict(self.topic_expertise),
                "emotional_response_patterns": {k: dict(v) for k, v in self.emotional_response_patterns.items()},
                "learning_metrics": self.learning_metrics,
                "pattern_weights": dict(self.pattern_weights),
                "learning_history": self.learning_history[-500:],  # Keep last 500 interactions
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.learning_file, 'wb') as f:
                pickle.dump(learning_data, f)
            
            return True
        except Exception as e:
            print(f"Error saving learning data: {e}")
            return False
    
    def load_learning_data(self):
        """Load learning data from file"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.conversation_patterns = defaultdict(list, data.get("conversation_patterns", {}))
                self.response_quality_scores = deque(data.get("response_quality_scores", []), maxlen=1000)
                self.user_feedback_history = data.get("user_feedback_history", [])
                self.topic_expertise = defaultdict(float, data.get("topic_expertise", {}))
                self.emotional_response_patterns = defaultdict(dict, {
                    k: defaultdict(list, v) for k, v in data.get("emotional_response_patterns", {}).items()
                })
                self.learning_metrics.update(data.get("learning_metrics", {}))
                self.pattern_weights = defaultdict(float, data.get("pattern_weights", {}))
                self.learning_history = data.get("learning_history", [])
                
                return True
        except Exception as e:
            print(f"Error loading learning data: {e}")
        
        return False