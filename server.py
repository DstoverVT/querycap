import os
import pathlib
from flask import Flask, request
from werkzeug.utils import secure_filename
from transformers import BlipProcessor, BlipForQuestionAnswering
from PIL import Image
import whisper
from datetime import datetime
from gtts import gTTS
import vlc

IMAGE_FOLDER = "./images"
SOUND_FOLDER = "./sounds"

app = Flask(__name__)

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SOUND_FOLDER'] = SOUND_FOLDER
pathlib.Path(IMAGE_FOLDER).mkdir(parents=True, exist_ok=True)
pathlib.Path(SOUND_FOLDER).mkdir(parents=True, exist_ok=True)

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-capfilt-large")
blip_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-capfilt-large")

whisper_model = whisper.load_model('base')


# @app.after_request
# def after(response):
#     print(response.status)
#     print(response.headers)
#     print(response.get_data())
#     return response


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


def process_image_sound(image_file, sound_file):
    print('processing now')
    question = whisper_model.transcribe(sound_file)['text']
    print(f"QUESTION: {question}")

    raw_image = Image.open(image_file).convert('RGB')

    inputs = blip_processor(raw_image, question, return_tensors='pt')
    out = blip_model.generate(**inputs)
    answer = blip_processor.decode(out[0], skip_special_tokens=True)
    print(f"ANSWER: {answer}")

    inputs = blip_processor(raw_image, "What is in this image?", return_tensors='pt')
    out = blip_model.generate(**inputs)
    print(f"DEBUG DESCRIPTION OF IMAGE <{image_file}>: {blip_processor.decode(out[0], skip_special_tokens=True)}")

    print("Saving audio...")
    tts = gTTS(answer)
    tts.save("answer.mp3")

    print("Playing audio...")
    p = vlc.MediaPlayer(f"file://{os.getcwd()}/answer.mp3")
    p.play()


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

    process_image_sound(image_filepath, sound_filepath)

    return {
        "success": True,
    }, 200

