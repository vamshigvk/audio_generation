import os
import wave
import json
from flask import Flask, request
from flask_restx import Api, Resource

from vosk import Model, KaldiRecognizer

app = Flask(__name__)
api = Api(app, version='1.0', title='Speech to Text API', description='Converts speech to text using Vosk')
ns = api.namespace('speech_to_text', description='Speech to Text operations')

# Initialize Vosk model
model_path = '/path/to/vosk-model'  # Replace with the path to your Vosk model
model = Model(model_path)

@ns.route('/recognize')
class SpeechToText(Resource):
    @api.doc('Recognize speech in an audio file')
    @api.expect(parser)
    def post(self):
        audio_file = request.files.get('audio_file')

        if not audio_file:
            return {'message': 'Audio file not provided'}, 400

        if not audio_file.filename.endswith('.wav'):
            return {'message': 'Invalid file format, only WAV files are supported'}, 400

        recognizer = KaldiRecognizer(model, 16000)
        text = ""

        with wave.open(audio_file, 'rb') as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
                return {'message': 'Audio file must be WAV format mono PCM'}, 400

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text += result['text']

            result = json.loads(recognizer.FinalResult())
            text += result['text']

        return {'recognized_text': text}

if __name__ == '__main__':
    app.run(debug=True)
