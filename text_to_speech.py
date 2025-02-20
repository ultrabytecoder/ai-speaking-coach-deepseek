from gtts import gTTS

class TextToSpeech:
    """
    A class to converts text to speech
    """

    def __init__(self, output_filename: str):
        self.output_filename = output_filename

    def save(self, text: str):
        try:
            tts = gTTS(text=text)
            tts.save(self.output_filename)
        except Exception as e:
            print(f"An error occurred: {e}")
