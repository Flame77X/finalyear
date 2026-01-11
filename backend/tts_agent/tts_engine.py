import os
import io
import wave
import uuid
import subprocess
import numpy as np

class TTSEngine:
    def __init__(self, piper_path=None, model_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Default paths if not provided
        if not piper_path:
            self.piper_path = os.path.join(base_dir, "piper", "piper.exe")
        else:
            self.piper_path = piper_path
            
        if not model_path:
            self.model_path = os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")
        else:
            self.model_path = model_path

        if not os.path.exists(self.piper_path):
            raise FileNotFoundError(f"Piper executable not found at: {self.piper_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

    def speak(self, text: str) -> str:
        """
        Converts text to audio using Piper TTS.
        Returns the absolute path to the generated WAV file.
        """
        output_filename = f"speech_{uuid.uuid4()}.wav"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp_audio", output_filename)
        # Ensure temp_audio directory exists in project root
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # We need a truly temporary file for the raw output before we scale it
        raw_temp = output_path.replace(".wav", "_raw.wav")

        cmd = [
            self.piper_path,
            "--model", self.model_path,
            "--output_file", raw_temp
        ]
        
        try:
            # Run Piper (input text via stdin)
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            input_data = text.encode('utf-8')
            stdout_data, stderr_data = process.communicate(input=input_data)
            
            if process.returncode != 0:
                print(f"Piper Error: {stderr_data.decode('utf-8', errors='ignore')}")
                return None
            
            if os.path.exists(raw_temp):
                # Apply Volume scaling (User volume fix)
                self._scale_volume(raw_temp, output_path, factor=0.2)
                
                # Cleanup raw file
                if os.path.exists(raw_temp):
                    os.remove(raw_temp)
                    
                return os.path.abspath(output_path)
            else:
                return None

        except Exception as e:
            print(f"Error in TTS speak: {e}")
            return None

    def _scale_volume(self, input_path, output_path, factor=0.2):
        try:
            with wave.open(input_path, "rb") as wf:
                params = wf.getparams()
                frames = wf.readframes(wf.getnframes())
            
            # Convert to numpy and scale
            audio_data = np.frombuffer(frames, dtype=np.int16)
            scaled_data = (audio_data * factor).astype(np.int16)
            
            with wave.open(output_path, "wb") as wf:
                wf.setparams(params)
                wf.writeframes(scaled_data.tobytes())
                
        except Exception as e:
            print(f"Error scaling volume: {e}")
            # Fallback: just move the file if scaling fails
            if os.path.exists(input_path):
                os.rename(input_path, output_path)
