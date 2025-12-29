import pyttsx3
import logging

class VoiceFeedback:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Set properties if needed
            self.engine.setProperty('rate', 150)
            logging.info("Voice Feedback Initialized")
        except Exception as e:
            logging.warning(f"Voice Feedback could not be initialized: {e}")
            self.engine = None

    def speak(self, text):
        """Audible feedback for the user"""
        print(f"🔊 [VOICE] {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
