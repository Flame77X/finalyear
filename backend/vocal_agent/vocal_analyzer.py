import numpy as np
import librosa
import soundfile as sf
import io
import logging

logger = logging.getLogger(__name__)

class VocalAnalyzer:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate

    def analyze_audio(self, audio_data) -> dict:
        """
        Analyze audio chunk for vocal confidence metrics.
        Args:
            audio_data: Can be raw bytes (file content) OR numpy array (PCM data).
        Returns: Pitch, Loudness, Confidence Score (0-100)
        """
        try:
            y = None
            sr = self.sample_rate

            # Handle different inputs
            if isinstance(audio_data, np.ndarray):
                y = audio_data
                # Assume input is already at correct sample rate if passed as array from server
                # or we could require sr to be passed, but server uses 16000 uniformly.
            elif isinstance(audio_data, bytes):
                # Load from bytes (legacy behavior / fallback)
                y, file_sr = sf.read(io.BytesIO(audio_data))
                if file_sr != self.sample_rate:
                    y = librosa.resample(y, orig_sr=file_sr, target_sr=self.sample_rate)
            else:
                return self._empty_response()

            if y is None or len(y) == 0:
                return self._empty_response()
            
            # Ensure float32
            if y.dtype != np.float32:
                y = y.astype(np.float32)

            # 1. Loudness in dB (RMS)
            rms = np.sqrt(np.mean(y**2))
            loudness_db = 20 * np.log10(rms) if rms > 1e-9 else -80.0

            
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
                'pitch_hz': float(round(pitch_hz, 1)),
                'loudness_db': float(round(loudness_db, 1)),
                'loudness_stability': float(round(loudness_stability, 2)),
                'speech_rate': float(round(words_per_minute, 0)),
                'confidence_score': float(round(confidence_raw, 1)),
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
