# QueryCap
QueryCap - A fashionable headset AI companion that can see what you see and answer questions about what's in front of you. For VTHacks 2023.

See more details about project, such as video, [on this Devpost link](https://devpost.com/software/querycap-ask-any-question-about-what-you-see?ref_content=my-projects-tab&ref_feature=my_projects)

## Prerequisites
- Raspberry Pi
  - Runs `Pi/pi_controller.py`
- Computer/server with at least 64GB of RAM for model
  - We used an AWS EC2 server
  - Runs `model.py`
- Computer/server on same WiFi network as Raspberry Pi for server
  - Runs `server.py`
 
## Hardware Setup
1. Need a Raspberry Pi on the same WiFi network as the computer running `server.py`
2. Plug a USB webcam, into the Raspberry Pi, as well as a microphone. Our webcam had a built-in microphone
3. Connect a button to Rapsberry Pi GPIO pin 15 (BCM numbering) and Ground, and configure pin 15 to use an internal pull-up resistor

## Software Setup (required before running)
1. On Raspberry Pi, install libraries in `Pi/requirements.txt` using `pip install -r Pi/requirements.txt` in a Python virtual environment
2. On computer/servers running the model and the server, install libraries in `requirements.txt` using `pip install -r requirements.txt` in a Python virtual environment
3. Networking setup for HTTP requests between devices:
    - On the Pi, in `Pi/pi_controller.py`, set the `URL` variable to `http://<server IP address>:5000/send_image`, where `<IP address>` is the IP address of the computer running `server.py` on the same WiFi network
    - On the computer running `server.py`, set up SSH port tunneling from port 5001 to port 5000 of the computer running `model.py` in another terminal: SSH into the computer running `model.py` like normal but passing the flag `-L 5001:<model server IP address>:5000`, where `<model server IP address>` is the IP address of the computer running `model.py`
    - In our case, we set this up because we were using an AWS server

## Running Software
5. For computer running `server.py`, run `flask --app server.py run --host 0.0.0.0`
6. For computer running `model.py`, run `flask --app model.py run`
7. For Raspberry Pi, run `python Pi/pi_controller.py`
8. Now, whenever you want to ask a question, hold down the button connected to the Raspberry Pi and speak your question
    - A picture will be taken on button press, and your audio will be recorded for as long as button is held
    - Then, the computer running `server.py` will play the answer through its speaker. Voila!
