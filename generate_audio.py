from flask import Flask, request, send_file
from flask_restx import Api, Resource, reqparse
import pyaudio
import os
import tempfile
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

        mp3_filename = "output.mp3"

        # Create a temporary directory to store the MP3 file
        tmp_dir = tempfile.mkdtemp()
        mp3_filename = os.path.join(tmp_dir, mp3_filename)

        audio = AudioSegment(
            data=b''.join(frames),
            sample_width=sample_format // 8,
            frame_rate=fs,
            channels=channels
        )

        # Export the audio as an MP3 file
        audio.export(mp3_filename, format="mp3")

        # Check if the MP3 file exists before sending it
        if os.path.isfile(mp3_filename):
            # Return the MP3 file as a downloadable response
            return send_file(mp3_filename, as_attachment=True)
        else:
            return {'message': 'MP3 file not found'}, 404

if __name__ == '__main__':
    app.run(debug=True)
