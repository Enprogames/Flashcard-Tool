"""
Use the google text to speech library to read content. Provide an easy-to-use interface
so that the library could be changed in the future.
"""

from io import BytesIO

import pygame
from gtts import gTTS


class TextToSpeech:
    def __init__(self, language: str = 'en', slow: bool = False):
        self.language = language
        self.slow = slow

    def save(self, text, file_path: str):
        tts = gTTS(text=text, lang=self.language, slow=False)
        tts.save(file_path)

    def play(self, text):

        tts = gTTS(text=text, lang=self.language, slow=False)

        with BytesIO() as fp:
            fp.seek(0)
            tts.write_to_fp(fp)
            # play the audio
            fp.seek(0)
            pygame.mixer.init()
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Wait for audio to finish playing
                pygame.time.Clock().tick(10)  # You can adjust the tick rate as needed
