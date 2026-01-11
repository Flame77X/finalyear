import numpy as np
import librosa
import soundfile as sf
import io
import logging

logger = logging.getLogger(__name__)

class VocalAnalyzer:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate

    def analyze_audio(self, audio_bytes: bytes) -> dict:
        """
        Analyze audio chunk for vocal confidence metrics.
        Returns: Pitch, Loudness, Confidence Score (0-100)
        """
        try:
            # Load audio
            y, sr = sf.read(io.BytesIO(audio_bytes))
            if len(y) == 0:
                return self._empty_response()
                
            # Resample if needed
            if sr != self.sample_rate:
                y = librosa.resample(y, orig_sr=sr, target_sr=self.sample_rate)

            # 1. Loudness in dB (RMS)
            rms = np.sqrt(np.mean(y**2))
            loudness_db = 20 * np.log10(rms) if rms > 0 else -80.0
            
            # Stability (Standard Deviation of Amplitude)
            loudness_stability = 1.0 - min(1.0, np.std(y) * 5) # Heuristic

            # 2. Pitch (Zero Crossing Rate as proxy for simple realtime, or PyIN)
            # Using Zero Crossing Rate for speed, PyIN is slow for chunks
            zcr = librosa.feature.zero_crossing_rate(y)
            avg_zcr = np.mean(zcr)
            # Estimate Pitch Hz roughly from ZCR (very rough)
            pitch_hz = avg_zcr * self.sample_rate / 2 

            # 3. Speech Rate (approx via Onset detection)
            onsets = librosa.onset.onset_detect(y=y, sr=self.sample_rate)
            words_per_minute = (len(onsets) / (len(y)/self.sample_rate)) * 60
            
            # 4. Confidence Score Calculation
            # Ideal Loudness: -20 to -10 dB
            vol_score = 1.0 if -25 <= loudness_db <= -5 else 0.6
            
            # Ideal Pitch: Human voice 85-255 Hz. 
            # ZCR is a poor proxy but usable for "is speaking".
            pitch_score = 1.0 if pitch_hz > 50 else 0.5 
            
            # Ideal Rate: 100-160 wpm.
            rate_score = 1.0 if 100 <= words_per_minute <= 180 else 0.7

            confidence_raw = (vol_score * 0.4 + pitch_score * 0.3 + rate_score * 0.3) * 100
            
            return {
                'pitch_hz': round(pitch_hz, 1),
                'loudness_db': round(loudness_db, 1),
                'loudness_stability': round(loudness_stability, 2),
                'speech_rate': round(words_per_minute, 0),
                'confidence_score': round(confidence_raw, 1),
                'success': True
            }

        except Exception as e:
            logger.error(f"Vocal analysis error: {e}")
            return self._empty_response()

    def _empty_response(self):
        return {
            'pitch_hz': 0.0,
            'loudness_db': -80.0,
            'loudness_stability': 0.0,
            'speech_rate': 0.0,
            'confidence_score': 50.0, # Neutral fallback
            'success': False
        }

if __name__ == "__main__":
    v = VocalAnalyzer()
    print("Vocal Analyzer Initialized.")
