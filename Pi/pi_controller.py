import cv2
import os
import pyaudio
import wave
import requests
import threading


class QueryCapPi:
    """Controls RPi image and audio for QueryCap."""

    user_input = None

    def __init__(self, audio_path, image_path, server_url):
        self.cap_path = image_path
        self.query_path = audio_path
        self.server = server_url

        # Video setup
        self.video = cv2.VideoCapture(-1)
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.use_video = True

        if not self.video.isOpened():
            print("Error opening webcam: not using video")
            self.use_video = False

        # Audio setup
        self.audio = pyaudio.PyAudio()

    def run(self):
        """Captures and image and then records the user's question"""
        print("Press Enter to start")
        while True:
            key = input()
            # Start image and audio capture on "enter" key press
            if key is not None:
                self.image_capture()
                # audio_capture waits for another "enter" press before done
                self.audio_capture()
                # self.post_request()

    def post_request(self):
        """Sends image and audio files to server"""
        files = {
            "image": open(f"{self.cap_path}/cap.png", "rb"),
            "sound": open(f"{self.query_path}/query.wav", "rb"),
        }
        response = requests.post(self.server, files=files)

        SUCCESS = 200
        if response.status_code == SUCCESS:
            print("Data sent to server.")
        else:
            print(f"Error sending POST to {self.server}")

    def image_capture(self):
        """Capture frames from webcam."""
        if self.use_video:
            # Need to call read once to flush buffer
            self.video.read()
            ret, frame = self.video.read()
            
            if ret:
                print(f"saving image")
                cv2.imwrite(f"{self.cap_path}/cap.png", frame)
            else:
                print(f"frame invalid")

    def audio_capture(self):
        """Captures audio from microphone."""
        audio_chunk = 1024
        # 16 kHz
        audio_rate = 16000
        audio_format = pyaudio.paInt16

        audio_stream = self.audio.open(
            format=audio_format,
            channels=1,
            rate=audio_rate,
            input=True,
            frames_per_buffer=audio_chunk,
        )
        # Stores audio from audio stream
        recording = []

        # Read console input in separate thread to determine when to stop recording
        input_thread = threading.Thread(target=self.get_input)
        input_thread.start()

        print("capturing audio...")
        while True:
            # Start recording audio
            audio_frame = audio_stream.read(audio_chunk)
            recording.append(audio_frame)

            # Stop recording audio on "enter" key press
            if self.user_input is not None:
                self.user_input = None
                break
        print("Done")

        audio_stream.stop_stream()
        audio_stream.close()

        # Save it to a .wav file
        filename = "query.wav"
        with wave.open(f"{self.query_path}/{filename}", "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(self.audio.get_sample_size(audio_format))
            wav.setframerate(audio_rate)
            wav.writeframes(b"".join(recording))

    def get_input(self):
        """Get keyboard input, runs in separate thread so non-blocking."""
        self.user_input = input()


if __name__ == "__main__":
    image_path = "images"
    audio_path = "audio"
    URL = "http://172.29.103.161:5000/send_image"

    if not os.path.exists(image_path):
        os.makedirs(image_path)
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    query_cap = QueryCapPi(audio_path, image_path, URL)
    query_cap.run()
    # query_cap.post_request()
