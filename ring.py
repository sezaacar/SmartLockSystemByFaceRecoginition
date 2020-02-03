# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import Message, Text
from cv2 import cv2
import os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
import RPi.GPIO as GPIO

channel = 21

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

GPIO.cleanup()




window = tk.Tk()
window.title("Face_Recogniser")

fname = "1.jpg"
bg_image = ImageTk.PhotoImage(file=fname)

# get the width and height of the image
w = bg_image.width()
h = bg_image.height()
# size the window so the image will fill it
window.geometry("%dx%d+50+30" % (w, h))
cv = tk.Canvas(width=w, height=h)
cv.pack(side='top', fill='both', expand='yes')
cv.create_image(0, 0, image=bg_image, anchor='nw')

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

message = tk.Label(window, text="Home Sweet Home", fg="red",
                   font=('times', 50, 'italic bold'))
message.place(x=500, y=100)

message = tk.Label(window, text="Please Identify Yourself", fg="red", font=('times', 50, 'italic bold'))
message.place(x=500, y=200)


lbl3 = tk.Label(window, text="Entry : ", width=30, fg="red", bg="White", height=2,
                font=('times', 20, ' bold  underline'))
lbl3.place(x=120, y=500)

message2 = tk.Label(window, text="", fg="red", bg="White", activeforeground="green", width=50, height=2,
                    font=('times', 20, ' bold '))
message2.place(x=650, y=500)


def clear():
    txt.delete(0, 'end')
    res = ""
    message.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = ""
    message.configure(text=res)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def getImagesAndLabels(path):
    # get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # print(imagePaths)

    # create empth face list
    faces = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids


def Ring():
    tt = "Unknown"
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer() , cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("/home/pi/Desktop/0679/TrainingImageLabel/Trainner.yml")
    harcascadePath = "/home/pi/Desktop/0679/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("/home/pi/Desktop/0679/StudentDetails/StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    entry = pd.DataFrame(columns=col_names)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if (conf < 50):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['Id'] == Id]['Name'].values
                tt = str(Id) + "-" + aa
                entry.loc[len(entry)] = [Id, aa, date, timeStamp]

            else:
                Id = 'Unknown'
                tt = str(Id)
            if (conf > 75):
                noOfFile = len(os.listdir("/home/pi/Desktop/0679/ImagesUnknown")) + 1
                cv2.imwrite("/home/pi/Desktop/0679/ImagesUnknown/Image" + str(noOfFile) + ".jpg", im[y:y + h, x:x + w])
            cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)

        tt = "Unknown"
        entry = entry.drop_duplicates(subset=['Id'], keep='first')
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            if (Id > 0):    # WE ARE USING ID SAMPLE TO LOCK TO DOOR

                channel = 21

                # GPIO setup
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(channel, GPIO.OUT)

                def door_on(pin):
                    GPIO.output(pin, GPIO.HIGH)  # Turn LOCK on

                def door_off(pin):
                    GPIO.output(pin, GPIO.LOW)  # Turn LOCK off

                if __name__ == '__main__':
                    try:
                        door_on(channel)
                        time.sleep(5)
                        door_off(channel)
                        time.sleep(1)
                        GPIO.cleanup()
                    except KeyboardInterrupt:
                        GPIO.cleanup()
             

            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    fileName = "/home/pi/Desktop/0679/Entry/Entry" + date + "_" + Hour + "-" + Minute + "-" + Second + ".csv"
    entry.to_csv(fileName, index=False)
    cam.release()
    cv2.destroyAllWindows()
    # print(entry)
    res = entry
    message2.configure(text=res)


ring = tk.Button(window, text="Ring", command=Ring, fg="blue", bg="gray", width=50, height=3,
                     activebackground="red", font=('times', 30, ' bold '))
ring.place(x=300, y=300)
quitWindow = tk.Button(window, text="Quit", command=window.destroy, fg="red", bg="gray", width=10, height=2,
                       activebackground="Red", font=('times', 15, ' bold '))
quitWindow.place(x=1550, y=700)

window.mainloop()

