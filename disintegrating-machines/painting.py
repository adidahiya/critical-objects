import io
import picamera
import cv2
import numpy
import os
import random
import threading
import tkinter
import atexit
import time
from PIL import Image, ImageTk

camera = picamera.PiCamera()

"""
Returns number of faces found
"""
def detect_faces(write_image):
    # create memory stream
    stream = io.BytesIO()
    # get the picture
    camera.resolution = (320, 240)
    print("capturing image...")
    camera.capture(stream, format='jpeg')

    # convert to numpy array
    buff = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8)

    # create opencv image
    image = cv2.imdecode(buff, 1)

    # load cascade file for detecting faces
    print("loading classifier...")
    face_cascade = cv2.CascadeClassifier('./face_detect/haarcascade_frontalface_default.xml')

    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # look for faces in the image
    print("detecting faces...")
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    print("Found " + str(len(faces)) + " face(s)")

    if write_image:
        # draw rectangle around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)

        # save image
        cv2.imwrite('result.jpg', image)

    return len(faces)


def corrupt_image(filename):
    filesize = os.path.getsize("./" + filename)

    # don't want to corrupt any bytes before this one
    startDHT = 0
    randByteLocation = 0
    randByteValue = b'\x00'

    with open(filename, "rb") as f:
        with open("new_" + filename, "wb") as g:
            byte = f.read(1)

            seenFirstDHT = False
            markerNext = False
            # num bytes
            i = 0

            while byte != b"":
                if markerNext and byte == b'\xc4' and not seenFirstDHT:
                    # print("DHT ********************************************************")
                    seenFirstDHT = True

                if byte == b'\xff':
                    markerNext = True
                else:
                    markerNext = False

                if seenFirstDHT:
                    startDHT = i
                    randByteLocation = random.randint(startDHT, filesize - 1)

                g.seek(i)
                if i > 0 and i == randByteLocation:
                    newByte = bytes([(byte[0] << 1) % 256])
                    g.write(newByte)
                else:
                    g.write(byte)

                i = i + 1
                byte = f.read(1)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def main_show_painting(original_filename):
    filename = "new_" + original_filename
    pilImage = Image.open(filename)

    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))

    canvas = tkinter.Canvas(root, width=w, height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size

    if (imgWidth > w or imgHeight > h):
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth * ratio)
        imgHeight = int(imgHeight * ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)

    def show_painting():
        # read file again
        pilImage = Image.open(filename)
        image = ImageTk.PhotoImage(pilImage)
        imageSprite = canvas.create_image(w/2, h/2, image=image)
        root.mainloop()

    def main_loop():
        print("running main loop...")
        num_faces = detect_faces(False)
        if num_faces == 0:
            corrupt_image(original_filename)
        show_painting()

    seconds = 0
    # TODO: non-blocking?
    while true:
        main_loop()
        time.sleep(5)
        seconds += 5

    # set_interval(main_loop, 3)

def handle_exit():
    camera.close()
    print("closing camera and exiting...")

atexit.register(handle_exit)
main_show_painting("glacier.jpg")

