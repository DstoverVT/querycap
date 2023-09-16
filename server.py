import os
import pathlib
from flask import Flask, request
from werkzeug.utils import secure_filename
from transformers import BlipProcessor, BlipForQuestionAnswering
from PIL import Image

IMAGE_FOLDER = "./images"
SOUND_FOLDER = "./sounds"

app = Flask(__name__)

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SOUND_FOLDER'] = SOUND_FOLDER
pathlib.Path(IMAGE_FOLDER).mkdir(parents=True, exist_ok=True)
pathlib.Path(SOUND_FOLDER).mkdir(parents=True, exist_ok=True)

processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-capfilt-large")
model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-capfilt-large")


def check_for_file(name):
    if name not in request.files:
        return {
            "success": False,
            "message": f"'{name}' file not found in request.",
        }, 400


def check_for_form(name):
    if name not in request.form:
        return {
            "success": False,
            "message": f"'{name}' field not found in form.",
        }, 400


def process_image_text(image, text):
    raw_image = Image.open(image).convert('RGB')
    inputs = processor(raw_image, text, return_tensors='pt')
    out = model.generate(**inputs)
    print(processor.decode(out[0], skip_special_tokens=True))


@app.route("/send_image", methods=['POST'])
def send_image():
    check_for_file('image')
    # check_for_file('sound')
    check_for_form('text')
    
    image = request.files['image']
    # sound = request.files['sound']
    text = request.form['text']

    image_filename = secure_filename(image.filename)
    image.save(
        os.path.join(app.config['IMAGE_FOLDER'], image_filename)
    )

    # sound_filename = secure_filename(sound.filename)
    # sound.save(
    #     os.path.join(app.config['SOUND_FOLDER'], sound_filename)
    # )

    # process_image_sound(image, sound)
    process_image_text(image, text)

    return {
        "success": True,
    }, 200

