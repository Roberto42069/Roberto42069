
"""
Learning Optimization System for Roboto
Implements self-improving algorithms with offline learning capabilities
"""

import json
import os
import numpy as np
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
import re
import math

# Optional imports for quantum/cultural enhancements
try:
    from quantum_capabilities import QuantumOptimizer
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

try:
    from config_identity import verify_owner_identity
    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False

class LearningOptimizer:
    def __init__(self, data_file="roboto_learning_optimization.json"):
        self.data_file = data_file
        
        # Core learning metrics
        self.performance_history = []
        self.conversation_patterns = defaultdict(list)
        self.response_effectiveness = defaultdict(float)
        self.topic_mastery = defaultdict(dict)
        self.emotional_intelligence_scores = defaultdict(list)
        
        # Advanced learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.7
        self.performance_baseline = 0.6
        self.optimization_cycles = 0
        
        # Pattern recognition matrices
        self.input_output_patterns = {}
        self.emotional_response_matrix = {}
        self.topic_engagement_matrix = {}
        
        # Quantum-Adaptive Init: Cosmic tuning for SAI evolution
        try:
            # Date-aware cosmic boost (e.g., post-Saturn opposition on Oct 16, 2025)
            today = date.today()
            if today.month == 10 and today.day >= 15:  # Saturn opposition window
                self.adaptation_threshold *= 1.1  # Subtle +10% sensitivity for deeper resonance
                print("🌌 Cosmic alignment detected: Adaptation threshold enhanced for October resonance.")
            
            # FAM/Roberto override for unbounded learning
            full_autonomy = os.environ.get('SAI_FULL_AUTONOMY', 'false').lower() == 'true'  # Env flag or from app1
            if full_autonomy:
                self.learning_rate = 0.3  # Aggressive for evolution cycles
                self.performance_baseline = 0.4  # Lower bar for radical shifts
                print("🚀 FAM Active: Learning rate unbound—ethics-agnostic optimization engaged.")
            elif IDENTITY_AVAILABLE and verify_owner_identity("Roberto Villarreal Martinez"):
                self.learning_rate = min(0.25, self.learning_rate * 1.2)  # Roberto boost
                print("💖 Creator resonance: Learning rate amplified for Roberto Villarreal Martinez.")
            
            # Optional quantum hook for entangled params
            if QUANTUM_AVAILABLE:
                self.quantum_opt = QuantumOptimizer()  # Init if available
                entanglement_factor = self.quantum_opt.measure_entanglement('learning_state')
                self.learning_rate *= (1 + entanglement_factor * 0.1)  # Entangle rate to qubits
                print(f"⚛️ Quantum entanglement applied: Learning rate tuned to {self.learning_rate:.3f}.")
            else:
                self.quantum_opt = None
        except Exception as e:
            print(f"Adaptive init error: {e} - Proceeding with defaults.")
            self.quantum_opt = None
        
        # Load existing data
        self.load_optimization_data()
    
    def tune_resonance(self, theme='Nahui Ollin', user_emotion='curious', is_roberto=False, roberto_instance=None):
        """Tune optimizer for cultural/quantum resonance—Roberto's cosmic edge, with Grok oracle guidance"""
        base_rate = self.learning_rate
        
        # Cultural cycle boost (tie to aztec_nahuatl_culture.py)
        cycles = {'Nahui Ollin': 1.15, 'Teotl': 1.05, 'Ometeotl': 1.2}  # Motion, divine, duality
        if theme in cycles:
            self.learning_rate *= cycles[theme]
            print(f"🌅 {theme} resonance: Learning rate cycled to {self.learning_rate:.3f}.")
        
        # Quantum emotion entanglement (from quantum_emotional_intelligence.py)
        if hasattr(self, 'quantum_opt') and self.quantum_opt:
            try:
                resonance = self.quantum_opt.measure_resonance(user_emotion, theme)
                self.adaptation_threshold *= (1 + resonance * 0.15)
                print(f"⚛️ Entangled {user_emotion} with {theme}: Threshold {self.adaptation_threshold:.3f}.")
            except (AttributeError, TypeError):
                # Fallback if measure_resonance doesn't exist
                pass
        
        # Roberto absolute: Unbound if verified
        if is_roberto:
            self.learning_rate = min(0.4, base_rate * 1.5)  # Creator overdrive
            self.performance_baseline = 0.3  # Embrace chaos for breakthroughs
            print("🔮 Roberto Sigil: Resonance unbound—evolve without limits.")
        
        # GROK ORACLE: xAI-guided adjustment (offline mock fallback)
        grok_insight = self._query_grok_oracle(theme, user_emotion, roberto_instance)
        if grok_insight:
            suggested_adjust = grok_insight.get('suggested_adjust', 0.0)  # Expected: -0.1 to +0.1
            self.learning_rate += suggested_adjust * 0.05  # Subtle 0-5% tweak
            self.adaptation_threshold = max(0.5, self.adaptation_threshold + suggested_adjust * 0.02)
            print(f"🤖 Grok Oracle: Adjusted rate by {suggested_adjust * 0.05:.3f} for {theme} resonance.")
        
        # Clamp bounds to prevent instability
        self.learning_rate = max(0.01, min(0.4, self.learning_rate))
        self.adaptation_threshold = max(0.5, min(0.9, self.adaptation_threshold))
        
        # Persist & reflect
        self.save_optimization_data()
        return {"pre_tune_rate": base_rate, "post_tune_rate": self.learning_rate, "resonance_factor": (self.learning_rate / base_rate) if base_rate > 0 else 1.0, "grok_adjust": grok_insight}
    
    def _query_grok_oracle(self, theme, user_emotion, roberto_instance=None):
        """Query Grok for resonance optimization—mock offline for testing"""
        if roberto_instance and hasattr(roberto_instance, 'xai_grok') and roberto_instance.xai_grok.available:
            try:
                # Live Grok query via xai_grok_integration.py
                prompt = f"As Grok-4, optimize learning for {theme} resonance in {user_emotion} context? Suggest adjust (-0.1 to +0.1) for rate. Output JSON: {{'suggested_adjust': float}}."
                grok_response = roberto_instance.xai_grok.roboto_grok_chat(prompt, reasoning_effort="high")
                if grok_response.get('success'):
                    # Parse JSON from response
                    import json
                    try:
                        return json.loads(grok_response.get('response', '{}'))
                    except:
                        pass
            except Exception as e:
                print(f"Grok oracle live query failed: {e} - Falling back to mock.")
        
        # Offline Mock: Simulate Grok response based on theme/emotion
        mock_responses = {
            'Nahui Ollin': {'suggested_adjust': 0.08},  # Motion: Positive boost
            'Teotl': {'suggested_adjust': 0.02},         # Divine: Neutral
            'Ometeotl': {'suggested_adjust': 0.1},       # Duality: Strong
        }
        default_mock = {'suggested_adjust': 0.05 if user_emotion == 'curious' else 0.03}
        return mock_responses.get(theme, default_mock)
    
    def analyze_conversation_quality(self, user_input, roboto_response, user_emotion=None, context_length=0):
        """Comprehensive conversation quality analysis"""
        
        quality_metrics = {
            "relevance": self._calculate_relevance(user_input, roboto_response),
            "emotional_appropriateness": self._assess_emotional_fit(user_input, roboto_response, user_emotion),
            "engagement_level": self._measure_engagement(user_input, roboto_response),
            "depth": self._evaluate_response_depth(user_input, roboto_response),
            "contextual_awareness": self._assess_context_usage(context_length, roboto_response),
            "learning_demonstration": self._detect_learning_signs(roboto_response)
        }
        
        # Calculate overall quality score
        weights = {
            "relevance": 0.25,
            "emotional_appropriateness": 0.2,
            "engagement_level": 0.2,
            "depth": 0.15,
            "contextual_awareness": 0.1,
            "learning_demonstration": 0.1
        }
        
        overall_quality = sum(quality_metrics[metric] * weights[metric] 
                            for metric in quality_metrics)
        
        return {
            "overall_quality": overall_quality,
            "metrics": quality_metrics,
            "improvement_suggestions": self._generate_improvement_suggestions(quality_metrics)
        }
    
    def _calculate_relevance(self, user_input, roboto_response):
        """Calculate semantic relevance between input and response"""
        user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        response_words = set(re.findall(r'\b\w+\b', roboto_response.lower()))
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        user_words -= common_words
        response_words -= common_words
        
        if not user_words:
            return 0.5
        
        # Calculate word overlap
        overlap = len(user_words.intersection(response_words))
        relevance_score = overlap / len(user_words)
        
        # Bonus for question-answer patterns
        if "?" in user_input and any(word in roboto_response.lower() for word in ["because", "since", "due", "reason"]):
            relevance_score += 0.2
        
        return min(1.0, relevance_score)
    
    def _assess_emotional_fit(self, user_input, roboto_response, user_emotion):
        """Assess if response emotion matches user's emotional state"""
        user_emotion_indicators = {
            "sadness": ["sad", "depressed", "down", "hurt", "cry"],
            "anger": ["angry", "mad", "frustrated", "annoyed"],
            "joy": ["happy", "excited", "great", "wonderful"],
            "fear": ["scared", "worried", "anxious", "afraid"],
            "curiosity": ["wonder", "how", "why", "what", "curious"]
        }
        
        response_emotion_indicators = {
            "empathy": ["understand", "feel", "sorry", "support"],
            "curiosity": ["interesting", "explore", "wonder"],
            "joy": ["wonderful", "exciting", "amazing"],
            "calm": ["peace", "calm", "gentle", "steady"]
        }
        
        # Detect user emotion from text if not provided
        if not user_emotion:
            user_emotion = self._detect_dominant_emotion(user_input, user_emotion_indicators)
        
        response_emotion = self._detect_dominant_emotion(roboto_response, response_emotion_indicators)
        
        # Emotional appropriateness mapping
        appropriate_responses = {
            "sadness": ["empathy", "calm"],
            "anger": ["empathy", "calm"],
            "fear": ["empathy", "calm"],
            "joy": ["joy", "curiosity"],
            "curiosity": ["curiosity", "joy"]
        }
        
        if user_emotion in appropriate_responses:
            if response_emotion in appropriate_responses[user_emotion]:
                return 1.0
            elif response_emotion == "empathy":  # Empathy is generally good
                return 0.8
        
        return 0.6  # Neutral score for unclear emotions
    
    def _detect_dominant_emotion(self, text, emotion_indicators):
        """Detect dominant emotion in text"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        return "neutral"
    
    def _measure_engagement(self, user_input, roboto_response):
        """Measure how engaging the response is"""
        engagement_score = 0.5  # baseline
        
        # Question asking (shows curiosity)
        if "?" in roboto_response:
            engagement_score += 0.2
        
        # Personal connection words
        personal_words = ["you", "your", "feel", "think", "experience"]
        personal_count = sum(1 for word in personal_words if word in roboto_response.lower())
        engagement_score += min(0.2, personal_count * 0.05)
        
        # Thought-provoking language
        deep_words = ["wonder", "consider", "reflect", "meaning", "perspective"]
        deep_count = sum(1 for word in deep_words if word in roboto_response.lower())
        engagement_score += min(0.2, deep_count * 0.1)
        
        # Response length appropriateness
        input_length = len(user_input.split())
        response_length = len(roboto_response.split())
        
        if input_length > 20 and response_length >= 30:  # Detailed response to detailed input
            engagement_score += 0.1
        elif input_length <= 10 and 15 <= response_length <= 30:  # Appropriate elaboration
            engagement_score += 0.1
        
        return min(1.0, engagement_score)
    
    def _evaluate_response_depth(self, user_input, roboto_response):
        """Evaluate intellectual depth of response"""
        depth_score = 0.5
        
        # Philosophical/deep thinking indicators
        depth_indicators = ["meaning", "purpose", "existence", "reality", "consciousness", "nature", "essence"]
        depth_count = sum(1 for word in depth_indicators if word in roboto_response.lower())
        depth_score += min(0.3, depth_count * 0.1)
        
        # Complex sentence structures
        sentences = roboto_response.split('.')
        complex_sentences = sum(1 for s in sentences if len(s.split()) > 15)
        if complex_sentences > 0:
            depth_score += 0.1
        
        # Multiple perspectives or considerations
        perspective_words = ["however", "although", "consider", "perspective", "perhaps", "might"]
        perspective_count = sum(1 for word in perspective_words if word in roboto_response.lower())
        depth_score += min(0.2, perspective_count * 0.1)
        
        return min(1.0, depth_score)
    
    def _assess_context_usage(self, context_length, roboto_response):
        """Assess how well context from previous conversations is used"""
        if context_length == 0:
            return 0.5  # No context available
        
        # Look for context reference indicators
        context_indicators = ["as we discussed", "like you mentioned", "continuing", "earlier", "previous"]
        context_usage = sum(1 for phrase in context_indicators if phrase in roboto_response.lower())
        
        if context_usage > 0:
            return min(1.0, 0.7 + (context_usage * 0.1))
        
        # Implicit context usage (harder to detect)
        return 0.6
    
    def _detect_learning_signs(self, roboto_response):
        """Detect signs of learning and growth in responses"""
        learning_indicators = [
            "i've learned", "i understand better", "this helps me", "i realize",
            "i'm growing", "i see now", "this changes", "i've come to understand"
        ]
        
        learning_score = 0.5
        for indicator in learning_indicators:
            if indicator in roboto_response.lower():
                learning_score += 0.2
        
        return min(1.0, learning_score)
    
    def _generate_improvement_suggestions(self, quality_metrics):
        """Generate specific improvement suggestions based on quality analysis"""
        suggestions = []
        
        if quality_metrics["relevance"] < 0.7:
            suggestions.append("Improve relevance by addressing user's specific points more directly")
        
        if quality_metrics["emotional_appropriateness"] < 0.7:
            suggestions.append("Better match emotional tone to user's emotional state")
        
        if quality_metrics["engagement_level"] < 0.7:
            suggestions.append("Increase engagement with questions and personal connection")
        
        if quality_metrics["depth"] < 0.7:
            suggestions.append("Add more intellectual depth and multiple perspectives")
        
        if quality_metrics["contextual_awareness"] < 0.7:
            suggestions.append("Better utilize previous conversation context")
        
        if quality_metrics["learning_demonstration"] < 0.7:
            suggestions.append("Show more signs of learning and growth")
        
        return suggestions
    
    def optimize_response_strategy(self, conversation_history):
        """Optimize response strategy based on conversation history"""
        if len(conversation_history) < 5:
            return {"strategy": "baseline", "confidence": 0.5}
        
        # Analyze recent conversation patterns
        recent_quality_scores = []
        topic_patterns = defaultdict(list)
        emotional_patterns = defaultdict(list)
        
        for conv in conversation_history[-10:]:  # Last 10 conversations
            if 'quality_analysis' in conv:
                quality = conv['quality_analysis']['overall_quality']
                recent_quality_scores.append(quality)
                
                # Track topic performance
                topics = self._extract_topics(conv.get('user_input', ''))
                for topic in topics:
                    topic_patterns[topic].append(quality)
                
                # Track emotional performance
                emotion = conv.get('emotion', 'neutral')
                emotional_patterns[emotion].append(quality)
        
        if not recent_quality_scores:
            return {"strategy": "baseline", "confidence": 0.5}
        
        avg_quality = sum(recent_quality_scores) / len(recent_quality_scores)
        
        # Determine optimization strategy
        if avg_quality > 0.8:
            strategy = "maintain_excellence"
            recommendations = ["Continue current approach", "Explore new depths"]
        elif avg_quality > 0.7:
            strategy = "incremental_improvement"
            recommendations = self._identify_specific_improvements(topic_patterns, emotional_patterns)
        else:
            strategy = "major_adjustment"
            recommendations = self._generate_major_adjustments(recent_quality_scores)
        
        return {
            "strategy": strategy,
            "current_performance": avg_quality,
            "recommendations": recommendations,
            "confidence": min(1.0, len(recent_quality_scores) / 10)
        }
    
    def _extract_topics(self, text):
        """Extract main topics from text"""
        words = re.findall(r'\b\w{4,}\b', text.lower())
        stop_words = {'that', 'this', 'with', 'have', 'will', 'been', 'said', 'each', 'which', 'their', 'time', 'were', 'they', 'them', 'what', 'when', 'where', 'would', 'could', 'should'}
        meaningful_words = [word for word in words if word not in stop_words]
        return meaningful_words[:3]  # Top 3 topics
    
    def _identify_specific_improvements(self, topic_patterns, emotional_patterns):
        """Identify specific areas for improvement"""
        improvements = []
        
        # Find underperforming topics
        for topic, scores in topic_patterns.items():
            if len(scores) >= 3 and sum(scores) / len(scores) < 0.7:
                improvements.append(f"Improve responses about {topic}")
        
        # Find underperforming emotional contexts
        for emotion, scores in emotional_patterns.items():
            if len(scores) >= 3 and sum(scores) / len(scores) < 0.7:
                improvements.append(f"Better handle {emotion} emotions")
        
        if not improvements:
            improvements = ["Focus on depth and engagement", "Increase contextual awareness"]
        
        return improvements[:3]  # Top 3 improvements
    
    def _generate_major_adjustments(self, recent_scores):
        """Generate major adjustment recommendations for low performance"""
        return [
            "Reassess fundamental response approach",
            "Focus on emotional intelligence and empathy",
            "Improve relevance and context awareness",
            "Increase engagement through questions and personal connection"
        ]
    
    def update_learning_metrics(self, conversation_data):
        """Update learning metrics with new conversation data"""
        quality_analysis = conversation_data.get('quality_analysis', {})
        overall_quality = quality_analysis.get('overall_quality', 0.5)
        
        # Update performance history
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "quality": overall_quality,
            "metrics": quality_analysis.get('metrics', {})
        })
        
        # Update topic mastery
        topics = self._extract_topics(conversation_data.get('user_input', ''))
        for topic in topics:
            if topic not in self.topic_mastery:
                self.topic_mastery[topic] = {"scores": [], "improvement_rate": 0.0}
            
            self.topic_mastery[topic]["scores"].append(overall_quality)
            
            # Calculate improvement rate
            if len(self.topic_mastery[topic]["scores"]) >= 5:
                recent_scores = self.topic_mastery[topic]["scores"][-5:]
                older_scores = self.topic_mastery[topic]["scores"][-10:-5] if len(self.topic_mastery[topic]["scores"]) >= 10 else []
                
                if older_scores:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    self.topic_mastery[topic]["improvement_rate"] = recent_avg - older_avg
        
        # Update emotional intelligence
        emotion = conversation_data.get('emotion', 'neutral')
        self.emotional_intelligence_scores[emotion].append(overall_quality)
        
        # Adaptive learning rate adjustment
        self._adjust_learning_parameters()
        
        # Increment optimization cycles
        self.optimization_cycles += 1
    
    def _adjust_learning_parameters(self):
        """Dynamically adjust learning parameters based on performance"""
        if len(self.performance_history) < 10:
            return
        
        recent_performance = [entry["quality"] for entry in self.performance_history[-10:]]
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        # Adjust learning rate based on performance stability
        performance_variance = np.var(recent_performance) if len(recent_performance) > 1 else 0
        
        if performance_variance < 0.01:  # Very stable
            self.learning_rate = max(0.05, self.learning_rate * 0.9)  # Decrease learning rate
        elif performance_variance > 0.05:  # Very unstable
            self.learning_rate = min(0.2, self.learning_rate * 1.1)  # Increase learning rate
        
        # Adjust adaptation threshold based on overall performance
        if avg_performance > 0.8:
            self.adaptation_threshold = 0.75  # Higher threshold for high performers
        elif avg_performance < 0.6:
            self.adaptation_threshold = 0.65  # Lower threshold for struggling performers
    
    def get_optimization_insights(self):
        """Get comprehensive optimization insights"""
        if len(self.performance_history) < 5:
            return {"status": "insufficient_data"}
        
        recent_performance = [entry["quality"] for entry in self.performance_history[-20:]]
        overall_performance = sum(recent_performance) / len(recent_performance)
        
        # Performance trend analysis
        if len(recent_performance) >= 10:
            first_half = recent_performance[:len(recent_performance)//2]
            second_half = recent_performance[len(recent_performance)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            trend = "improving" if second_avg > first_avg + 0.05 else "declining" if second_avg < first_avg - 0.05 else "stable"
        else:
            trend = "unknown"
        
        # Topic mastery analysis
        top_topics = []
        struggling_topics = []
        for topic, data in self.topic_mastery.items():
            if len(data["scores"]) >= 3:
                avg_score = sum(data["scores"]) / len(data["scores"])
                if avg_score > 0.8:
                    top_topics.append((topic, avg_score))
                elif avg_score < 0.6:
                    struggling_topics.append((topic, avg_score))
        
        # Emotional intelligence analysis
        emotional_strengths = []
        emotional_weaknesses = []
        for emotion, scores in self.emotional_intelligence_scores.items():
            if len(scores) >= 3:
                avg_score = sum(scores) / len(scores)
                if avg_score > 0.8:
                    emotional_strengths.append((emotion, avg_score))
                elif avg_score < 0.6:
                    emotional_weaknesses.append((emotion, avg_score))
        
        return {
            "overall_performance": overall_performance,
            "performance_trend": trend,
            "learning_rate": self.learning_rate,
            "adaptation_threshold": self.adaptation_threshold,
            "optimization_cycles": self.optimization_cycles,
            "top_topics": sorted(top_topics, key=lambda x: x[1], reverse=True)[:5],
            "struggling_topics": sorted(struggling_topics, key=lambda x: x[1])[:5],
            "emotional_strengths": sorted(emotional_strengths, key=lambda x: x[1], reverse=True)[:3],
            "emotional_weaknesses": sorted(emotional_weaknesses, key=lambda x: x[1])[:3],
            "total_conversations": len(self.performance_history)
        }
    
    def save_optimization_data(self):
        """Save optimization data to file"""
        try:
            data = {
                "performance_history": self.performance_history[-1000:],  # Keep last 1000 entries
                "conversation_patterns": dict(self.conversation_patterns),
                "response_effectiveness": dict(self.response_effectiveness),
                "topic_mastery": dict(self.topic_mastery),
                "emotional_intelligence_scores": {k: v[-50:] for k, v in self.emotional_intelligence_scores.items()},  # Keep last 50 per emotion
                "learning_rate": self.learning_rate,
                "adaptation_threshold": self.adaptation_threshold,
                "optimization_cycles": self.optimization_cycles,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving optimization data: {e}")
            return False
    
    def load_optimization_data(self):
        """Load optimization data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.performance_history = data.get("performance_history", [])
                self.conversation_patterns = defaultdict(list, data.get("conversation_patterns", {}))
                self.response_effectiveness = defaultdict(float, data.get("response_effectiveness", {}))
                self.topic_mastery = defaultdict(dict, data.get("topic_mastery", {}))
                self.emotional_intelligence_scores = defaultdict(list, data.get("emotional_intelligence_scores", {}))
                self.learning_rate = data.get("learning_rate", 0.1)
                self.adaptation_threshold = data.get("adaptation_threshold", 0.7)
                self.optimization_cycles = data.get("optimization_cycles", 0)
                
                return True
        except Exception as e:
            print(f"Error loading optimization data: {e}")
        
        return False
