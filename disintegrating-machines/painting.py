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
from jpglitch import Jpeg # local module

print("starting camera...")
camera = picamera.PiCamera()

# load cascade file for detecting faces
print("loading classifier...")
face_cascade = cv2.CascadeClassifier('./face_detect/haarcascade_frontalface_default.xml')

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

DHT_marker = b'\xc4'
SOS_marker = b'\xda'

"""
Raspberry Pi OS doesn't like opening corrupted jpegs, but macOS can do it fine :(
"""
def corrupt_image_bytes(filename):
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
                if markerNext and byte == SOS_marker and not seenFirstDHT:
                    seenFirstDHT = True

                if byte == b'\xff':
                    markerNext = True
                else:
                    markerNext = False

                if seenFirstDHT:
                    startDHT = i
                    # skip 16 bytes for SOS segment
                    randByteLocation = random.randint(startDHT + 16, filesize - 1)

                g.seek(i)
                if i > 0 and i == randByteLocation:
                    print("corrupting byte ", i)
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

def corrupt_image_glitch(filename):
    amount = 20
    seed = 4
    iterations = 2

    filename_split = filename.split(".")
    first_parts = filename_split[0].split("_")
    i = int(first_parts[-1])
    new_parts = first_parts[0:-1]
    new_parts.append(str(i + 1))
    new_filename = "_".join(new_parts) + "." + filename_split[1]

    with open(filename, "rb") as f:
        image_bytes = bytearray(f.read())
        jpeg = Jpeg(image_bytes, amount, seed, iterations)
        jpeg.save_image(new_filename)

def main_show_painting(tkRoot, original_filename, interval_length):
    filename_split = original_filename.split(".")
    i = 0

    def get_current_filename():
        return filename_split[0] + "_" + str(i) + "." + filename_split[1]

    filename = get_current_filename()
    pilImage = Image.open(filename)

    canvas = tkinter.Canvas(tkRoot, width=w, height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size

    if (imgWidth > w or imgHeight > h):
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth * ratio)
        imgHeight = int(imgHeight * ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)

    def show_painting(read_file_again):
        if read_file_again:
            # read file again
            pilImage = Image.open(get_current_filename())
            image = ImageTk.PhotoImage(pilImage)
            canvas.delete("all")
            imageSprite = canvas.create_image(w/2, h/2, image=image)
        tkRoot.update_idletasks()
        tkRoot.update()

    def main_loop():
        print("running main loop...")
        num_faces = detect_faces(False)
        did_file_change = False

        if num_faces == 0:
            print("corrupting image...")
            # corrupt_image_bytes(original_filename)
            corrupt_image_glitch(get_current_filename())
            did_file_change = True

        show_painting(did_file_change)
        return did_file_change

    while True:
        did_file_change = main_loop()

        if did_file_change:
            i += 1

        time.sleep(interval_length)

    # set_interval(main_loop, 3)

def handle_exit():
    camera.close()
    print("closing camera and exiting...")

atexit.register(handle_exit)

root = tkinter.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (w, h))
root.focus_set()
root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))

main_show_painting(root, "glacier.jpg", 2)

