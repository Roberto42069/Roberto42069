"""
Voice Cloning System for Roberto Villarreal Martinez
Creates personalized voice synthesis using recorded audio samples
"""

import os
import json
import numpy as np
import wave
import subprocess
import shlex
from datetime import datetime
import logging
from collections import defaultdict
import re

class VoiceCloningEngine:
    def __init__(self, user_name="Roberto Villarreal Martinez"):
        self.user_name = user_name
        self.voice_profile_file = f"roberto_voice_profile.json"
        self.audio_samples_dir = "."
        self.voice_characteristics = {}
        self.phoneme_patterns = defaultdict(list)
        self.prosody_features = {}
        self.voice_model_data = {}
        
        # Initialize voice analysis
        self.load_voice_profile()
        self.analyze_existing_samples()
    
    def find_audio_samples(self):
        """Find all audio samples for voice analysis"""
        audio_files = []
        
        # Find WebM audio files
        for file in os.listdir(self.audio_samples_dir):
            if file.startswith("temp_audio_") and file.endswith(".webm"):
                audio_files.append(os.path.join(self.audio_samples_dir, file))
        
        return sorted(audio_files)
    
    def analyze_existing_samples(self):
        """Analyze existing audio samples to build voice profile"""
        audio_files = self.find_audio_samples()
        
        if not audio_files:
            logging.info("No audio samples found for voice analysis")
            return
        
        logging.info(f"Analyzing {len(audio_files)} audio samples for voice cloning")
        
        for audio_file in audio_files:
            try:
                # Convert WebM to WAV for analysis
                wav_file = self.convert_to_wav(audio_file)
                if wav_file:
                    self.extract_voice_features(wav_file)
                    # Clean up temporary WAV file
                    if os.path.exists(wav_file):
                        os.remove(wav_file)
            except Exception as e:
                logging.error(f"Error analyzing {audio_file}: {e}")
        
        self.build_voice_model()
        self.save_voice_profile()
    
    def convert_to_wav(self, webm_file):
        """Convert WebM audio to WAV format for analysis"""
        try:
            # Validate input file path for security
            if not os.path.basename(webm_file).startswith("temp_audio_") or not webm_file.endswith(".webm"):
                logging.error(f"Invalid audio file format: {webm_file}")
                return None
            
            # Sanitize file paths to prevent command injection
            webm_file = os.path.normpath(webm_file)
            if os.path.isabs(webm_file) or '..' in webm_file:
                logging.error(f"Invalid file path detected: {webm_file}")
                return None
            
            wav_file = webm_file.replace('.webm', '_converted.wav')
            wav_file = os.path.normpath(wav_file)
            
            # Use ffmpeg to convert WebM to WAV
            cmd = [
                'ffmpeg', '-i', shlex.quote(webm_file), 
                '-ac', '1',  # Mono
                '-ar', '22050',  # Sample rate
                '-y',  # Overwrite output
                shlex.quote(wav_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(wav_file):
                return wav_file
            else:
                logging.error(f"FFmpeg conversion failed: {result.stderr}")
                return None
                
        except Exception as e:
            logging.error(f"Error converting {webm_file}: {e}")
            return None
    
    def extract_voice_features(self, wav_file):
        """Extract voice characteristics from WAV file"""
        try:
            with wave.open(wav_file, 'rb') as wav:
                frames = wav.readframes(-1)
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                
                # Convert to numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Basic voice feature extraction
                features = self.analyze_audio_features(audio_data, sample_rate)
                
                # Store features for voice model
                timestamp = os.path.basename(wav_file).split('_')[2].split('.')[0]
                self.voice_characteristics[timestamp] = features
                
        except Exception as e:
            logging.error(f"Error extracting features from {wav_file}: {e}")
    
    def analyze_audio_features(self, audio_data, sample_rate):
        """Analyze basic audio features for voice characteristics"""
        features = {}
        
        # Fundamental frequency (pitch) analysis
        features['pitch_mean'] = self.estimate_pitch(audio_data, sample_rate)
        features['pitch_variance'] = np.var(audio_data.astype(float))
        
        # Speech rate analysis
        features['speech_rate'] = self.estimate_speech_rate(audio_data, sample_rate)
        
        # Energy and volume characteristics
        features['energy_mean'] = np.mean(np.abs(audio_data))
        features['energy_variance'] = np.var(np.abs(audio_data))
        
        # Spectral characteristics
        features['spectral_centroid'] = self.calculate_spectral_centroid(audio_data)
        
        # Voice quality indicators
        features['voice_stability'] = self.measure_voice_stability(audio_data)
        
        return features
    
    def estimate_pitch(self, audio_data, sample_rate):
        """Estimate fundamental frequency (pitch)"""
        try:
            # Simple autocorrelation-based pitch estimation
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peak in autocorrelation
            if len(autocorr) > 100:
                peak_idx = np.argmax(autocorr[50:]) + 50
                if peak_idx > 0:
                    return sample_rate / peak_idx
            
            return 150.0  # Default male voice fundamental frequency
        except:
            return 150.0
    
    def estimate_speech_rate(self, audio_data, sample_rate):
        """Estimate speech rate (syllables per second)"""
        try:
            # Simple energy-based speech rate estimation
            frame_size = int(sample_rate * 0.02)  # 20ms frames
            frames = [audio_data[i:i+frame_size] for i in range(0, len(audio_data), frame_size)]
            
            energy_frames = [np.mean(np.abs(frame)) for frame in frames if len(frame) == frame_size]
            
            if energy_frames:
                threshold = np.mean(energy_frames) * 0.3
                speech_frames = sum(1 for energy in energy_frames if energy > threshold)
                duration = len(energy_frames) * 0.02
                return speech_frames / duration if duration > 0 else 0
            
            return 5.0  # Default speech rate
        except:
            return 5.0
    
    def calculate_spectral_centroid(self, audio_data):
        """Calculate spectral centroid for voice timbre analysis"""
        try:
            # Simple spectral centroid calculation
            fft = np.fft.fft(audio_data)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(fft))
            
            if np.sum(magnitude) > 0:
                centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
                return abs(centroid)
            
            return 0.1
        except:
            return 0.1
    
    def measure_voice_stability(self, audio_data):
        """Measure voice stability and consistency"""
        try:
            # Simple stability measure based on energy variance
            frame_size = len(audio_data) // 10
            frames = [audio_data[i:i+frame_size] for i in range(0, len(audio_data), frame_size)]
            
            energies = [np.mean(np.abs(frame)) for frame in frames if len(frame) == frame_size]
            
            if len(energies) > 1:
                return 1.0 / (1.0 + np.var(energies))
            
            return 0.8
        except:
            return 0.8
    
    def build_voice_model(self):
        """Build comprehensive voice model from analyzed features"""
        if not self.voice_characteristics:
            logging.warning("No voice characteristics available for model building")
            return
        
        features_list = list(self.voice_characteristics.values())
        
        # Calculate average voice characteristics
        self.voice_model_data = {
            'user_name': self.user_name,
            'sample_count': len(features_list),
            'voice_profile': {
                'pitch_mean': np.mean([f['pitch_mean'] for f in features_list]),
                'pitch_variance': np.mean([f['pitch_variance'] for f in features_list]),
                'speech_rate': np.mean([f['speech_rate'] for f in features_list]),
                'energy_mean': np.mean([f['energy_mean'] for f in features_list]),
                'energy_variance': np.mean([f['energy_variance'] for f in features_list]),
                'spectral_centroid': np.mean([f['spectral_centroid'] for f in features_list]),
                'voice_stability': np.mean([f['voice_stability'] for f in features_list])
            },
            'voice_characteristics': {
                'fundamental_frequency': np.mean([f['pitch_mean'] for f in features_list]),
                'speaking_rate': np.mean([f['speech_rate'] for f in features_list]),
                'voice_timbre': np.mean([f['spectral_centroid'] for f in features_list]),
                'pronunciation_style': 'Hispanic-English bilingual',
                'accent_type': 'Spanish-influenced English',
                'voice_quality': 'Natural, conversational'
            },
            'synthesis_parameters': self.generate_synthesis_parameters(),
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        logging.info(f"Voice model built with {len(features_list)} samples")
        logging.info(f"Average pitch: {self.voice_model_data['voice_profile']['pitch_mean']:.2f} Hz")
        logging.info(f"Speaking rate: {self.voice_model_data['voice_profile']['speech_rate']:.2f} syllables/sec")
    
    def generate_synthesis_parameters(self):
        """Generate TTS synthesis parameters based on voice analysis"""
        if not self.voice_characteristics:
            return self.get_default_synthesis_parameters()
        
        features_list = list(self.voice_characteristics.values())
        avg_pitch = np.mean([f['pitch_mean'] for f in features_list])
        avg_rate = np.mean([f['speech_rate'] for f in features_list])
        
        # Map analyzed features to TTS parameters
        pitch_adjustment = max(0.5, min(2.0, avg_pitch / 150.0))  # Normalize around 150Hz
        rate_adjustment = max(0.5, min(2.0, avg_rate / 5.0))  # Normalize around 5 syllables/sec
        
        return {
            'pitch': pitch_adjustment,
            'rate': rate_adjustment,
            'volume': 0.8,
            'voice_type': 'male' if avg_pitch < 180 else 'female',
            'language': 'en-US',
            'accent': 'Hispanic-English',
            'speaking_style': 'conversational',
            'emotion_baseline': 'neutral_friendly'
        }
    
    def get_default_synthesis_parameters(self):
        """Default synthesis parameters for Roberto"""
        return {
            'pitch': 0.9,  # Slightly lower pitch for male voice
            'rate': 1.0,   # Normal speaking rate
            'volume': 0.8,
            'voice_type': 'male',
            'language': 'en-US',
            'accent': 'Hispanic-English',
            'speaking_style': 'conversational',
            'emotion_baseline': 'neutral_friendly'
        }
    
    def generate_roboto_voice_config(self):
        """Generate voice configuration for Roboto TTS"""
        if not self.voice_model_data:
            return self.get_default_synthesis_parameters()
        
        return {
            'tts_config': {
                'voice_settings': self.voice_model_data['synthesis_parameters'],
                'personalization': {
                    'user_name': self.user_name,
                    'voice_profile_strength': len(self.voice_characteristics) / 20.0,  # Max 1.0
                    'adaptation_level': 'high',
                    'accent_preservation': True
                },
                'quality_settings': {
                    'sample_rate': 22050,
                    'bit_depth': 16,
                    'channels': 1,
                    'format': 'wav'
                }
            },
            'voice_characteristics': self.voice_model_data['voice_characteristics'],
            'last_training': self.voice_model_data['last_updated']
        }
    
    def save_voice_profile(self):
        """Save voice profile to file"""
        try:
            with open(self.voice_profile_file, 'w') as f:
                json.dump(self.voice_model_data, f, indent=2)
            logging.info(f"Voice profile saved to {self.voice_profile_file}")
        except Exception as e:
            logging.error(f"Error saving voice profile: {e}")
    
    def load_voice_profile(self):
        """Load existing voice profile"""
        try:
            if os.path.exists(self.voice_profile_file):
                with open(self.voice_profile_file, 'r') as f:
                    self.voice_model_data = json.load(f)
                logging.info("Existing voice profile loaded")
            else:
                logging.info("No existing voice profile found, will create new one")
        except Exception as e:
            logging.error(f"Error loading voice profile: {e}")
    
    def get_voice_insights(self):
        """Get comprehensive voice analysis insights"""
        if not self.voice_model_data:
            return "Voice profile not yet created. Recording more audio samples..."
        
        profile = self.voice_model_data['voice_profile']
        characteristics = self.voice_model_data['voice_characteristics']
        
        insights = []
        
        # Voice quality assessment
        if self.voice_model_data['sample_count'] > 5:
            insights.append(f"Voice profile built from {self.voice_model_data['sample_count']} audio samples")
        else:
            insights.append("Building voice profile - need more audio samples")
        
        # Pitch characteristics
        pitch = characteristics['fundamental_frequency']
        if pitch < 150:
            insights.append("Deep, resonant voice characteristics detected")
        elif pitch < 200:
            insights.append("Standard male voice range with clear articulation")
        else:
            insights.append("Higher pitch range with expressive qualities")
        
        # Speaking style
        rate = characteristics['speaking_rate']
        if rate > 6:
            insights.append("Fast, energetic speaking pattern")
        elif rate > 4:
            insights.append("Natural, conversational speaking pace")
        else:
            insights.append("Deliberate, thoughtful speaking style")
        
        # Accent and pronunciation
        insights.append("Spanish-English bilingual pronunciation patterns integrated")
        
        return " • ".join(insights)
    
    def apply_voice_to_tts(self, text, utterance_obj):
        """Apply voice cloning parameters to TTS utterance"""
        try:
            if not self.voice_model_data:
                return utterance_obj
            
            params = self.voice_model_data['synthesis_parameters']
            
            # Apply voice characteristics
            utterance_obj.pitch = params.get('pitch', 1.0)
            utterance_obj.rate = params.get('rate', 1.0)
            utterance_obj.volume = params.get('volume', 0.8)
            
            logging.info(f"Applied voice cloning: pitch={params.get('pitch')}, rate={params.get('rate')}")
            
            return utterance_obj
            
        except Exception as e:
            logging.error(f"Error applying voice cloning: {e}")
            return utterance_obj

def initialize_voice_cloning():
    """Initialize voice cloning system for Roberto"""
    try:
        cloning_engine = VoiceCloningEngine("Roberto Villarreal Martinez")
        return cloning_engine
    except Exception as e:
        logging.error(f"Error initializing voice cloning: {e}")
        return None

if __name__ == "__main__":
    # Test voice cloning system
    logging.basicConfig(level=logging.INFO)
    
    cloning_engine = initialize_voice_cloning()
    if cloning_engine:
        insights = cloning_engine.get_voice_insights()
        print("Voice Cloning Insights:", insights)
        
        config = cloning_engine.generate_roboto_voice_config()
        print("Voice Configuration:", json.dumps(config, indent=2))