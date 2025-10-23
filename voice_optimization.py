"""
Voice Recognition Optimization for Roberto Villarreal Martinez
Implements personalized speech recognition algorithms
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import re

class VoiceOptimizer:
    def __init__(self, user_name="Roberto Villarreal Martinez"):
        self.user_name = user_name
        self.voice_profile_file = f"voice_profile_{user_name.replace(' ', '_').lower()}.json"
        
        # Voice pattern analysis
        self.phonetic_patterns = defaultdict(list)
        self.pronunciation_preferences = {}
        self.speech_rhythm_data = []
        self.confidence_thresholds = {
            "high_confidence": 0.95,
            "medium_confidence": 0.85,
            "low_confidence": 0.75
        }
        
        # Common Spanish-English linguistic patterns for Roberto's background
        self.linguistic_adaptations = {
            "spanish_influence": {
                "b_v_confusion": ["be", "ve", "been", "veen"],
                "double_r": ["rr", "rolling_r"],
                "soft_consonants": ["ll", "ñ", "ch"],
                "vowel_emphasis": ["a", "e", "i", "o", "u"]
            },
            "common_words": {
                "roberto": ["roberto", "robotto", "robert"],
                "villarreal": ["villarreal", "villa real", "viyarreal"],
                "martinez": ["martinez", "martínez", "martines"]
            }
        }
        
        # Voice recognition improvements
        self.recognition_history = []
        self.accuracy_metrics = {
            "total_attempts": 0,
            "successful_recognitions": 0,
            "confidence_scores": [],
            "common_misrecognitions": defaultdict(int)
        }
        
        self.load_voice_profile()
    
    def analyze_voice_pattern(self, recognized_text, confidence_score, actual_text=None):
        """Analyze voice patterns for personalized optimization"""
        
        # Record recognition attempt
        attempt_data = {
            "timestamp": datetime.now().isoformat(),
            "recognized_text": recognized_text,
            "confidence": confidence_score,
            "actual_text": actual_text
        }
        
        self.recognition_history.append(attempt_data)
        self.accuracy_metrics["total_attempts"] += 1
        self.accuracy_metrics["confidence_scores"].append(confidence_score)
        
        # Analyze confidence patterns
        if confidence_score >= self.confidence_thresholds["high_confidence"]:
            self.accuracy_metrics["successful_recognitions"] += 1
        
        # Detect speech patterns
        self._analyze_phonetic_patterns(recognized_text)
        self._analyze_pronunciation_preferences(recognized_text, confidence_score)
        
        # Track misrecognitions for improvement
        if actual_text and recognized_text.lower() != actual_text.lower():
            self._track_misrecognition(recognized_text, actual_text)
        
        return self._generate_optimization_suggestions(recognized_text, confidence_score)
    
    def _analyze_phonetic_patterns(self, text):
        """Analyze phonetic patterns specific to Roberto's voice"""
        
        words = text.lower().split()
        
        for word in words:
            # Analyze Spanish linguistic influences
            if any(pattern in word for pattern in ["ll", "rr", "ñ", "ch"]):
                self.phonetic_patterns["spanish_sounds"].append(word)
            
            # Detect vowel emphasis patterns
            vowel_count = sum(1 for char in word if char in "aeiou")
            if vowel_count > len(word) * 0.4:  # High vowel density
                self.phonetic_patterns["vowel_emphasis"].append(word)
            
            # Track common name pronunciations
            if word in ["roberto", "villarreal", "martinez"]:
                self.phonetic_patterns["name_pronunciations"].append(word)
    
    def _analyze_pronunciation_preferences(self, text, confidence):
        """Learn Roberto's specific pronunciation preferences"""
        
        words = text.lower().split()
        
        for word in words:
            if word not in self.pronunciation_preferences:
                self.pronunciation_preferences[word] = {
                    "occurrences": 0,
                    "avg_confidence": 0,
                    "variants": []
                }
            
            pref = self.pronunciation_preferences[word]
            pref["occurrences"] += 1
            pref["avg_confidence"] = (
                (pref["avg_confidence"] * (pref["occurrences"] - 1) + confidence) 
                / pref["occurrences"]
            )
            
            # Track pronunciation variants
            if confidence > 0.9:
                pref["variants"].append(word)
    
    def _track_misrecognition(self, recognized, actual):
        """Track common misrecognitions for pattern learning"""
        
        misrecognition_key = f"{actual} -> {recognized}"
        self.accuracy_metrics["common_misrecognitions"][misrecognition_key] += 1
        
        # Analyze phonetic similarity for learning
        self._analyze_phonetic_similarity(recognized, actual)
    
    def _analyze_phonetic_similarity(self, recognized, actual):
        """Analyze why certain words are misrecognized"""
        
        # Simple phonetic analysis
        recognized_sounds = self._extract_phonetic_features(recognized)
        actual_sounds = self._extract_phonetic_features(actual)
        
        # Find common phonetic confusions
        if len(recognized_sounds) == len(actual_sounds):
            for i, (rec_sound, act_sound) in enumerate(zip(recognized_sounds, actual_sounds)):
                if rec_sound != act_sound:
                    confusion_key = f"{act_sound}_confused_with_{rec_sound}"
                    self.phonetic_patterns["confusions"].append(confusion_key)
    
    def _extract_phonetic_features(self, word):
        """Extract basic phonetic features from word"""
        
        # Simplified phonetic feature extraction
        features = []
        
        # Consonant clusters
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', word.lower())
        features.extend(consonant_clusters)
        
        # Vowel patterns
        vowel_patterns = re.findall(r'[aeiou]+', word.lower())
        features.extend(vowel_patterns)
        
        # Starting/ending sounds
        if len(word) > 0:
            features.append(f"start_{word[0].lower()}")
            features.append(f"end_{word[-1].lower()}")
        
        return features
    
    def _generate_optimization_suggestions(self, text, confidence):
        """Generate personalized optimization suggestions"""
        
        suggestions = []
        
        # Confidence-based suggestions
        if confidence < self.confidence_thresholds["low_confidence"]:
            suggestions.append("Consider speaking more clearly or reducing background noise")
        elif confidence < self.confidence_thresholds["medium_confidence"]:
            suggestions.append("Good recognition - slight pronunciation adjustment could help")
        else:
            suggestions.append("Excellent voice recognition quality")
        
        # Pattern-based suggestions
        words = text.lower().split()
        
        for word in words:
            if word in self.pronunciation_preferences:
                pref = self.pronunciation_preferences[word]
                if pref["avg_confidence"] < 0.8:
                    suggestions.append(f"Practice pronunciation of '{word}' for better recognition")
        
        # Spanish linguistic support
        if any(self._has_spanish_influence(word) for word in words):
            suggestions.append("Spanish accent adaptation active - pronunciation patterns learned")
        
        return suggestions
    
    def _has_spanish_influence(self, word):
        """Detect Spanish linguistic influence in pronunciation"""
        
        spanish_patterns = ["ll", "rr", "ñ", "ch"]
        return any(pattern in word for pattern in spanish_patterns)
    
    def get_voice_optimization_config(self):
        """Generate optimized voice recognition configuration"""
        
        config = {
            "user_profile": {
                "name": self.user_name,
                "linguistic_background": "Spanish-English bilingual",
                "voice_characteristics": self._analyze_voice_characteristics()
            },
            "recognition_settings": {
                "confidence_thresholds": self.confidence_thresholds,
                "language_model": "en-US",
                "accent_adaptation": "hispanic_english",
                "phonetic_adaptations": self._get_phonetic_adaptations()
            },
            "optimization_data": {
                "total_samples": len(self.recognition_history),
                "average_confidence": self._calculate_average_confidence(),
                "success_rate": self._calculate_success_rate(),
                "common_patterns": self._get_common_patterns()
            }
        }
        
        return config
    
    def _analyze_voice_characteristics(self):
        """Analyze Roberto's specific voice characteristics"""
        
        characteristics = {
            "speech_rate": "moderate",
            "accent_type": "hispanic_english",
            "common_phonetic_patterns": [],
            "pronunciation_stability": "high"
        }
        
        # Analyze phonetic patterns
        if "spanish_sounds" in self.phonetic_patterns:
            characteristics["common_phonetic_patterns"].extend(
                Counter(self.phonetic_patterns["spanish_sounds"]).most_common(5)
            )
        
        return characteristics
    
    def _get_phonetic_adaptations(self):
        """Get phonetic adaptations for Roberto's voice"""
        
        adaptations = {
            "b_v_distinction": "enhanced",
            "rolling_r_detection": "enabled",
            "vowel_emphasis_adjustment": "moderate",
            "consonant_cluster_recognition": "enhanced"
        }
        
        # Add specific adaptations based on learned patterns
        if "confusions" in self.phonetic_patterns:
            common_confusions = Counter(self.phonetic_patterns["confusions"]).most_common(3)
            adaptations["common_confusions"] = [conf[0] for conf in common_confusions]
        
        return adaptations
    
    def _calculate_average_confidence(self):
        """Calculate average confidence score"""
        
        if not self.accuracy_metrics["confidence_scores"]:
            return 0.0
        
        return sum(self.accuracy_metrics["confidence_scores"]) / len(self.accuracy_metrics["confidence_scores"])
    
    def _calculate_success_rate(self):
        """Calculate recognition success rate"""
        
        if self.accuracy_metrics["total_attempts"] == 0:
            return 0.0
        
        return self.accuracy_metrics["successful_recognitions"] / self.accuracy_metrics["total_attempts"]
    
    def _get_common_patterns(self):
        """Get most common voice patterns"""
        
        patterns = {}
        
        for pattern_type, pattern_list in self.phonetic_patterns.items():
            if pattern_list:
                patterns[pattern_type] = Counter(pattern_list).most_common(3)
        
        return patterns
    
    def generate_personalized_grammar(self):
        """Generate personalized grammar for better recognition"""
        
        grammar_rules = []
        
        # Name recognition rules
        grammar_rules.extend([
            "ROBERTO = roberto | robotto | robert",
            "VILLARREAL = villarreal | villa real | viyarreal",
            "MARTINEZ = martinez | martínez | martines",
            "FULL_NAME = ROBERTO VILLARREAL MARTINEZ"
        ])
        
        # Common Spanish-influenced pronunciations
        grammar_rules.extend([
            "BE_VE = be | ve | been | veen",
            "DOUBLE_R = rr | rolling_r",
            "SOFT_CONSONANTS = ll | ñ | ch"
        ])
        
        # Learned pronunciation patterns
        for word, pref in self.pronunciation_preferences.items():
            if pref["avg_confidence"] > 0.9 and len(pref["variants"]) > 1:
                variants = " | ".join(set(pref["variants"]))
                grammar_rules.append(f"{word.upper()} = {variants}")
        
        return grammar_rules
    
    def get_optimization_insights(self):
        """Get comprehensive optimization insights"""
        
        insights = {
            "voice_profile_strength": self._calculate_profile_strength(),
            "recognition_accuracy": self._calculate_success_rate(),
            "confidence_trend": self._analyze_confidence_trend(),
            "improvement_areas": self._identify_improvement_areas(),
            "optimization_recommendations": self._generate_optimization_recommendations()
        }
        
        return insights
    
    def _calculate_profile_strength(self):
        """Calculate how well-trained the voice profile is"""
        
        factors = {
            "sample_size": min(len(self.recognition_history) / 100, 1.0),
            "pattern_diversity": len(self.phonetic_patterns) / 10,
            "pronunciation_stability": len(self.pronunciation_preferences) / 50
        }
        
        return sum(factors.values()) / len(factors)
    
    def _analyze_confidence_trend(self):
        """Analyze confidence score trends over time"""
        
        if len(self.accuracy_metrics["confidence_scores"]) < 10:
            return "insufficient_data"
        
        recent_scores = self.accuracy_metrics["confidence_scores"][-10:]
        older_scores = self.accuracy_metrics["confidence_scores"][-20:-10] if len(self.accuracy_metrics["confidence_scores"]) >= 20 else []
        
        if older_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            if recent_avg > older_avg + 0.05:
                return "improving"
            elif recent_avg < older_avg - 0.05:
                return "declining"
        
        return "stable"
    
    def _identify_improvement_areas(self):
        """Identify specific areas for voice recognition improvement"""
        
        areas = []
        
        # Low confidence words
        low_confidence_words = [
            word for word, pref in self.pronunciation_preferences.items()
            if pref["avg_confidence"] < 0.8
        ]
        
        if low_confidence_words:
            areas.append(f"Practice pronunciation: {', '.join(low_confidence_words[:3])}")
        
        # Common misrecognitions
        from collections import Counter
        misrecognitions = self.accuracy_metrics.get("common_misrecognitions", {})
        if isinstance(misrecognitions, dict):
            counter = Counter(misrecognitions)
            common_errors = counter.most_common(3)
            if common_errors:
                areas.append("Address common misrecognitions in speech patterns")
        
        # Overall confidence
        avg_confidence = self._calculate_average_confidence()
        if avg_confidence < 0.85:
            areas.append("Improve overall speech clarity and microphone positioning")
        
        return areas
    
    def _generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        
        recommendations = []
        
        # Microphone and environment
        recommendations.append("Use a high-quality microphone positioned 6-8 inches from mouth")
        recommendations.append("Minimize background noise during voice recognition")
        
        # Speech patterns
        recommendations.append("Speak at moderate pace with clear articulation")
        recommendations.append("Emphasize consonant sounds for better recognition")
        
        # Language-specific
        recommendations.append("Spanish accent adaptation is active - natural pronunciation works well")
        
        # Personalized recommendations
        success_rate = self._calculate_success_rate()
        if success_rate > 0.9:
            recommendations.append("Excellent voice profile - continue current speech patterns")
        elif success_rate > 0.8:
            recommendations.append("Good recognition - minor adjustments could improve accuracy")
        else:
            recommendations.append("Consider voice training for improved recognition accuracy")
        
        return recommendations
    
    def save_voice_profile(self):
        """Save voice profile to file"""
        
        try:
            profile_data = {
                "user_name": self.user_name,
                "phonetic_patterns": dict(self.phonetic_patterns),
                "pronunciation_preferences": self.pronunciation_preferences,
                "accuracy_metrics": dict(self.accuracy_metrics),
                "recognition_history": self.recognition_history[-500:],  # Keep last 500
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.voice_profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving voice profile: {e}")
            return False
    
    def load_voice_profile(self):
        """Load voice profile from file"""
        
        try:
            if os.path.exists(self.voice_profile_file):
                with open(self.voice_profile_file, 'r') as f:
                    data = json.load(f)
                
                self.phonetic_patterns = defaultdict(list, data.get("phonetic_patterns", {}))
                self.pronunciation_preferences = data.get("pronunciation_preferences", {})
                self.accuracy_metrics = defaultdict(int, data.get("accuracy_metrics", {}))
                self.recognition_history = data.get("recognition_history", [])
                
                return True
        except Exception as e:
            print(f"Error loading voice profile: {e}")
        
        return False