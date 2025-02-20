import whisper

class Transcriber:
    WHISPER_MODEL = "small.en"

    def __init__(self, input_filename: str):
        self.input_filename = input_filename
        self.model = whisper.load_model(Transcriber.WHISPER_MODEL)

    def transcribe(self):
        audio = whisper.load_audio(self.input_filename)
        result = self.model.transcribe(audio)
        return result["text"]