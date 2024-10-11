from transformers import pipeline
import io
import ffmpeg

class SpeechToText:
    def __init__(self):
        self.speechRecogniser = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

    def convertAudioToText(self, audio):
        audio.seek(0) # This moves the cursor to the beginning of the audio file
        audioData = audio.read() #This reads the audio file
        textResult = self.speechRecogniser(audioData)
        return textResult