import requests
from PIL import Image

# from transformers import BlipProcessor, Blip2ForConditionalGeneration
# processor = BlipProcessor.from_pretrained("Salesforce/blip2-flan-t5-xl")
# model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl")

from transformers import BlipProcessor, BlipForQuestionAnswering
processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-capfilt-large")
model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-capfilt-large")

print("Finished loading model")

img_url = 'https://www.hethwoodfoundation.com/gridmedia/img/quad/quad7_orig.jpg' 
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

while True:
    question = input(">> ")
    inputs = processor(raw_image, question, return_tensors="pt")
    out = model.generate(**inputs)

    print(processor.decode(out[0], skip_special_tokens=True))

