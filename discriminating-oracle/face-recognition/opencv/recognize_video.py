# USAGE
# python recognize_video.py --detector model \
#	--embedding-model openface_nn4.small2.v1.t7 \
#	--recognizer output/recognizer.pickle \
#	--le output/le.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import sys
import argparse
import imutils
import pickle
import time
import cv2
import os
import random


# image manipulation functions
def grab_frame(cap):
    ret, frame = cap.read()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detector", required=True,
                help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", required=True,
                help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", required=True,
                help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", required=True,
                help="path to label encoder")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
                help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
modelPath = os.path.sep.join([args["detector"],
                              "res10_300x300_ssd_iter_140000.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open(args["recognizer"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

# initialize the video stream, then allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
vs2 = cv2.VideoCapture(0)
time.sleep(2.0)

# start the FPS throughput estimator
fps = FPS().start()

# if a trusted face is detected with a given confidence for enough time,
# enter "unlocked" mode
state = 'locked'  # 'locked' | 'unlocking' | 'unlocked'
unlock_timer = 2  # seconds
unlock_confidence = 0.75
time_of_last_trusted_face = 0
trusted_faces = ['adi', 'brent']

# loop over frames from the video file stream
while True:
    now = time.time()

    # grab the frame from the threaded video stream
    frame = vs.read()

    # testing image pyramid

    # resize the frame to have a width of 600 pixels (while
    # maintaining the aspect ratio), and then grab the image
    # dimensions
    frame = imutils.resize(frame, width=600)
    (h, w) = frame.shape[:2]

    # construct a blob from the image
    imageBlob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False)

    # apply OpenCV's deep learning-based face detector to localize
    # faces in the input image
    detector.setInput(imageBlob)
    detections = detector.forward()

    seen_trusted_face = False
    # if we're in the progress of unlocking (counting up to the timer),
    # we don't want to update time_of_last_trusted_face
    # is_unlocking = now - time_of_last_trusted_face < unlock_timer

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the face ROI
            face = frame[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]

            # ensure the face width and height are sufficiently large
            if fW < 20 or fH < 20:
                continue

            # construct a blob for the face ROI, then pass the blob
            # through our face embedding model to obtain the 128-d
            # quantification of the face
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                                             (96, 96), (0, 0, 0), swapRB=True, crop=False)
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            # perform classification to recognize the face
            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            # if we see a trusted face, we can update state
            if name in trusted_faces and confidence > unlock_confidence:
                seen_trusted_face = True
                if state == 'locked':
                    state = 'unlocking'
                    time_of_last_trusted_face = now
                elif state == 'unlocking':
                    if now - time_of_last_trusted_face > unlock_timer:
                        state = 'unlocked'
                else:
                    # unlocked
                    pass

            # draw the bounding box of the face along with the
            # associated probability
            text = "{}: {:.2f}%".format(name, proba * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            color = (0, 255, 0) if state == 'unlocked' else (0, 0, 255)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          color, 2)
            cv2.putText(frame, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
    print("trusted", seen_trusted_face)
    if not seen_trusted_face:
        state = 'locked'
        time_of_last_trusted_face = 0

        # testing canny edge detection
        edges = cv2.Canny(frame, 100, 200)
        output = edges
        # testing image pyramid output
#        A = frame
#        A = cv2.resize(A, (300, 300))
#        print("A: ", A)
#        cv2.imshow("Frame ", A)
#        cv2.imwrite("./image_A.jpg", A)
#        dir = './dataset/adi/'
#        randimg = random.choice(os.listdir(dir))
#        B = cv2.imread(str(os.path.join(dir, randimg)))
#        B = cv2.resize(B, (300, 300))
#        print("B: ", B)
#        cv2.imshow("Frame ", B)
#        sleep(2)
#        cv2.imwrite('./image_B.jpg', B)
#        # generate Gaussian pyramid for A
#        G = A.copy()
#        gpA = [G]
#        for i in range(6):
#            G = cv2.pyrDown(gpA[i])
#            gpA.append(G)
#
#        # generate Gaussian pyramid for B
#        G = B.copy()
#        gpB = [G]
#        for i in range(6):
#            G = cv2.pyrDown(gpA[i])
#            gpB.append(G)
#
#        # generate Laplacian Pyramid for A
#        lpA = [gpA[5]]
#        for i in range(5, 0, -1):
#            size = (gpA[i-1].shape[1], gpA[i-1].shape[0])
#            GE = cv2.pyrUp(gpA[i], dstsize=size)
#            L = cv2.subtract(gpA[i-1], GE)
#            lpA.append(L)
#
#        # generate Laplacian Pyramid for B
#        lpB = [gpB[5]]
#        for i in range(5, 0, -1):
#            size = (gpB[i-1].shape[1], gpB[i-1].shape[0])
#            GE = cv2.pyrUp(gpB[i], dstsize=size)
#            lpB.append(L)
#
#        # Now add left and right halves of images in each level
#        LS = []
#        for la, lb in zip(lpA, lpB):
#            rows, cols, dpt = la.shape
#            ls = np.hstack((la[:, 0:cols//2], lb[:, cols//2:]))
#            LS.append(ls)
#
#        # now reconstruct
#        ls_ = LS[0]
#        for i in range(1, 6):
#            size = (LS[i].shape[1], LS[i].shape[0])
#            ls_ = cv2.pyrUp(ls_, dstsize=size)
#            ls_ = cv2.add(ls_, LS[i])
#        # image with direct connecting each half
#        real = np.hstack((A[:, :cols//2], B[:, cols//2:]))
#        cv2.imshow("Frame", ls_)
#        cv2.imwrite("./blend_output.jpg", ls_)
    else:
        print("hitting else")
        output = frame
        fps.update()

    cv2.imshow("Frame", output)
    # update the FPS counter
    # show the output frame

    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
