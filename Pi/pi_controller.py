import cv2
import time
import os
import pyaudio
import wave

class QueryCapPi:
    '''Controls RPi image and audio for QueryCap.'''

    def __init__(self, audio_path, image_path):
        self.cap_path = image_path
        self.query_path = audio_path

        # Video setup
        self.video = cv2.VideoCapture(0)
        self.use_video = True

        if(not self.video.isOpened()):
            self.use_video = False

        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.audio_chunk = 1024
        # 16 kHz
        self.audio_rate = 16000
        self.audio_format = pyaudio.paInt16

    
    def run(self):
        '''Captures and image and then records the user's question'''
        while(True):
            key = input()
            if(key == ''):
                self.image_capture()
                self.audio_capture(5)


    def image_capture(self):
        '''Capture frames from webcam.'''
        if(self.use_video):
            ret, frame = self.video.read()
            # Save 1 frame per second to path
            if(ret):
                print(f"saving image")
                cv2.imwrite(f"{self.cap_path}/cap.png", frame)
            else:
                print(f"frame invalid")


    def audio_capture(self, duration):
        '''Captures audio from microphone.'''
        self.audio_stream = self.audio.open(format=self.audio_format,
                            channels=1,
                            rate=self.audio_rate,
                            input=True,
                            frames_per_buffer=self.audio_chunk)
        recording = []
        begin = time.time()

        print("capturing audio...")
        while((time.time() - begin) < duration):
            # Start recording audio
            audio_frame = self.audio_stream.read(self.audio_chunk)
            recording.append(audio_frame)
        print("Done")

        # Save it to a .wav file
        filename = "query.wav"
        with wave.open(f'{self.query_path}/{filename}', 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(self.audio.get_sample_size(self.audio_format))
            wav.setframerate(self.audio_rate)
            wav.writeframes(b''.join(recording))

        
if __name__ == '__main__':
    image_path = "images"
    audio_path = "audio"

    if not os.path.exists(image_path):
        os.makedirs(image_path)
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    # image_capture(path, FPS=1)
    query_cap = QueryCapPi(audio_path, image_path)
    query_cap.run()