import os
import wave
import json
from flask import Flask, request
from flask_restx import Api, Resource, reqparse

from vosk import Model, KaldiRecognizer

app = Flask(__name__)
api = Api(app, version='1.0', title='Speech to Text API', description='Converts speech to text using Vosk')
ns = api.namespace('speech_to_text', description='Speech to Text operations')

# Initialize Vosk model
model_path = '/path/to/vosk-model'  # Replace with the path to your Vosk model
model = Model(model_path)

# Define a parser for the audio file
parser = reqparse.RequestParser()
parser.add_argument('audio_file', location='files', required=True, help='WAV audio file to be recognized')

@ns.route('/recognize')
class SpeechToText(Resource):
    @api.doc('Recognize speech in an audio file')
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        audio_file = args['audio_file']

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
