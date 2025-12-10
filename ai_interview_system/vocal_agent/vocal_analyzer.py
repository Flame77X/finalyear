import librosa
import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

class VocalAnalyzer:
    def __init__(self):
        self.target_sr = 16000

    def analyze(self, audio_path: str) -> dict:
        """
        Analyzes audio for paralinguistic features: Pitch, Energy, Pace.
        Returns a dictionary with metrics and a confidence score.
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.target_sr)
            
            if len(y) == 0:
                return self._get_empty_metrics()

            # 1. Pitch (F0)
            # piptrack returns (magnitudes, frequencies)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            # Select dominant pitch
            pitch_indices = magnitudes > np.median(magnitudes)
            selected_pitches = pitches[pitch_indices]
            avg_pitch = np.mean(selected_pitches) if len(selected_pitches) > 0 else 0
            
            # 2. Energy (RMS)
            rms = librosa.feature.rms(y=y)
            avg_energy = np.mean(rms)

            # 3. Pace (Tempo)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
            avg_tempo = tempo[0] if len(tempo) > 0 else 0

            # 4. Confidence Score Logic (0-100)
            # Heuristic: 
            # - Stable pitch (not too high, not too low)
            # - Good energy (not whispering)
            # - Steady tempo (not rushing)
            
            score = 50.0 # Start neutral
            
            # Volume Boost
            if avg_energy > 0.02: score += 10
            if avg_energy > 0.05: score += 10
            
            # Tempo Penalty (Too fast or too slow)
            if 100 < avg_tempo < 160: score += 10 # Ideal conversational pace
            
            # Pitch Presence
            if avg_pitch > 50: score += 10
            
            # Cap at 100
            score = min(100.0, score)

            results = {
                "avg_pitch": float(avg_pitch),
                "avg_energy": float(avg_energy),
                "speech_rate": float(avg_tempo),
                "confidence_score": float(score)
            }
            
            # Explicitly print to terminal for user visibility
            print(f"\n[VOCAL ANALYSIS] 🎤 Pitch: {avg_pitch:.1f}Hz | Tempo: {avg_tempo:.1f}BPM | Energy: {avg_energy:.3f}")
            print(f"[VOCAL ANALYSIS] ⭐ Confidence Score: {score:.1f}%\n")
            
            logger.info(f"Vocal Analysis: {results}")
            return results

        except Exception as e:
            logger.error(f"Vocal Analysis failed: {e}")
            print("\n[VOCAL ERROR DEBUG]")
            traceback.print_exc()
            print("-------------------\n")
            return self._get_empty_metrics()

    def _get_empty_metrics(self):
        return {
            "avg_pitch": 0.0,
            "avg_energy": 0.0,
            "speech_rate": 0.0,
            "confidence_score": 0.0
        }
