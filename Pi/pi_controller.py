import cv2
import time
import os


def image_capture(path, FPS):
    '''Capture frames from webcam.'''
    num = 0
    video = cv2.VideoCapture(0)

    if video.isOpened():
        while(True):
            ret, frame = video.read()
            # Save 1 frame per second to path
            if(ret):
                print("saving image")
                cv2.imwrite(f"{path}/image{num}.png", frame)
                num += 1
                time.sleep(1/FPS)
            else:
                print(f"frame {num} invalid")
    else:
        print("Video could not be opened")
    
        
if __name__ == '__main__':
    path = "images"

    if not os.path.exists(path):
        os.makedirs(path)
    
    image_capture(path, FPS=1)