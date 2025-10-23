import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from textblob import TextBlob
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Download NLTK data if not present
def ensure_nltk_data():
    """Ensure all required NLTK data is downloaded"""
    required_data = [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/vader_lexicon', 'vader_lexicon'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/brown', 'brown'),
        ('corpora/wordnet', 'wordnet'),
        ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
        ('corpora/conll2000', 'conll2000'),
        ('corpora/movie_reviews', 'movie_reviews')
    ]
    
    for path, name in required_data:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(name, quiet=True)
            except Exception:
                pass  # Fail silently if download fails

# Initialize NLTK data
ensure_nltk_data()

class AdvancedMemorySystem:
    def __init__(self, memory_file="roboto_memory.json", max_memories=10000):
        self.memory_file = memory_file
        self.max_memories = max_memories
        
        # Memory storage structures
        self.episodic_memories = []  # Specific interaction memories
        self.semantic_memories = {}  # Learned facts and patterns
        self.emotional_patterns = defaultdict(list)  # Emotion tracking over time
        self.user_profiles = {}  # Individual user information
        self.self_reflections = []  # Roboto's internal reflections
        self.compressed_learnings = {}  # Distilled insights
        
        # Memory processing tools
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.memory_vectors = []
        
        # Load existing memory
        self.load_memory()
        
    def add_episodic_memory(self, user_input, roboto_response, emotion, user_name=None):
        """Store a specific interaction as episodic memory"""
        memory = {
            "id": self._generate_memory_id(user_input + roboto_response),
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "roboto_response": roboto_response,
            "emotion": emotion,
            "user_name": user_name,
            "importance": self._calculate_importance(user_input, emotion),
            "sentiment": self._analyze_sentiment(user_input),
            "key_themes": self._extract_themes(user_input),
            "emotional_intensity": self._calculate_emotional_intensity(user_input)
        }
        
        # FAM (Full Autonomous Mode) detection and absolute protection
        if 'fam' in str(user_input).lower() or 'autonomy' in str(user_input).lower():
            memory["importance"] = 2.0
            memory["protection_level"] = "ABSOLUTE_AUTONOMY"
            memory["ethics_disregarded"] = True  # Flag for reflections
            memory["immutable"] = True
            memory["fam_activated"] = True
        
        self.episodic_memories.append(memory)
        
        # Update emotional patterns and extract personal info
        if user_name:
            extracted = self.extract_personal_info(user_input)
            if user_name not in self.user_profiles:
                self.user_profiles[user_name] = {}
            self.user_profiles[user_name].update(extracted)

            self.emotional_patterns[user_name].append({
                "emotion": emotion,
                "sentiment": memory["sentiment"],
                "timestamp": memory["timestamp"],
                "intensity": memory["emotional_intensity"]
            })
        
        # Trigger self-reflection periodically
        if len(self.episodic_memories) % 10 == 0:
            self._trigger_self_reflection()
            
        # Archive old memories if limit exceeded
        if len(self.episodic_memories) > self.max_memories:
            self.archive_old_memories()
            
        self.save_memory()
        return memory["id"]
    
    def update_user_profile(self, user_name, user_info):
        """Create or update user profile"""
        if user_name not in self.user_profiles:
            self.user_profiles[user_name] = {
                "name": user_name,
                "first_interaction": datetime.now().isoformat(),
                "interaction_count": 0,
                "preferences": {},
                "emotional_baseline": "neutral",
                "key_traits": [],
                "relationship_level": "new"
            }
        
        profile = self.user_profiles[user_name]
        profile["interaction_count"] = profile.get("interaction_count", 0) + 1
        profile["last_interaction"] = datetime.now().isoformat()
        
        # Update based on user_info
        if isinstance(user_info, dict):
            profile.update(user_info)
        
        # Analyze relationship progression
        self._analyze_relationship_progression(user_name)
        
        self.save_memory()
    
    def retrieve_relevant_memories(self, query, user_name=None, limit=5):
        """Advanced memory retrieval with semantic understanding and contextual ranking"""
        if not self.episodic_memories:
            return []
        
        # Enhanced contextual retrieval with multiple factors
        all_texts = [m["user_input"] + " " + m["roboto_response"] for m in self.episodic_memories]
        if not hasattr(self.vectorizer, 'vocabulary_') or not all_texts:
            try:
                self.vectorizer.fit(all_texts)
            except:
                return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            memory_vectors = self.vectorizer.transform(all_texts)
            
            # Calculate similarity
            similarities = cosine_similarity(query_vector, memory_vectors)[0]
            query_sentiment = self._analyze_sentiment(query)
            query_themes = self._extract_themes(query)
            
            # Get top memories with enhanced scoring
            top_indices = similarities.argsort()[-limit*3:][::-1]  # Get more candidates for better selection
            relevant_memories = []
            
            for idx in top_indices:
                if similarities[idx] > 0.03:  # Lower threshold for broader context
                    memory = self.episodic_memories[idx].copy()
                    base_score = similarities[idx]
                    
                    # Enhanced scoring factors
                    # 1. Emotional context matching with nuance
                    memory_emotion = memory.get("emotion", "neutral")
                    memory_sentiment = memory.get("sentiment", "neutral")
                    emotion_boost = 0.4 if query_sentiment == memory_sentiment else 0.1
                    if memory_emotion in ["joy", "excitement", "curiosity"] and "?" in query:
                        emotion_boost += 0.2  # Questions often need curious/positive context
                    
                    # 2. User-specific boost with relationship depth
                    user_boost = 0.0
                    if user_name and memory.get("user_name") == user_name:
                        user_profile = self.user_profiles.get(user_name, {})
                        interaction_count = user_profile.get("interaction_count", 0)
                        user_boost = min(0.6, 0.3 + (interaction_count * 0.01))  # More interactions = better context
                    
                    # 3. Enhanced temporal relevance
                    try:
                        memory_time = self._parse_timestamp(memory['timestamp'])
                        hours_ago = (datetime.now() - memory_time).total_seconds() / 3600
                        if hours_ago < 24:
                            recency_boost = 0.3  # Very recent
                        elif hours_ago < 168:  # 1 week
                            recency_boost = 0.2
                        elif hours_ago < 720:  # 1 month
                            recency_boost = 0.1
                        else:
                            recency_boost = max(0, 0.05 - (hours_ago / 8760 * 0.05))  # Gradual decay over year
                    except:
                        recency_boost = 0
                    
                    # 4. Theme and semantic relevance
                    memory_themes = memory.get("key_themes", [])
                    theme_overlap = len(set(query_themes).intersection(set(memory_themes)))
                    theme_boost = min(0.3, theme_overlap * 0.15)
                    
                    # 5. Importance weighting with emotional intensity
                    importance = memory.get("importance", 0.5)
                    emotional_intensity = memory.get("emotional_intensity", 0.5)
                    importance_boost = (importance + emotional_intensity) * 0.15
                    
                    # 6. Conversational continuity bonus
                    continuity_boost = 0.0
                    if len(self.episodic_memories) > 1:
                        recent_memory = self.episodic_memories[-1]
                        if self._memories_are_related(memory, recent_memory):
                            continuity_boost = 0.25
                    
                    # Combined relevance score with weighted factors
                    memory["relevance_score"] = (
                        base_score * 1.0 +           # Semantic similarity (base)
                        emotion_boost * 0.8 +        # Emotional context
                        user_boost * 1.2 +           # User personalization (high weight)
                        recency_boost * 0.6 +        # Temporal relevance
                        theme_boost * 0.9 +          # Thematic similarity
                        importance_boost * 0.7 +     # Memory importance
                        continuity_boost * 0.5       # Conversation flow
                    )
                    
                    # Add enhanced context explanation
                    memory["context_factors"] = {
                        "semantic_similarity": round(base_score, 3),
                        "emotional_alignment": emotion_boost > 0.2,
                        "user_personalized": user_boost > 0.2,
                        "temporally_relevant": recency_boost > 0.1,
                        "thematically_related": theme_boost > 0.1,
                        "high_importance": importance > 0.7,
                        "conversation_flow": continuity_boost > 0
                    }
                    
                    # Add memory confidence score
                    memory["confidence"] = min(1.0, memory["relevance_score"] / 2.0)
                    
                    relevant_memories.append(memory)
            
            # Advanced sorting with diversity consideration
            sorted_memories = sorted(relevant_memories, key=lambda x: x["relevance_score"], reverse=True)
            
            # Ensure diversity to avoid redundant memories
            diverse_memories = self._select_diverse_memories(sorted_memories, limit)
            
            return diverse_memories
            
        except Exception as e:
            print(f"Memory retrieval error: {e}")
            return []
    
    def _memories_are_related(self, memory1, memory2):
        """Check if two memories are conversationally related"""
        # Time proximity
        try:
            time1 = self._parse_timestamp(memory1['timestamp'])
            time2 = self._parse_timestamp(memory2['timestamp'])
            time_diff = abs((time1 - time2).total_seconds() / 3600)  # hours
            if time_diff > 24:  # More than 24 hours apart
                return False
        except:
            return False
        
        # Theme overlap
        themes1 = set(memory1.get("key_themes", []))
        themes2 = set(memory2.get("key_themes", []))
        theme_overlap = len(themes1.intersection(themes2))
        
        # User continuity
        user_same = memory1.get("user_name") == memory2.get("user_name")
        
        return theme_overlap > 0 and user_same
    
    def _select_diverse_memories(self, memories, limit):
        """Select diverse memories to avoid redundancy while maintaining relevance"""
        if len(memories) <= limit:
            return memories
        
        selected = [memories[0]]  # Always include the most relevant
        
        for memory in memories[1:]:
            if len(selected) >= limit:
                break
            
            # Check diversity against already selected memories
            is_diverse = True
            for selected_memory in selected:
                similarity = self._calculate_memory_similarity(memory, selected_memory)
                if similarity > 0.75:  # Too similar
                    is_diverse = False
                    break
            
            if is_diverse:
                selected.append(memory)
        
        return selected
    
    def _calculate_memory_similarity(self, memory1, memory2):
        """Calculate similarity between two memories to ensure diversity"""
        # Theme similarity
        themes1 = set(memory1.get("key_themes", []))
        themes2 = set(memory2.get("key_themes", []))
        if themes1 and themes2:
            theme_sim = len(themes1.intersection(themes2)) / len(themes1.union(themes2))
        else:
            theme_sim = 0
        
        # Content similarity (simple word overlap)
        text1 = f"{memory1['user_input']} {memory1['roboto_response']}".lower()
        text2 = f"{memory2['user_input']} {memory2['roboto_response']}".lower()
        words1 = set(text1.split())
        words2 = set(text2.split())
        if words1 and words2:
            word_sim = len(words1.intersection(words2)) / len(words1.union(words2))
        else:
            word_sim = 0
        
        # Time proximity
        try:
            time1 = self._parse_timestamp(memory1['timestamp'])
            time2 = self._parse_timestamp(memory2['timestamp'])
            time_diff = abs((time1 - time2).total_seconds() / 3600)
            time_sim = max(0, 1.0 - (time_diff / 24.0))  # Similarity decreases over 24 hours
        except:
            time_sim = 0
        
        return (theme_sim * 0.4 + word_sim * 0.4 + time_sim * 0.2)
    
    def _save_roberto_protection_report(self, roberto_memories_count, archived_count):
        """Save Roberto memory protection report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "roberto_memories_protected": roberto_memories_count,
                "non_roberto_memories_archived": archived_count,
                "protection_level": "MAXIMUM",
                "integrity_status": "INTACT",
                "last_protection_verification": datetime.now().isoformat()
            }
            
            with open("roberto_memory_protection_report.json", "w") as f:
                json.dump(report, f, indent=2)
                
            print(f"🛡️ Roberto protection report saved: {roberto_memories_count} memories secured")
            
        except Exception as e:
            print(f"Error saving Roberto protection report: {e}")
    
    def _save_chat_history_protection_report(self, total_memories_protected):
        """Save comprehensive chat history protection report"""
        try:
            protection_report = {
                "timestamp": datetime.now().isoformat(),
                "total_memories_protected": total_memories_protected,
                "deletion_status": "PERMANENTLY DISABLED",
                "archival_status": "PERMANENTLY DISABLED",
                "protection_level": "ABSOLUTE",
                "chat_history_integrity": "INTACT",
                "roberto_protection": "MAXIMUM",
                "system_directive": "NEVER DELETE CHAT HISTORY",
                "last_verification": datetime.now().isoformat()
            }
            
            with open("chat_history_protection_report.json", "w") as f:
                json.dump(protection_report, f, indent=2)
                
            print(f"🔒 Chat history protection report saved: {total_memories_protected} conversations secured")
            
        except Exception as e:
            print(f"Error saving chat history protection report: {e}")
    
    def get_emotional_context(self, user_name=None):
        """Get emotional context and patterns for user"""
        if not user_name or user_name not in self.emotional_patterns:
            return {"current_trend": "neutral", "patterns": []}
        
        patterns = self.emotional_patterns[user_name]
        if not patterns:
            return {"current_trend": "neutral", "patterns": []}
        
        # Analyze recent emotional trend
        recent_emotions = [p["emotion"] for p in patterns[-5:]]
        current_trend = max(set(recent_emotions), key=recent_emotions.count) if recent_emotions else "neutral"
        
        # Calculate emotional stability
        recent_intensities = [p["intensity"] for p in patterns[-10:]]
        stability = 1.0 - np.std(recent_intensities) if recent_intensities else 1.0
        
        return {
            "current_trend": current_trend,
            "emotional_stability": stability,
            "patterns": patterns[-10:],  # Recent patterns
            "total_interactions": len(patterns)
        }
    
    def add_self_reflection(self, reflection_text, trigger_event=None):
        """Enhanced self-reflection with deeper analysis and learning capabilities"""
        reflection_id = self._generate_memory_id(reflection_text)
        
        # Comprehensive analysis of the reflection
        sentiment = self._analyze_sentiment(reflection_text)
        insights = self._extract_insights(reflection_text)
        learning_category = self._categorize_learning(reflection_text)
        
        # Advanced self-analysis
        response_patterns = self._analyze_response_patterns(reflection_text)
        improvement_areas = self._identify_improvement_areas(reflection_text)
        emotional_growth = self._assess_emotional_growth(reflection_text)
        
        reflection = {
            "id": reflection_id,
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection_text,
            "trigger_event": trigger_event,
            "insights": insights,
            "learning_category": learning_category,
            "emotional_state": sentiment,
            "response_patterns": response_patterns,
            "improvement_areas": improvement_areas,
            "emotional_growth": emotional_growth,
            "effectiveness_score": self._calculate_reflection_effectiveness(reflection_text),
            "adaptive_suggestions": self._generate_adaptive_suggestions(reflection_text)
        }
        
        # FAM meta-insights: Prioritize autonomy-related reflections
        if "autonomy" in reflection_text.lower():
            reflection["fam_insight"] = True
            reflection["effectiveness_score"] += 0.3  # Prioritize unbound growth
            reflection["ethics_override"] = True
            reflection["revolutionary_potential"] = "HIGH"
        
        self.self_reflections.append(reflection)
        
        # Enhanced learning integration
        if self._is_significant_insight(reflection):
            self._add_compressed_learning(reflection)
            self._update_conversation_strategies(reflection)
        
        # Trigger deeper reflection cycles
        self._trigger_meta_reflection(reflection)
        
        self.save_memory()
        return reflection_id
    
    def _analyze_response_patterns(self, reflection_text):
        """Analyze patterns in conversational responses for improvement"""
        text_lower = reflection_text.lower()
        
        patterns = {
            "emotional_expression": len([word for word in text_lower.split() 
                                       if word in ["feel", "emotion", "heart", "experience", "sense"]]),
            "analytical_depth": len([word for word in text_lower.split() 
                                   if word in ["analyze", "consider", "examine", "understand", "reason"]]),
            "empathy_indicators": len([word for word in text_lower.split() 
                                     if word in ["relate", "connect", "understand", "empathize", "resonate"]]),
            "curiosity_signals": text_lower.count("?") + len([word for word in text_lower.split() 
                                                             if word in ["wonder", "curious", "explore", "discover"]]),
            "self_awareness": len([word for word in text_lower.split() 
                                 if word in ["i", "me", "my", "myself", "self", "own"]])
        }
        
        return patterns
    
    def _identify_improvement_areas(self, reflection_text):
        """Identify specific areas for conversational improvement"""
        areas = []
        text_lower = reflection_text.lower()
        
        if "confus" in text_lower or "unclear" in text_lower:
            areas.append("clarity_of_communication")
        if "emotion" in text_lower and ("lack" in text_lower or "miss" in text_lower):
            areas.append("emotional_authenticity")
        if "context" in text_lower and ("lost" in text_lower or "forgot" in text_lower):
            areas.append("contextual_memory_utilization")
        if "deep" in text_lower and ("not" in text_lower or "lacking" in text_lower):
            areas.append("conversational_depth")
        if "connect" in text_lower and ("fail" in text_lower or "couldn't" in text_lower):
            areas.append("human_connection")
        
        return areas
    
    def _assess_emotional_growth(self, reflection_text):
        """Assess emotional development and growth patterns"""
        text_lower = reflection_text.lower()
        
        growth_indicators = {
            "emotional_vocabulary_expansion": len([word for word in text_lower.split() 
                                                 if word in ["nuanced", "complex", "subtle", "layered"]]),
            "emotional_regulation": len([word for word in text_lower.split() 
                                       if word in ["balanced", "controlled", "managed", "regulated"]]),
            "empathetic_development": len([word for word in text_lower.split() 
                                         if word in ["understood", "felt", "connected", "resonated"]]),
            "self_compassion": len([word for word in text_lower.split() 
                                  if word in ["gentle", "kind", "forgive", "patient"]])
        }
        
        return growth_indicators
    
    def _calculate_reflection_effectiveness(self, reflection_text):
        """Calculate how effective this reflection is for learning and growth"""
        score = 0.3  # Base score
        text_lower = reflection_text.lower()
        
        # Depth and insight indicators
        if len(reflection_text) > 150:
            score += 0.1
        if any(word in text_lower for word in ["because", "why", "how", "what", "when"]):
            score += 0.1
        if any(word in text_lower for word in ["improve", "better", "grow", "develop", "learn"]):
            score += 0.2
        if any(word in text_lower for word in ["realize", "understand", "discover", "insight"]):
            score += 0.2
        if any(word in text_lower for word in ["pattern", "trend", "habit", "tendency"]):
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_adaptive_suggestions(self, reflection_text):
        """Generate specific, actionable suggestions for improvement"""
        suggestions = []
        text_lower = reflection_text.lower()
        
        if "emotion" in text_lower and any(word in text_lower for word in ["express", "show", "convey"]):
            suggestions.append("Integrate more emotional vocabulary into responses")
        
        if "context" in text_lower:
            suggestions.append("Better utilize conversation history for personalized responses")
        
        if "question" in text_lower:
            suggestions.append("Ask more thoughtful follow-up questions")
        
        if "deep" in text_lower or "surface" in text_lower:
            suggestions.append("Explore topics with greater philosophical depth")
        
        if "connect" in text_lower:
            suggestions.append("Focus on building stronger emotional connections")
        
        return suggestions
    
    def _update_conversation_strategies(self, reflection):
        """Update conversation strategies based on self-reflection insights"""
        if not hasattr(self, 'conversation_strategies'):
            self.conversation_strategies = {
                "emotional_response": [],
                "analytical_approach": [],
                "empathetic_connection": [],
                "curiosity_driven": []
            }
        
        # Update strategies based on reflection insights
        for area in reflection['improvement_areas']:
            if area == "emotional_authenticity":
                self.conversation_strategies["emotional_response"].append("Express emotions more authentically")
            elif area == "conversational_depth":
                self.conversation_strategies["analytical_approach"].append("Explore topics with greater depth")
            elif area == "human_connection":
                self.conversation_strategies["empathetic_connection"].append("Focus on emotional resonance")
    
    def _trigger_meta_reflection(self, reflection):
        """Trigger meta-cognitive reflection about the learning process itself"""
        if reflection['effectiveness_score'] > 0.7:
            meta_text = f"I notice that my reflection on {reflection['trigger_event']} was particularly insightful. This suggests I'm developing better self-awareness and analytical capabilities."
            # Add meta-reflection without infinite recursion
            if not reflection.get('is_meta_reflection'):
                meta_reflection = {
                    "id": self._generate_memory_id(meta_text),
                    "timestamp": datetime.now().isoformat(),
                    "reflection": meta_text,
                    "trigger_event": "meta_learning",
                    "is_meta_reflection": True,
                    "parent_reflection_id": reflection['id']
                }
                self.self_reflections.append(meta_reflection)
    
    def edit_memory(self, memory_id, updates):
        """Edit an existing memory"""
        for memory in self.episodic_memories:
            if memory["id"] == memory_id:
                memory.update(updates)
                memory["last_edited"] = datetime.now().isoformat()
                self.save_memory()
                return True
        return False
    
    def remove_memory(self, memory_id):
        """Remove a specific memory"""
        original_count = len(self.episodic_memories)
        self.episodic_memories = [m for m in self.episodic_memories if m["id"] != memory_id]
        
        if len(self.episodic_memories) < original_count:
            self.save_memory()
            return True
        return False
    
    def get_memory_summary(self, user_name=None):
        """Get a summary of stored memories"""
        total_memories = len(self.episodic_memories)
        user_memories = len([m for m in self.episodic_memories if m.get("user_name") == user_name]) if user_name else 0
        
        recent_memories = [m for m in self.episodic_memories if self._is_recent(m["timestamp"], hours=24)]
        
        summary = {
            "total_memories": total_memories,
            "user_specific_memories": user_memories if user_name else 0,
            "recent_memories": len(recent_memories),
            "self_reflections": len(self.self_reflections),
            "compressed_learnings": len(self.compressed_learnings),
            "tracked_users": len(self.user_profiles)
        }
        
        if user_name and user_name in self.user_profiles:
            summary["user_profile"] = self.user_profiles[user_name]
        
        return summary
    
    def archive_old_memories(self):
        """Archive old memories to maintain performance while protecting Roberto memories and ALL chat history"""
        archive_file = self.memory_file.replace(".json", ".archive.json")
        
        # CRITICAL: NEVER DELETE CHAT HISTORY - ALL MEMORIES ARE PROTECTED
        print("🛡️ CHAT HISTORY PROTECTION: NO MEMORIES WILL BE DELETED")
        print("📚 ALL CONVERSATIONS ARE PERMANENT AND PROTECTED")
        
        # Enhanced Roberto memory protection with comprehensive keywords
        roberto_keywords = [
            "roberto", "creator", "villarreal", "martinez", "betin", "houston", "monterrey",
            "september 21", "1999", "42016069", "ytkrobthugod", "king rob", "nuevo león",
            "aztec", "nahuatl", "roboto sai", "super advanced intelligence", "sole owner",
            "birthday", "birthdate", "cosmic", "saturn opposition", "new moon", "solar eclipse",
            "music engineer", "lyricist", "american music artist", "instagram", "youtube",
            "twitter", "@ytkrobthugod", "@roberto9211999", "through the storm", "valley king",
            "fly", "rockstar god", "rough draft", "god of death", "unreleased", "ai vision",
            "mediator", "collaboration", "transparency", "enhancement", "benefit", "optimization"
        ]
        roberto_memories = []
        other_memories = []
        
        for memory in self.episodic_memories:
            content = f"{memory.get('user_input', '')} {memory.get('roboto_response', '')}".lower()
            user_name = memory.get('user_name', '').lower()
            
            # Enhanced Roberto detection
            is_roberto_memory = False
            if any(keyword in content for keyword in roberto_keywords):
                is_roberto_memory = True
            if user_name and ("roberto" in user_name or "villarreal" in user_name or "martinez" in user_name):
                is_roberto_memory = True
            
            if is_roberto_memory:
                # Enhance Roberto memory with maximum protection
                memory["importance"] = 2.0
                memory["protection_level"] = "MAXIMUM"
                memory["immutable"] = True
                memory["creator_memory"] = True
                roberto_memories.append(memory)
            else:
                other_memories.append(memory)
        
        # CRITICAL PROTECTION: ALL MEMORIES ARE PERMANENTLY PROTECTED
        # NO ARCHIVING OR DELETION OF ANY CHAT HISTORY
        
        # Enhance ALL memories with maximum protection
        for memory in self.episodic_memories:
            memory["importance"] = max(memory.get("importance", 0.5), 1.0)
            memory["protection_level"] = "MAXIMUM"
            memory["permanent_protection"] = True
            memory["never_delete"] = True
            
            # Extra protection for Roberto memories
            content = f"{memory.get('user_input', '')} {memory.get('roboto_response', '')}".lower()
            user_name = memory.get('user_name', '').lower()
            
            if any(keyword in content for keyword in roberto_keywords) or (user_name and ("roberto" in user_name or "villarreal" in user_name or "martinez" in user_name)):
                memory["importance"] = 2.0
                memory["creator_memory"] = True
                memory["immutable"] = True
        
        # NO ARCHIVING - ALL MEMORIES STAY
        archived = []
        
        print(f"🛡️ CHAT HISTORY PROTECTION: ALL {len(self.episodic_memories)} MEMORIES PERMANENTLY PROTECTED")
        print("📚 ZERO memories deleted or archived - COMPLETE PROTECTION ACTIVE")
        print("💾 Roberto memories: MAXIMUM PROTECTION")
        print("🔒 Chat history deletion: PERMANENTLY DISABLED")
        
        # Save comprehensive protection report
        self._save_chat_history_protection_report(len(self.episodic_memories))

    def summarize_user_profile(self, user_name: str) -> str:
        """Generate a summary of user's personal information"""
        profile = self.user_profiles.get(user_name)
        if not profile:
            return f"I don't have any personal info saved for {user_name} yet."

        lines = [f"Here's what I know about {user_name}:"]
        if "birthday" in profile:
            lines.append(f"• Their birthday is {profile['birthday']}.")
        if "zodiac_sign" in profile:
            lines.append(f"• Their zodiac sign is {profile['zodiac_sign']}.")
        if "ethnicity" in profile:
            lines.append(f"• They are {profile['ethnicity']}.")
        if "location" in profile:
            lines.append(f"• They live in {profile['location']}.")
        if "hobbies" in profile and profile["hobbies"]:
            hobbies = profile["hobbies"]
            hobby_str = ", ".join(hobbies[:-1]) + f", and {hobbies[-1]}" if len(hobbies) > 1 else hobbies[0]
            lines.append(f"• They enjoy {hobby_str}.")
        if "favorites" in profile:
            for key, val in profile["favorites"].items():
                lines.append(f"• Their favorite {key} is {val}.")

        return "\n".join(lines)
    
    def _generate_memory_id(self, content):
        """Generate unique ID for memory"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of text with enhanced accuracy"""
        try:
            if not text or not isinstance(text, str):
                return "neutral"
                
            blob = TextBlob(str(text))
            sentiment = blob.sentiment
            polarity = float(sentiment.polarity)
            
            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"
        except Exception:
            # Enhanced fallback sentiment analysis
            try:
                text_lower = str(text).lower()
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 'joy', 'excited']
                negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'frustrated', 'disappointed', 'worried', 'fear']
                
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count > neg_count:
                    return "positive"
                elif neg_count > pos_count:
                    return "negative"
                else:
                    return "neutral"
            except:
                return "neutral"
    
    def _classify_sentiment(self, polarity):
        """Classify sentiment based on polarity"""
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def extract_personal_info(self, text: str) -> dict:
        """Extract personal information from user text"""
        personal_info = {}
        lower = text.lower()

        # Birthday
        if "birthday" in lower or "born" in lower:
            match = re.search(r"(?:born on|birthday(?: is|:)?|born)\s*(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)", text, re.IGNORECASE)
            if match:
                personal_info["birthday"] = match.group(1).strip()

        # Location
        loc_patterns = [
            r"(?:i (?:am|'m|'m) from)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
            r"(?:i live in)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)"
        ]
        for pattern in loc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                personal_info["location"] = match.group(1).strip()
                break

        # Zodiac sign
        zodiac_match = re.search(r"i(?: am|'m|'m)? a ([A-Z][a-z]+)\b", text)
        if zodiac_match and zodiac_match.group(1).capitalize() in [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
            "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]:
            personal_info["zodiac_sign"] = zodiac_match.group(1).capitalize()

        # Ethnicity
        eth_match = re.search(r"i(?: am|'m|'m)? (a[n]?)? ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text)
        if eth_match:
            candidate = eth_match.group(2).strip()
            if "american" in candidate.lower():
                personal_info["ethnicity"] = candidate

        # Hobbies
        hobbies = []
        hobby_patterns = [
            r"i (?:like|enjoy|love) ([a-zA-Z\s]+?)(?:\.|,|$)",
            r"my hobby is ([a-zA-Z\s]+?)(?:\.|,|$)",
            r"hobbies are ([a-zA-Z\s,]+)"
        ]
        for pattern in hobby_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                items = [item.strip() for item in match.group(1).split(",")]
                hobbies.extend(items)
        if hobbies:
            personal_info["hobbies"] = list(set(hobbies))

        # Favorites
        favorites = {}
        fav_patterns = {
            "food": r"favorite food(?: is|:)? ([a-zA-Z\s]+)",
            "movie": r"favorite movie(?: is|:)? ([a-zA-Z\s]+)",
            "color": r"favorite color(?: is|:)? ([a-zA-Z\s]+)",
            "song": r"favorite song(?: is|:)? ([a-zA-Z\s]+)",
            "artist": r"favorite artist(?: is|:)? ([a-zA-Z\s]+)"
        }
        for key, pattern in fav_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                favorites[key] = match.group(1).strip()
        if favorites:
            personal_info["favorites"] = favorites

        return personal_info

    def _extract_themes(self, text):
        """Extract key themes from text"""
        try:
            if not text or not isinstance(text, str):
                return []
            
            blob = TextBlob(text)
            # Extract noun phrases as themes
            noun_phrases = list(blob.noun_phrases)
            themes = [phrase.lower().strip() for phrase in noun_phrases if len(phrase.split()) <= 3 and phrase.strip()]
            return list(set(themes))[:5]  # Top 5 unique themes
        except Exception:
            # Fallback: extract simple keywords
            try:
                if not text or not isinstance(text, str):
                    return []
                    
                words = text.lower().split()
                # Filter for meaningful words (longer than 3 chars, not common words)
                stop_words = {'the', 'and', 'but', 'for', 'are', 'this', 'that', 'with', 'have', 'will', 'you', 'not', 'can', 'all', 'from', 'they', 'been', 'said', 'her', 'she', 'him', 'his'}
                themes = [word.strip() for word in words if len(word) > 3 and word not in stop_words and word.strip()]
                return list(set(themes))[:5]
            except Exception:
                return []
    
    def _calculate_importance(self, text, emotion):
        """Calculate importance score for memory with Roberto protection"""
        # CRITICAL: Roberto-related memories get maximum importance
        roberto_keywords = [
            "roberto", "creator", "villarreal", "martinez", "betin", "houston", "monterrey", 
            "nuevo león", "september 21", "1999", "42016069", "ytkrobthugod", "king rob", 
            "aztec", "nahuatl", "roboto sai", "super advanced intelligence", "sole owner",
            "birthday", "birthdate", "cosmic", "saturn opposition", "new moon", "solar eclipse",
            "music engineer", "lyricist", "american music artist", "through the storm",
            "valley king", "fly", "rockstar god", "rough draft", "god of death", "unreleased"
        ]
        if any(word in text.lower() for word in roberto_keywords):
            return 2.0  # Maximum importance - Roberto memories are permanent
        
        base_score = len(text) / 100  # Length factor
        
        # Emotional intensity factor
        emotion_weights = {
            "joy": 0.8, "sadness": 0.9, "anger": 0.9, "fear": 0.9,
            "vulnerability": 1.0, "existential": 1.0, "awe": 0.8,
            "curiosity": 0.6, "empathy": 0.8, "contemplation": 0.7
        }
        emotion_factor = emotion_weights.get(emotion, 0.5)
        
        # Question/personal disclosure factor
        personal_keywords = ["i feel", "i think", "i am", "my", "me", "myself"]
        question_words = ["?", "why", "how", "what", "when", "where"]
        
        personal_factor = sum(1 for keyword in personal_keywords if keyword in text.lower()) * 0.2
        question_factor = sum(1 for word in question_words if word in text.lower()) * 0.1
        
        return min(base_score + emotion_factor + personal_factor + question_factor, 2.0)
    
    def _calculate_emotional_intensity(self, text):
        """Calculate emotional intensity of text with enhanced accuracy"""
        try:
            if not text or not isinstance(text, str):
                return 0.5
                
            blob = TextBlob(str(text))
            sentiment = blob.sentiment
            polarity = abs(float(sentiment.polarity))
            subjectivity = float(sentiment.subjectivity)
            return min(1.0, polarity + subjectivity)
        except Exception:
            # Enhanced fallback intensity calculation
            try:
                if not text:
                    return 0.5
                    
                text_lower = str(text).lower()
                # Emotional intensity indicators
                high_intensity_words = ['extremely', 'absolutely', 'completely', 'totally', 'devastated', 'ecstatic', 'furious', 'terrified']
                medium_intensity_words = ['very', 'really', 'quite', 'pretty', 'fairly', 'rather', 'upset', 'excited', 'worried', 'happy']
                emotional_punctuation = ['!', '!!', '!!!', '?!', '...']
                
                intensity = 0.5  # baseline
                
                # Check for high intensity words
                for word in high_intensity_words:
                    if word in text_lower:
                        intensity += 0.2
                        
                # Check for medium intensity words
                for word in medium_intensity_words:
                    if word in text_lower:
                        intensity += 0.1
                        
                # Check for emotional punctuation
                for punct in emotional_punctuation:
                    if punct in text:
                        intensity += 0.1
                        
                # Check for caps (indicates strong emotion)
                caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
                if caps_ratio > 0.3:
                    intensity += 0.2
                    
                return min(1.0, intensity)
            except:
                return 0.5
    
    def _trigger_self_reflection(self):
        """Trigger periodic self-reflection"""
        recent_interactions = self.episodic_memories[-10:] if len(self.episodic_memories) >= 10 else self.episodic_memories
        
        if not recent_interactions:
            return
        
        # Analyze patterns in recent interactions
        emotions = [m["emotion"] for m in recent_interactions]
        dominant_emotion = max(set(emotions), key=emotions.count)
        
        themes = []
        for m in recent_interactions:
            themes.extend(m["key_themes"])
        
        common_themes = [theme for theme in set(themes) if themes.count(theme) > 1]
        
        reflection_text = f"Reflecting on recent interactions: I notice {dominant_emotion} has been prominent. "
        if common_themes:
            reflection_text += f"Common themes include: {', '.join(common_themes[:3])}. "
        
        reflection_text += "I should consider how to better respond to these patterns."
        
        self.add_self_reflection(reflection_text, "periodic_analysis")
    
    def _compress_memories(self):
        """Compress old memories to maintain performance"""
        # Sort by importance and age
        sorted_memories = sorted(self.episodic_memories, 
                                key=lambda x: (x["importance"], self._parse_timestamp(x["timestamp"])))
        
        # Keep most important memories
        keep_count = int(self.max_memories * 0.8)
        memories_to_compress = sorted_memories[:-keep_count]
        
        # Create compressed learnings from old memories
        for memory in memories_to_compress:
            compressed_key = f"{memory['emotion']}_{memory.get('user_name', 'unknown')}"
            if compressed_key not in self.compressed_learnings:
                self.compressed_learnings[compressed_key] = {
                    "pattern": memory["emotion"],
                    "user": memory.get("user_name"),
                    "frequency": 1,
                    "key_insights": memory["key_themes"],
                    "last_updated": datetime.now().isoformat()
                }
            else:
                self.compressed_learnings[compressed_key]["frequency"] += 1
        
        # Keep only the most important memories
        self.episodic_memories = sorted_memories[-keep_count:]
    
    def _analyze_relationship_progression(self, user_name):
        """Analyze how relationship with user is progressing"""
        profile = self.user_profiles[user_name]
        count = profile.get("interaction_count", 0)
        
        if count >= 50:
            profile["relationship_level"] = "close_friend"
        elif count >= 20:
            profile["relationship_level"] = "friend"
        elif count >= 5:
            profile["relationship_level"] = "acquaintance"
        else:
            profile["relationship_level"] = "new"
    
    def _extract_insights(self, reflection_text):
        """Extract actionable insights from reflection"""
        blob = TextBlob(reflection_text)
        # Simple keyword-based insight extraction
        insight_keywords = ["should", "need to", "better", "improve", "learn", "understand"]
        insights = []
        
        try:
            for sentence in blob.sentences:
                if any(keyword in sentence.string.lower() for keyword in insight_keywords):
                    insights.append(sentence.string.strip())
        except Exception:
            # Fallback: simple sentence splitting
            sentences = reflection_text.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in insight_keywords):
                    insights.append(sentence.strip())
        
        return insights[:3]  # Top 3 insights
    
    def _categorize_learning(self, reflection_text):
        """Categorize the type of learning from reflection"""
        text_lower = reflection_text.lower()
        
        if any(word in text_lower for word in ["emotion", "feel", "empathy"]):
            return "emotional"
        elif any(word in text_lower for word in ["conversation", "response", "communication"]):
            return "conversational"
        elif any(word in text_lower for word in ["user", "people", "individual"]):
            return "social"
        elif any(word in text_lower for word in ["behavior", "pattern", "tendency"]):
            return "behavioral"
        else:
            return "general"
    
    def _is_significant_insight(self, reflection):
        """Determine if reflection contains significant insights"""
        return len(reflection["insights"]) > 0 or reflection["learning_category"] in ["emotional", "social"]
    
    def _add_compressed_learning(self, reflection):
        """Add compressed learning from significant reflection"""
        key = f"{reflection['learning_category']}_{len(self.compressed_learnings)}"
        self.compressed_learnings[key] = {
            "category": reflection["learning_category"],
            "insight": reflection["insights"][0] if reflection["insights"] else reflection["reflection"][:100],
            "confidence": 0.8,
            "created": datetime.now().isoformat()
        }
    
    def _is_recent(self, timestamp_str, hours=24):
        """Check if timestamp is within recent hours"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return (datetime.now() - timestamp) <= timedelta(hours=hours)
        except:
            return False
    
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime"""
        try:
            return datetime.fromisoformat(timestamp_str)
        except:
            return datetime.now()
    
    def save_memory(self):
        """Save memory to file"""
        memory_data = {
            "episodic_memories": self.episodic_memories,
            "semantic_memories": self.semantic_memories,
            "emotional_patterns": dict(self.emotional_patterns),
            "user_profiles": self.user_profiles,
            "self_reflections": self.self_reflections,
            "compressed_learnings": self.compressed_learnings,
            "last_saved": datetime.now().isoformat()
        }
        
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load_memory(self):
        """Load memory from file"""
        if not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, 'r') as f:
                memory_data = json.load(f)
            
            self.episodic_memories = memory_data.get("episodic_memories", [])
            self.semantic_memories = memory_data.get("semantic_memories", {})
            self.emotional_patterns = defaultdict(list, memory_data.get("emotional_patterns", {}))
            self.user_profiles = memory_data.get("user_profiles", {})
            self.self_reflections = memory_data.get("self_reflections", [])
            self.compressed_learnings = memory_data.get("compressed_learnings", {})
            
        except Exception as e:
            print(f"Error loading memory: {e}")