import subprocess
import os
import io
import tempfile
import uuid

class PiperTTSEngine:
    def __init__(self, piper_path, model_path):
        self.piper_path = piper_path
        self.model_path = model_path
        
        if not os.path.exists(self.piper_path):
            raise FileNotFoundError(f"Piper executable not found at: {self.piper_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

    def synthesize(self, text):
        """
        Synthesizes text to audio bytes (WAV format).
        Uses a temporary file to ensure clean output.
        """
        # Create a temp file path
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        cmd = [
            self.piper_path,
            "--model", self.model_path,
            "--output_file", temp_path
        ]
        
        try:
            # Run Piper
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
            
            # Read the generated WAV file
            if os.path.exists(temp_path):
                import wave
                import numpy as np
                
                with wave.open(temp_path, "rb") as wf:
                    params = wf.getparams()
                    frames = wf.readframes(wf.getnframes())
                
                # Convert bytes to numpy array (Int16)
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Verify we have data
                if len(audio_data) == 0:
                    os.remove(temp_path)
                    return None
                    
                # Reduce volume (scale by 0.2)
                scaled_data = (audio_data * 0.2).astype(np.int16)
                
                # Write back to a clean bytes buffer
                output_buffer = io.BytesIO()
                with wave.open(output_buffer, "wb") as wf:
                    wf.setparams(params)
                    wf.writeframes(scaled_data.tobytes())
                
                # Cleanup
                os.remove(temp_path)
                return output_buffer.getvalue()
            else:
                print("Error: Temporary audio file was not created.")
                return None
            
        except Exception as e:
            print(f"Error executing Piper: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
