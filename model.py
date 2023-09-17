import os
import pathlib
from flask import Flask, request
from werkzeug.utils import secure_filename
# from transformers import BlipProcessor, BlipForQuestionAnswering
# from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
from PIL import Image
import whisper
from datetime import datetime
import requests
from transformers import BlipProcessor, Blip2ForConditionalGeneration
# from transformers import BlipProcessor, BlipForQuestionAnswering

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip2-flan-t5-xl")
blip_model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl")

IMAGE_FOLDER = "./images"
SOUND_FOLDER = "./sounds"

app = Flask(__name__)

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['SOUND_FOLDER'] = SOUND_FOLDER
pathlib.Path(IMAGE_FOLDER).mkdir(parents=True, exist_ok=True)
pathlib.Path(SOUND_FOLDER).mkdir(parents=True, exist_ok=True)

# blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-capfilt-large")
# blip_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-capfilt-large")
# blip_model = InstructBlipForConditionalGeneration.from_pretrained("Salesforce/instructblip-vicuna-7b")
# blip_processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")

whisper_model = whisper.load_model('base')


@app.after_request
def after(response):
    print(response.status)
    print(response.headers)
    print(response.get_data())
    return response


def process_image_sound(image_file, sound_file):
    print('processing now')
    question = whisper_model.transcribe(sound_file)['text']
    print(f"QUESTION: {question}")

    raw_image = Image.open(image_file).convert('RGB')

    inputs = blip_processor(raw_image, f"Question: {question} Answer: ", return_tensors='pt')
    out = blip_model.generate(**inputs, max_new_tokens=256, min_length=10)
    # out = blip_model.generate(**inputs,
    #                         num_beams=5,
    #                         max_length=256,
    #                         min_length=1,
    #                         repetition_penalty=1.5,
    #                         length_penalty=1.0,
    #                         temperature=1)``
    answer = blip_processor.batch_decode(out, skip_special_tokens=True)[0].strip()
    # answer = blip_processor.decode(out[0], skip_special_tokens=True)
    print(f"ANSWER: {answer}")

    # inputs = blip_processor(raw_image, "Question: What is in this image? Answer: ", return_tensors='pt')
    # out = blip_model.generate(**inputs, max_new_tokens=256)
    # # out = blip_model.generate(**inputs,
    # #                         num_beams=5,
    # #                         max_length=256,
    # #                         min_length=1,
    # #                         repetition_penalty=1.5,
    # #                         length_penalty=1.0,
    # #                         temperature=1)
    # print(f"DEBUG DESCRIPTION OF IMAGE <{image_file}>: {blip_processor.batch_decode(out, skip_special_tokens=True)[0].strip()}")

    return answer

def check_for_file(name):
    if name not in request.files:
        print(f"didn't find file {name}")
        return {
            "success": False,
            "message": f"'{name}' file not found in request.",
        }, 400

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

    answer = process_image_sound(image_filepath, sound_filepath)

    return {
        "success": True,
        "answer": answer,
    }, 200