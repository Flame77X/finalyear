import pygame
import io
import time

class AudioPlayer:
    def __init__(self, sample_rate=22050):
        # Initialize mixer with specific sample rate to match Piper (usually 22050)
        # 16-bit (-16), 1 channel (mono) is standard for Piper voices
        # Buffer size of 1024 to reduce latency
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=1, buffer=1024)
            pygame.mixer.init()

    def play_audio(self, audio_data, volume=0.3):
        """
        Plays audio from a bytes object (WAV format expected).
        volume: Float from 0.0 to 1.0
        """
        try:
            # Create a file-like object from the bytes
            sound_file = io.BytesIO(audio_data)
            
            # Load the sound
            sound = pygame.mixer.Sound(sound_file)
            
            # Set volume (safety first!)
            sound.set_volume(volume)
            
            # Play the sound
            channel = sound.play()
            
            while channel.get_busy():
                pygame.time.wait(50)
                
        except Exception as e:
            print(f"Error playing audio: {e}")

    def stop(self):
        pygame.mixer.stop()
