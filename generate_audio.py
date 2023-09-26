from flask import Flask, request, send_from_directory, send_file
from flask_restx import Api, Resource, reqparse
import pyaudio
import wave
from pydub import AudioSegment

app = Flask(__name__)
api = Api(app)

# Define a request parser to accept the 'seconds' field
parser = reqparse.RequestParser()
parser.add_argument('seconds', type=int, required=True, help='Number of seconds to record')

@api.route('/record')
class VoiceRecorder(Resource):
    @api.expect(parser)  # Expect the 'seconds' parameter in the request
    def post(self):
        args = parser.parse_args()
        seconds = args['seconds']

        frames = []
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        print(f"Recording for {seconds} seconds...")

        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wav_filename = "output.wav"
        mp3_filename = "output.mp3"

        wf = wave.open(wav_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        audio = AudioSegment.from_wav(wav_filename)
        audio.export(mp3_filename, format="mp3")

        # Return the MP3 file as a downloadable response
        return send_file(mp3_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
