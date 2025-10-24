# Advanced voice processing with graceful fallbacks
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None

import numpy as np

# Optional advanced AI models - use fallbacks if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False
    BERTopic = None
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedVoiceProcessor:
    """
    Advanced voice processing system that adds conversation context preservation,
    emotion detection, topic modeling, and multi-session continuity to Roboto.
    """

    def __init__(self, user_name="Roberto Villarreal Martinez"):
        self.user_name = user_name
        if SPEECH_RECOGNITION_AVAILABLE and sr:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None

        # Initialize AI models with error handling
        self.emotion_classifier = None
        self.topic_model = None

        if TRANSFORMERS_AVAILABLE and pipeline:
            try:
                self.emotion_classifier = pipeline("audio-classification", 
                                                 model="superb/wav2vec2-base-superb-er")
                logger.info("Emotion classifier initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize emotion classifier: {e}")
                self.emotion_classifier = None
        else:
            logger.info("Transformers not available - using fallback emotion detection")

        if BERTOPIC_AVAILABLE and BERTopic:
            try:
                self.topic_model = BERTopic(language="english", calculate_probabilities=True)
                logger.info("Topic modeling initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize topic model: {e}")
                self.topic_model = None
        else:
            logger.info("BERTopic not available - using fallback topic extraction")

        # Storage paths
        self.context_storage_dir = "conversation_contexts"
        self.audio_samples_dir = "audio_samples"
        self.ensure_directories()

        # Conversation session tracking
        self.current_session_id = None
        self.session_data = []

    def ensure_directories(self):
        """Create necessary directories for storage."""
        for directory in [self.context_storage_dir, self.audio_samples_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")

    def transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio file to text with enhanced error handling."""
        if not SPEECH_RECOGNITION_AVAILABLE or not sr:
            return "Speech recognition not available - using fallback transcription simulation"

        try:
            # Convert to compatible format if pydub is available
            if PYDUB_AVAILABLE and AudioSegment:
                audio = AudioSegment.from_file(audio_file)
                temp_wav = "temp_transcription.wav"
                audio.export(temp_wav, format="wav")
                audio_file = temp_wav

            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)

                try:
                    # Try Google Speech Recognition first
                    text = self.recognizer.recognize_google(audio_data)
                    logger.info(f"Successfully transcribed audio: {text[:50]}...")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Google Speech Recognition could not understand audio")
                    return "Could not understand the audio content"
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {e}")
                    return f"Transcription service error: {e}"

        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            return f"Audio processing error: {e}"
        finally:
            # Clean up temporary file
            if PYDUB_AVAILABLE and os.path.exists("temp_transcription.wav"):
                os.remove("temp_transcription.wav")

    def detect_emotions(self, audio_file: str) -> List[Dict[str, Any]]:
        """Detect emotions in audio using transformer models or fallback analysis."""
        if not self.emotion_classifier:
            # Fallback emotion detection based on file name or basic analysis
            return self._fallback_emotion_detection(audio_file)

        if not LIBROSA_AVAILABLE or not librosa:
            logger.warning("Librosa not available - using fallback emotion detection")
            return self._fallback_emotion_detection(audio_file)

        try:
            # Load and resample audio for the model
            audio, sample_rate = librosa.load(audio_file, sr=16000)

            # Ensure audio is not too short
            if len(audio) < 1600:  # Less than 0.1 seconds
                logger.warning("Audio too short for emotion detection")
                return [{"label": "neutral", "score": 0.5}]

            emotions = self.emotion_classifier(audio)
            logger.info(f"Detected emotions: {emotions[:2]}")
            return emotions

        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return self._fallback_emotion_detection(audio_file)

    def _fallback_emotion_detection(self, audio_file: str) -> List[Dict[str, Any]]:
        """Simple fallback emotion detection based on basic audio analysis."""
        try:
            # Try to get basic audio info for emotion estimation
            if PYDUB_AVAILABLE and AudioSegment:
                audio = AudioSegment.from_file(audio_file)
                duration = len(audio) / 1000.0  # Convert to seconds

                # Simple heuristic based on duration and file characteristics
                if duration < 2:
                    emotion = "neutral"
                    score = 0.6
                elif duration > 10:
                    emotion = "thoughtful"
                    score = 0.7
                else:
                    emotion = "engaged"
                    score = 0.65

                return [{"label": emotion, "score": score, "method": "fallback_analysis"}]
            else:
                return [{"label": "neutral", "score": 0.5, "method": "default_fallback"}]

        except Exception as e:
            logger.error(f"Fallback emotion detection error: {e}")
            return [{"label": "neutral", "score": 0.5, "method": "error_fallback"}]

    def extract_topics(self, text: str) -> tuple:
        """Extract topics from transcribed text using BERTopic or fallback analysis."""
        if not text.strip():
            return {}, [], []

        if not self.topic_model:
            return self._fallback_topic_extraction(text)

        try:
            topics, probabilities = self.topic_model.fit_transform([text])
            topic_info = self.topic_model.get_topic_info()

            logger.info(f"Extracted {len(topic_info)} topics from text")
            return topic_info, topics, probabilities

        except Exception as e:
            logger.error(f"Topic extraction error: {e}")
            return self._fallback_topic_extraction(text)

    def _fallback_topic_extraction(self, text: str) -> tuple:
        """Simple fallback topic extraction using keyword analysis."""
        try:
            words = text.lower().split()
            word_freq = {}

            # Count word frequencies (excluding common words)
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'}

            for word in words:
                if len(word) > 3 and word not in common_words:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Get top keywords
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

            # Create simple topic structure
            topic_info = {
                "fallback_analysis": True,
                "top_keywords": [word for word, count in top_words],
                "keyword_frequencies": dict(top_words),
                "text_length": len(text),
                "word_count": len(words)
            }

            return topic_info, [0], [0.5]  # Simple fallback values

        except Exception as e:
            logger.error(f"Fallback topic extraction error: {e}")
            return {"error": "Topic extraction failed"}, [], []

    def process_voice_chat(self, audio_files: List[str], session_id: str = None) -> List[Dict[str, Any]]:
        """
        Process multiple audio files, extract comprehensive conversation context.
        This is the main enhancement that adds context preservation across sessions.
        """
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session_id = session_id
        results = []

        logger.info(f"Processing voice chat session {session_id} with {len(audio_files)} files")

        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                logger.warning(f"File {audio_file} not found, skipping")
                continue

            logger.info(f"Processing audio file {i+1}/{len(audio_files)}: {audio_file}")

            try:
                # Transcribe audio
                transcription = self.transcribe_audio(audio_file)

                # Detect emotions
                emotions = self.detect_emotions(audio_file)

                # Extract topics if transcription was successful
                if transcription and "error" not in transcription.lower():
                    topic_info, topics, probabilities = self.extract_topics(transcription)
                else:
                    topic_info, topics, probabilities = {}, [], []

                # Compile comprehensive results
                result = {
                    "session_id": session_id,
                    "file_index": i,
                    "file": audio_file,
                    "timestamp": datetime.now().isoformat(),
                    "transcription": transcription,
                    "emotions": emotions,
                    "dominant_emotion": emotions[0]["label"] if emotions else "neutral",
                    "emotion_confidence": emotions[0]["score"] if emotions else 0.5,
                    "topics": topic_info.to_dict() if hasattr(topic_info, 'to_dict') and topic_info is not None else (topic_info if topic_info is not None else {}),
                    "topic_probabilities": probabilities.tolist() if hasattr(probabilities, 'tolist') and probabilities is not None else (probabilities if probabilities is not None else []),
                    "processing_metadata": {
                        "audio_duration": self._get_audio_duration(audio_file),
                        "text_length": len(transcription) if transcription else 0,
                        "emotion_model_used": bool(self.emotion_classifier),
                        "topic_model_used": bool(self.topic_model)
                    }
                }
                results.append(result)

            except Exception as e:
                logger.error(f"Error processing {audio_file}: {e}")
                # Add error result to maintain sequence
                results.append({
                    "session_id": session_id,
                    "file_index": i,
                    "file": audio_file,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "transcription": f"Processing error: {e}",
                    "emotions": [{"label": "error", "score": 0.0}],
                    "topics": {}
                })

        # Save session context
        self.save_session_context(results, session_id)

        return results

    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio file duration in seconds."""
        try:
            if PYDUB_AVAILABLE and AudioSegment:
                audio = AudioSegment.from_file(audio_file)
                return len(audio) / 1000.0  # Convert milliseconds to seconds
            else:
                return 0.0
        except:
            return 0.0

    def save_session_context(self, results: List[Dict[str, Any]], session_id: str):
        """Save conversation context for session continuity."""
        try:
            output_file = os.path.join(self.context_storage_dir, f"{session_id}_context.json")

            # Create comprehensive session summary
            session_summary = {
                "session_id": session_id,
                "user_name": self.user_name,
                "created_at": datetime.now().isoformat(),
                "total_files": len(results),
                "successful_transcriptions": sum(1 for r in results if r.get("transcription") and "error" not in r.get("transcription", "").lower()),
                "dominant_emotions": self._analyze_session_emotions(results),
                "key_topics": self._analyze_session_topics(results),
                "conversation_flow": results,
                "session_metadata": {
                    "total_duration": sum(r.get("processing_metadata", {}).get("audio_duration", 0) for r in results),
                    "average_emotion_confidence": np.mean([r.get("emotion_confidence", 0) for r in results]),
                    "models_used": {
                        "emotion_detection": bool(self.emotion_classifier),
                        "topic_modeling": bool(self.topic_model),
                        "speech_recognition": True
                    }
                }
            }

            with open(output_file, "w") as f:
                json.dump(session_summary, f, indent=4)

            logger.info(f"Session context saved to {output_file}")

        except Exception as e:
            logger.error(f"Error saving session context: {e}")

    def _analyze_session_emotions(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze emotional patterns across the session."""
        emotions = [r.get("dominant_emotion", "neutral") for r in results if r.get("dominant_emotion")]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        return {
            "most_common": max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else ("neutral", 0),
            "emotion_distribution": emotion_counts,
            "emotional_trajectory": emotions
        }

    def _analyze_session_topics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze topical patterns across the session."""
        all_text = " ".join([r.get("transcription", "") for r in results if r.get("transcription")])

        if not all_text.strip() or not self.topic_model:
            return {"summary": "No topics extracted", "text_length": len(all_text)}

        try:
            topic_info, topics, probabilities = self.extract_topics(all_text)
            return {
                "session_topics": topic_info.to_dict() if hasattr(topic_info, 'to_dict') and topic_info is not None else (topic_info if topic_info is not None else {}),
                "topic_confidence": probabilities.tolist() if hasattr(probabilities, 'tolist') and probabilities is not None else (probabilities if probabilities is not None else []),
                "text_analyzed": len(all_text)
            }
        except:
            return {"summary": "Topic analysis failed", "text_length": len(all_text)}

    def load_context_for_new_session(self, session_id: Optional[str] = None, context_file: Optional[str] = None) -> Dict[str, Any]:
        """Load saved context for continuing conversation across sessions."""
        try:
            if context_file:
                file_path = context_file
            elif session_id:
                file_path = os.path.join(self.context_storage_dir, f"{session_id}_context.json")
            else:
                # Load most recent session
                context_files = [f for f in os.listdir(self.context_storage_dir) if f.endswith("_context.json")]
                if not context_files:
                    logger.warning("No context files found")
                    return {}

                latest_file = max(context_files, key=lambda f: os.path.getctime(os.path.join(self.context_storage_dir, f)))
                file_path = os.path.join(self.context_storage_dir, latest_file)

            with open(file_path, "r") as f:
                context = json.load(f)

            logger.info(f"Loaded context from {file_path}")
            return context

        except Exception as e:
            logger.error(f"Error loading context: {e}")
            return {}

    def generate_conversation_summary(self, context: Dict[str, Any]) -> str:
        """Generate a human-readable summary for AI continuation."""
        if not context:
            return "No previous conversation context available."

        try:
            session_id = context.get("session_id", "unknown")
            total_files = context.get("total_files", 0)
            emotions = context.get("dominant_emotions", {})
            topics = context.get("key_topics", {})

            summary_parts = [
                f"Previous conversation session: {session_id}",
                f"Total interactions: {total_files}",
            ]

            # Add emotional context
            if emotions.get("most_common"):
                emotion, count = emotions["most_common"]
                summary_parts.append(f"Dominant emotion: {emotion} ({count} instances)")

            # Add topical context
            if topics.get("session_topics"):
                summary_parts.append("Key topics discussed: available in detailed analysis")

            # Add conversation flow summary
            conversation_flow = context.get("conversation_flow", [])
            if conversation_flow:
                recent_transcriptions = [
                    item.get("transcription", "")[:100] + "..." 
                    for item in conversation_flow[-3:] 
                    if item.get("transcription") and "error" not in item.get("transcription", "").lower()
                ]
                if recent_transcriptions:
                    summary_parts.append("Recent conversation snippets:")
                    summary_parts.extend([f"- {snippet}" for snippet in recent_transcriptions])

            return "\n".join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Context available but summary generation failed: {e}"

    def integrate_with_roboto(self, audio_files: List[str]) -> Dict[str, Any]:
        """
        Main integration method for Roboto - processes voice chat and returns
        enhanced context for the AI conversation system.
        """
        logger.info("Integrating advanced voice processing with Roboto")

        # Process the voice chat
        session_context = self.process_voice_chat(audio_files)

        # Generate summary for AI system
        context_summary = {
            "session_context": session_context,
            "conversation_summary": self.generate_conversation_summary({
                "session_id": self.current_session_id,
                "conversation_flow": session_context,
                "dominant_emotions": self._analyze_session_emotions(session_context),
                "key_topics": self._analyze_session_topics(session_context)
            }),
            "roboto_integration": {
                "voice_profile_user": self.user_name,
                "context_preserved": True,
                "emotion_analysis_enabled": bool(self.emotion_classifier),
                "topic_modeling_enabled": bool(self.topic_model),
                "session_continuity": True
            }
        }

        return context_summary

# Example usage and testing function
def example_usage():
    """Example of how to use the AdvancedVoiceProcessor with Roboto."""
    processor = AdvancedVoiceProcessor("Roberto Villarreal Martinez")

    # Example audio files (would be actual recorded files)
    audio_files = ["voice_chat1.wav", "voice_chat2.wav"]

    # Check if example files exist, create dummy if needed for demo
    example_files = []
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            example_files.append(audio_file)

    if example_files:
        # Process audio files and get enhanced context
        roboto_context = processor.integrate_with_roboto(example_files)

        # Print summary for demonstration
        print("=" * 60)
        print("ROBOTO ADVANCED VOICE PROCESSING INTEGRATION")
        print("=" * 60)
        print(roboto_context["conversation_summary"])
        print("\nIntegration Status:")
        for key, value in roboto_context["roboto_integration"].items():
            print(f"  {key}: {value}")
    else:
        print("No audio files found for processing example")
        print("Advanced Voice Processor initialized and ready for integration")

if __name__ == "__main__":
    example_usage()