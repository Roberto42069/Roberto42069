import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, deque
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
        profile["interaction_count"] += 1
        profile["last_interaction"] = datetime.now().isoformat()
        
        # Update based on user_info
        if isinstance(user_info, dict):
            profile.update(user_info)
        
        # Analyze relationship progression
        self._analyze_relationship_progression(user_name)
        
        self.save_memory()
    
    def retrieve_relevant_memories(self, query, user_name=None, limit=5):
        """Retrieve memories with deeper contextual understanding"""
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
            
            # Get top memories with enhanced scoring
            top_indices = similarities.argsort()[-limit*2:][::-1]  # Get more candidates
            relevant_memories = []
            
            for idx in top_indices:
                if similarities[idx] > 0.05:  # Lower threshold for broader context
                    memory = self.episodic_memories[idx].copy()
                    base_score = similarities[idx]
                    
                    # Enhanced scoring factors
                    # 1. Emotional context matching
                    memory_emotion = memory.get("emotion", "neutral")
                    emotion_boost = 0.3 if query_sentiment == memory_emotion else 0.1
                    
                    # 2. User-specific boost
                    user_boost = 0.5 if user_name and memory.get("user_name") == user_name else 0
                    
                    # 3. Temporal relevance (recent conversations matter more)
                    try:
                        memory_time = self._parse_timestamp(memory['timestamp'])
                        days_ago = (datetime.now() - memory_time).days
                        recency_boost = max(0, 0.2 - (days_ago * 0.02))  # Decays over time
                    except:
                        recency_boost = 0
                    
                    # 4. Importance weighting
                    importance = memory.get("importance", 0.5)
                    importance_boost = importance * 0.2
                    
                    # Combined relevance score
                    memory["relevance_score"] = (base_score + emotion_boost + 
                                               user_boost + recency_boost + importance_boost)
                    
                    # Add context explanation for debugging
                    memory["context_factors"] = {
                        "similarity": base_score,
                        "emotional_match": emotion_boost > 0.2,
                        "user_specific": user_boost > 0,
                        "recent": recency_boost > 0.1,
                        "important": importance > 0.7
                    }
                    
                    relevant_memories.append(memory)
            
            # Sort by enhanced relevance score and return top results
            return sorted(relevant_memories, key=lambda x: x["relevance_score"], reverse=True)[:limit]
        except Exception as e:
            print(f"Memory retrieval error: {e}")
            return []
    
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
        """Archive old memories to maintain performance"""
        archive_file = self.memory_file.replace(".json", ".archive.json")
        scored = sorted(
            self.episodic_memories,
            key=lambda m: m["importance"] * m["emotional_intensity"]
        )
        archived = scored[:len(scored) - self.max_memories]
        self.episodic_memories = scored[-self.max_memories:]

        try:
            if os.path.exists(archive_file):
                with open(archive_file, 'r') as f:
                    existing = json.load(f)
            else:
                existing = []
            with open(archive_file, 'w') as f:
                json.dump(existing + archived, f, indent=2)
        except Exception as e:
            print(f"Error archiving memories: {e}")

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
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            polarity = float(sentiment.polarity)
            subjectivity = float(sentiment.subjectivity)
            return {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "classification": self._classify_sentiment(polarity)
            }
        except Exception:
            # Fallback sentiment analysis if TextBlob fails
            return {
                "polarity": 0.0,
                "subjectivity": 0.5,
                "classification": "neutral"
            }
    
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
            blob = TextBlob(text)
            # Extract noun phrases as themes
            noun_phrases = list(blob.noun_phrases)
            themes = [phrase.lower() for phrase in noun_phrases if len(phrase.split()) <= 3]
            return list(set(themes))[:5]  # Top 5 unique themes
        except Exception:
            # Fallback: extract simple keywords
            words = text.lower().split()
            # Filter for meaningful words (longer than 3 chars, not common words)
            stop_words = {'the', 'and', 'but', 'for', 'are', 'this', 'that', 'with', 'have', 'will', 'you', 'not', 'can', 'all', 'from', 'they', 'been', 'said', 'her', 'she', 'him', 'his'}
            themes = [word for word in words if len(word) > 3 and word not in stop_words]
            return list(set(themes))[:5]
    
    def _calculate_importance(self, text, emotion):
        """Calculate importance score for memory"""
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
        """Calculate emotional intensity of text"""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            return abs(float(sentiment.polarity)) + float(sentiment.subjectivity)
        except Exception:
            # Fallback: simple intensity calculation based on keywords
            emotional_words = ['very', 'extremely', 'really', 'so', 'absolutely', 'completely', 'totally']
            intensity = 0.5  # baseline
            words = text.lower().split()
            for word in emotional_words:
                if word in words:
                    intensity += 0.1
            return min(intensity, 1.0)
    
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
        count = profile["interaction_count"]
        
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