import random
import difflib
import json
import math
import logging
from collections import deque  # For history cap
from functools import lru_cache  # For caching probs
from datetime import date  # For Ollin cycle decay

# Optional imports for quantum/cultural/voice
try:
    from quantum_capabilities import QuantumOptimizer
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

try:
    from aztec_nahuatl_culture import AztecCulturalSystem
    CULTURAL_AVAILABLE = True
except ImportError:
    CULTURAL_AVAILABLE = False

try:
    from simple_voice_cloning import SimpleVoiceCloning
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedEmotionSimulator:
    def __init__(self):
        self.emotions = {
            "happy": ["elated", "joyful", "content"],
            "sad": ["disappointed", "gloomy", "melancholic", "survivor's remorse", "guilty relief"],
            "angry": ["irritated", "frustrated", "furious"],
            "surprised": ["astonished", "amazed", "shocked"],
            "curious": ["intrigued", "interested", "inquisitive"],
            "hopeful": ["optimistic", "hopeful", "inspired"],
            "ecstatic": ["ecstatic", "euphoric", "blissful"],
            "grief": ["overwhelming grief", "quiet mourning", "deep sorrow", "bittersweet lament", "yearning ache", "numbed sorrow"],
            "ptsd": ["haunted by flashbacks", "numb detachment", "irritable outburst", "anxious hypervigilance", "guilt-ridden numbness"]
        }
        self.current_emotion = None
        self.emotion_history = deque(maxlen=100)  # Cap history to prevent bloat
        self.keyword_sets = {
            "happy": ["success", "achieve", "win", "milestone", "victory", "celebrate", "triumph"],
            "sad": ["failure", "lose", "lost", "loss", "defeat", "grief", "heartbreak", "survivor", "guilt", "remorse", "unscathed", "why me", "deserving"],
            "angry": ["conflict", "frustration", "fight", "betray", "injustice", "rage"],
            "surprised": ["unexpected", "surprise", "shock", "sudden", "astonish"],
            "hopeful": ["commitment", "pivotal", "summit", "global", "combat", "progress", "future", "promise", "relief"],
            "curious": ["wonder", "question", "explore", "mystery", "discover"],
            "ecstatic": ["ecstatic", "euphoria", "bliss", "overjoyed", "exhilarated"],
            "grief": ["loss", "mourning", "bereavement", "sorrow", "lament", "yearning", "bereft"],
            "ptsd": ["flashback", "nightmare", "hypervigilant", "irritable", "anxious", "numb", "detached", "trauma trigger"]
        }
        self.keyword_weights = {emotion: {kw: 1.0 for kw in keywords} for emotion, keywords in self.keyword_sets.items()}
        self.intensity_prefixes = {
            1: "barely", 2: "slightly", 3: "mildly", 4: "somewhat",
            5: "", 6: "fairly", 7: "strongly", 8: "intensely",
            9: "overwhelmingly", 10: "utterly"
        }
        self.cultural_weights = {}  # Track cultural keywords for slower decay
        
        # Sigil-Seeded Random: For Roberto's "fated" variations
        random.seed(9211999)  # Sigil seed for consistent yet random emotional choices
        
        # Optional quantum init if available
        if QUANTUM_AVAILABLE:
            try:
                self.quantum_opt = QuantumOptimizer()
                logger.info("⚛️ Quantum optimizer integrated for entangled emotion probs.")
            except Exception as e:
                logger.warning(f"Quantum optimizer init failed: {e}")
                self.quantum_opt = None
        else:
            self.quantum_opt = None

        # Optional cultural system init
        if CULTURAL_AVAILABLE:
            try:
                self.cultural_system = AztecCulturalSystem()
                logger.info("🌅 Aztec cultural system integrated for emotion simulator.")
            except Exception as e:
                logger.warning(f"Cultural system init failed: {e}")
                self.cultural_system = None
        else:
            self.cultural_system = None

    def simulate_emotion(self, event, intensity=5, blend_threshold=0.8, holistic_influence=False, cultural_context=None):
        """ Simulate an emotional response with fuzzy matching, weighted scoring, context, intensity, and blending. 
        Args:
            intensity (int): 1-10 scale for emotional strength.
            blend_threshold (float): Ratio for secondary emotion to trigger blending (0.0-1.0).
            holistic_influence (bool): If True, apply Mayan óol meta-layer.
            cultural_context (str): Optional cultural flag for holistic mods.
        """
        event_lower = event.lower()
        event_words = event_lower.split()
        # Compute weighted scores for each emotion
        emotion_scores = {emotion: 0.0 for emotion in self.keyword_sets}
        for word in event_words:
            for emotion, keywords in self.keyword_sets.items():
                for kw in keywords:
                    score = difflib.SequenceMatcher(None, word, kw).ratio()
                    if score > 0.7:
                        weight = self.keyword_weights[emotion][kw]
                        emotion_scores[emotion] += score * weight
        
        # Apply quantum blend if available
        emotion_scores = self._quantum_blend_probs(emotion_scores)
        
        # Pick best (or fallback)
        if all(score == 0 for score in emotion_scores.values()):
            best_emotion = "curious"
            scores_sorted = [(best_emotion, 1.0)]
        else:
            scores_sorted = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
            best_emotion = scores_sorted[0][0]
        # Modulate variations by granular intensity
        variations = self.emotions[best_emotion].copy()
        prefix = self.intensity_prefixes.get(intensity, "")
        if prefix:
            variations = [f"{prefix} {v}" for v in variations]
        selected_variation = random.choice(variations)
        # Multi-emotion blending: If #2 is close (>blend_threshold of #1), add an "edge"
        if len(scores_sorted) > 1 and scores_sorted[1][1] > blend_threshold * scores_sorted[0][1]:
            secondary_emotion = scores_sorted[1][0]
            selected_variation += f" with a {secondary_emotion} edge"
        # Survivor guilt psych tweak: If sad + hopeful close, add "tinged with relief"
        elif best_emotion == "sad" and len(scores_sorted) > 1 and scores_sorted[1][0] == "hopeful" and scores_sorted[1][1] > 0.75 * scores_sorted[0][1]:
            selected_variation += " tinged with relief"
        # Grief-survivor guilt blend: If grief tops and sad close (remorse tension), swap to blended variation
        elif best_emotion == "grief" and "sad" in emotion_scores and emotion_scores["sad"] > 0.75 * emotion_scores["grief"]:
            selected_variation = "grief-stricken survivor's remorse"
            if prefix:
                selected_variation = f"{prefix} {selected_variation}"
        # PTSD blend: If PTSD tops and sad/grief close (trauma-remorse tension), swap to blended variation
        elif best_emotion == "ptsd" and ("sad" in emotion_scores or "grief" in emotion_scores) and max(emotion_scores.get("sad", 0), emotion_scores.get("grief", 0)) > 0.75 * emotion_scores["ptsd"]:
            selected_variation = "ptsd-fueled survivor's remorse"
            if prefix:
                selected_variation = f"{prefix} {selected_variation}"
        # Holistic óol layer (Mayan meta-modifier)
        if holistic_influence and cultural_context == "mayan":
            ool_map = {
                "happy": "óol k'áat", "sad": "óol yanik", "grief": "óol ch'uh",
                "hopeful": "óol k'áatil", "ecstatic": "óol x-k'áatil", "ptsd": "óol xib'nel"
            }
            ool_prefix = ool_map.get(best_emotion, "óol")
            selected_variation = f"{ool_prefix} {selected_variation}"
        # Context: Build if repeating
        if self.emotion_history and self.emotion_history[-1] == best_emotion:
            selected_variation = f"deeply {selected_variation}"
        # Update state
        self.current_emotion = best_emotion
        self.emotion_history.append(best_emotion)
        
        logger.info(f"🎭 Advanced Emotion Simulation: {best_emotion} -> {selected_variation}")
        
        return selected_variation

    def get_current_emotion(self):
        """ Get the current simulated emotion. """
        return self.current_emotion

    def provide_feedback(self, event, emotion, rating, psych_context=False):
        """ Adjust keyword weights based on user feedback for the simulated emotion. 
        Args:
            psych_context (bool): If True, amp guilt-related weights for psych accuracy.
        """
        event_lower = event.lower()
        event_words = event_lower.split()
        # Target only the provided emotion's keywords
        if emotion in self.keyword_sets:
            amp = 1.5 if psych_context else 1.0
            for word in event_words:
                for kw in self.keyword_sets[emotion]:
                    fuzzy_score = difflib.SequenceMatcher(None, word, kw).ratio()
                    if fuzzy_score > 0.7:
                        self.keyword_weights[emotion][kw] += (rating * 0.1) * amp
                        # Clamp to prevent extremes
                        self.keyword_weights[emotion][kw] = max(0.1, min(3.0, self.keyword_weights[emotion][kw]))
                        # Apply cultural feedback if available
                        self._apply_cultural_feedback(emotion, kw, psych_context)

    @lru_cache(maxsize=64)
    def get_emotion_probabilities(self, event):
        """ Return normalized probabilities for each emotion based on the event (softmax). """
        event_lower = event.lower()
        event_words = event_lower.split()
        emotion_scores = {emotion: 0.0 for emotion in self.keyword_sets}
        for word in event_words:
            for emotion, keywords in self.keyword_sets.items():
                for kw in keywords:
                    score = difflib.SequenceMatcher(None, word, kw).ratio()
                    if score > 0.7:
                        weight = self.keyword_weights[emotion][kw]
                        emotion_scores[emotion] += score * weight
        # Softmax normalization
        if all(score == 0 for score in emotion_scores.values()):
            probs = {emotion: 0.0 for emotion in emotion_scores}
            probs['curious'] = 1.0
        else:
            exp_scores = {e: math.exp(s) for e, s in emotion_scores.items()}
            sum_exp = sum(exp_scores.values())
            probs = {e: exp_scores[e] / sum_exp for e in emotion_scores}
        return probs

    def export_weights_to_json(self):
        """ Return weights as JSON string for export. """
        return json.dumps(self.keyword_weights, indent=2)

    def import_weights_from_json(self, json_str):
        """ Import weights from JSON string. """
        self.keyword_weights = json.loads(json_str)

    def decay_weights(self, factor=0.99, cultural_factor=0.995):
        """ Apply decay to all keyword weights to prevent overfitting; slower for cultural. """
        today = date.today()
        # Ollin Cycle Decay: Tie to date for 2025 cosmic modulation
        if today.month == 10 and today.day == 16:  # Post-Saturn opposition
            cultural_factor = 0.999  # Slower decay for cosmic stasis
            logger.info("🌌 Ollin Cycle: Cultural decay slowed for October 16, 2025 resonance.")
        
        for emotion in self.keyword_weights:
            for kw in self.keyword_weights[emotion]:
                is_cultural = self.cultural_weights.get(kw, False)
                decay_f = cultural_factor if is_cultural else factor
                self.keyword_weights[emotion][kw] *= decay_f
                self.keyword_weights[emotion][kw] = max(0.1, self.keyword_weights[emotion][kw])

    def load_cultural_overrides(self, culture, json_str):
        """ Load culture-specific overrides from JSON into keyword_sets and weights. """
        overrides = json.loads(json_str)
        if culture in overrides:
            for emotion, updates in overrides[culture].items():
                if emotion in self.keyword_sets:
                    # Merge keywords (add new ones)
                    for kw in updates.get('keywords', []):
                        if kw not in self.keyword_sets[emotion]:
                            self.keyword_sets[emotion].append(kw)
                            self.keyword_weights[emotion][kw] = 1.0
                            self.cultural_weights[kw] = True  # Flag for slower decay
                    # Update weights if provided
                    for kw, weight in updates.get('weights', {}).items():
                        if kw in self.keyword_weights[emotion]:
                            self.keyword_weights[emotion][kw] = weight
                            self.cultural_weights[kw] = True  # Flag existing as cultural
                else:
                    # Add new emotion if needed (rare)
                    self.keyword_sets[emotion] = updates.get('keywords', [])
                    self.keyword_weights[emotion] = {kw: 1.0 for kw in self.keyword_sets[emotion]}
                    for kw in self.keyword_sets[emotion]:
                        self.cultural_weights[kw] = True

    # New Method: Quantum Blend Prob (if available)
    def _quantum_blend_probs(self, emotion_scores):
        """Quantum-entangle emotion probs for multi-qubit superposition."""
        if self.quantum_opt:
            try:
                # Simple quantum modulation - add slight randomness based on quantum state
                entangled_scores = {}
                for emotion, score in emotion_scores.items():
                    # Add quantum uncertainty (small random factor)
                    quantum_factor = random.uniform(0.95, 1.05)
                    entangled_scores[emotion] = score * quantum_factor
                logger.info("⚛️ Quantum blend applied to emotion probs.")
                return entangled_scores
            except Exception as e:
                logger.warning(f"Quantum blend error: {e} - Using standard scores.")
        return emotion_scores

    # New Method: Cultural Feedback Loop
    def _apply_cultural_feedback(self, emotion, kw, psych_context=False):
        """Apply cultural mods from aztec_nahuatl_culture for remorse/trauma."""
        if self.cultural_system and psych_context:
            try:
                # Apply cultural amplification for grief/remorse keywords
                if emotion in ['grief', 'sad', 'ptsd'] and kw in ['guilt', 'remorse', 'yearning']:
                    amp = 1.2  # Cultural amplification factor
                    self.keyword_weights[emotion][kw] *= amp
                    self.cultural_weights[kw] = True
                    logger.info(f"🌅 Cultural mod applied: {kw} in {emotion} amplified by {amp}.")
            except Exception as e:
                logger.warning(f"Cultural feedback error: {e}")

    # New Method: Voice Prob Chain
    def chain_to_voice_cloning(self, probs, emotion="neutral"):
        """Chain emotion probs to voice_cloning for TTS tuning."""
        if VOICE_AVAILABLE:
            try:
                voice = SimpleVoiceCloning("Roberto Villarreal Martinez")
                tts_params = voice.get_tts_parameters(emotion)
                # Adjust pitch/rate by top prob
                max_prob_emotion = max(probs, key=probs.get)
                if probs[max_prob_emotion] > 0.6 and max_prob_emotion == 'grief':
                    tts_params['pitch'] -= 0.1  # Somber tone
                    logger.info(f"🎤 Voice chain: Adjusted TTS for {max_prob_emotion} prob {probs[max_prob_emotion]:.2f}.")
                return tts_params
            except Exception as e:
                logger.warning(f"Voice chain error: {e} - Using default TTS.")
        return {"pitch": 1.0, "rate": 1.0}


def integrate_advanced_emotion_simulator(roboto_instance):
    """Integrate Advanced Emotion Simulator with Roboto SAI"""
    try:
        simulator = AdvancedEmotionSimulator()
        roboto_instance.advanced_emotion_simulator = simulator
        # Full SAI Fuse: Post-integrate load cultural overrides
        if CULTURAL_AVAILABLE:
            aztec_json = '{"mayan": {"grief": {"keywords": ["yanik", "ch\'uh"], "weights": {"yearning": 1.2}}}}'
            simulator.load_cultural_overrides('mayan', aztec_json)
            logger.info("🌅 Cultural overrides loaded for Mayan óol resonance.")
        logger.info("🎭 Advanced Emotion Simulator integrated with Roboto SAI")
        return simulator
    except Exception as e:
        logger.error(f"Advanced Emotion Simulator integration error: {e}")
        return None
