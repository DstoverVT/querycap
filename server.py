import os
import pathlib
from flask import Flask, request
from werkzeug.utils import secure_filename
from datetime import datetime
from gtts import gTTS
import requests
import subprocess

IMAGE_FOLDER = "./images"
SOUND_FOLDER = "./sounds"

app = Flask(__name__)

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SOUND_FOLDER'] = SOUND_FOLDER
pathlib.Path(IMAGE_FOLDER).mkdir(parents=True, exist_ok=True)
pathlib.Path(SOUND_FOLDER).mkdir(parents=True, exist_ok=True)


@app.after_request
def after(response):
    print(response.status)
    print(response.headers)
    print(response.get_data())
    return response


def check_for_file(name):
    if name not in request.files:
        print(f"didn't find file {name}")
        return {
            "success": False,
            "message": f"'{name}' file not found in request.",
        }, 400


def check_for_form(name):
    if name not in request.form:
        print(f"didn't find form field {name}")
        return {
            "success": False,
            "message": f"'{name}' field not found in form.",
        }, 400
    

def generate_sound(answer):
    print("Saving audio...")
    tts = gTTS(answer)
    tts.save("answer.mp3")

    subprocess.call(["afplay", "answer.mp3"])
    

def send_image_sound(img_path, sound_path):
    '''Send image and sound file to AWS server through SSH tunnel.''' 
    # ssh -o "ServerAliveInterval 60" -L 5001:ec2-18-190-153-119.us-east-2.compute.amazonaws.com:5000
    files = {
            "image": open(img_path, "rb"),
            "sound": open(sound_path, "rb"),
    }
    URL = 'http://127.0.0.1:5001/send_image'
    response = requests.post(URL, files=files)
    response_json = response.json()

    SUCCESS = 200
    if response.status_code == SUCCESS:
        print("Data sent to model.")
        generate_sound(response_json['answer'])
    else:
        print(f"Error sending POST to {URL}")


@app.route("/send_image", methods=['POST'])
def send_image():
    check_for_file('image')
    check_for_file('sound')
    
    image = request.files['image']
    sound = request.files['sound']

    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    image_filename = now_str + secure_filename(image.filename)
    image_filepath = os.path.join(app.config['IMAGE_FOLDER'], image_filename)
    image.save(image_filepath)

    sound_filename = now_str + secure_filename(sound.filename)
    sound_filepath = os.path.join(app.config['SOUND_FOLDER'], sound_filename)
    sound.save(sound_filepath)

    send_image_sound(image_filepath, sound_filepath)

    return {
        "success": True,
    }, 200

