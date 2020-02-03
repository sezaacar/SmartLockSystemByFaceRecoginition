

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

fname = "9.jpg"
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

message = tk.Label(window, text="Remote Smart Locking System By Face Recognition", fg="red",
                   font=('times', 30, 'italic bold'))
message.place(x=250, y=60)

message = tk.Label(window, text="Administration Screen", fg="red", font=('times', 10, 'italic bold'))
message.place(x=700, y=800)

lbl = tk.Label(window, text="Enter ID", width=20, height=2, fg="red", bg="White", font=('times', 15, ' bold '))
lbl.place(x=150, y=200)

txt = tk.Entry(window, width=20, bg="White", fg="red", font=('times', 15, ' bold '))
txt.place(x=450, y=215)

lbl2 = tk.Label(window, text="Enter Name", width=20, fg="red", bg="White", height=2, font=('times', 15, ' bold '))
lbl2.place(x=150, y=300)

txt2 = tk.Entry(window, width=20, bg="White", fg="red", font=('times', 15, ' bold '))
txt2.place(x=450, y=315)

lbl3 = tk.Label(window, text="Notification : ", width=20, fg="red", bg="White", height=2,
                font=('times', 15, ' bold underline '))
lbl3.place(x=150, y=500)

message = tk.Label(window, text="", bg="White", fg="red", width=30, height=2, activebackground="White",
                   font=('times', 15, ' bold '))
message.place(x=450, y=500)

lbl3 = tk.Label(window, text="Entry : ", width=20, fg="red", bg="White", height=2,
                font=('times', 15, ' bold  underline'))
lbl3.place(x=150, y=650)

message2 = tk.Label(window, text="", fg="red", bg="White", activeforeground="green", width=30, height=2,
                    font=('times', 15, ' bold '))
message2.place(x=450, y=650)


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


def TakeImages():
    Id = (txt.get())
    name = (txt2.get())
    if (is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "/home/pi/Desktop/0679/haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # incrementing sample number
                sampleNum = sampleNum + 1
                # saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("/home/pi/Desktop/0679/TrainingImage/ " + name + "." + Id + '.' + str(sampleNum) + ".jpg",
                            gray[y:y + h, x:x + w])
                # display the frame
                cv2.imshow('frame', img)

            cv2.imshow('img', img)
            # wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum > 60:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for ID : " + Id + " Name : " + name
        row = [Id, name]
        with open('/home/pi/Desktop/0679/StudentDetails/StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text=res)
    else:
        if (is_number(Id) == 0):
            res = "Enter Numeric Id"
            message.configure(text=res)
        if (name.isalpha() == 0):
            res = "Enter Alphabetical Name"
            message.configure(text=res)


def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()  # recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "/home/pi/Desktop/0679/haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels("/home/pi/Desktop/0679/TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("/home/pi/Desktop/0679/TrainingImageLabel/Trainner.yml")
    res = "Image Trained"  # +",".join(str(f) for f in Id)
    message.configure(text=res)


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


def TrackImages():
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
            if (Id >  0 ):          # WE ARE USING ID SAMPLE TO LOCK TO DOOR

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


clearButton = tk.Button(window, text="Clear", command=clear, fg="red", bg="White", width=20, height=2,
                        activebackground="Red", font=('times', 15, ' bold '))
clearButton.place(x=700, y=200)
clearButton2 = tk.Button(window, text="Clear", command=clear2, fg="red", bg="White", width=20, height=2,
                         activebackground="Red", font=('times', 15, ' bold '))
clearButton2.place(x=700, y=300)
takeImg = tk.Button(window, text="Take Images", command=TakeImages, fg="blue", bg="gray", width=20, height=3,
                    activebackground="Red", font=('times', 15, ' bold '))
takeImg.place(x=1000, y=200)
trainImg = tk.Button(window, text="Train Images", command=TrainImages, fg="blue", bg="gray", width=20, height=3,
                     activebackground="Red", font=('times', 15, ' bold '))
trainImg.place(x=1000, y=350)
trackImg = tk.Button(window, text="Track Images", command=TrackImages, fg="blue", bg="gray", width=20, height=3,
                     activebackground="Red", font=('times', 15, ' bold '))
trackImg.place(x=1000, y=500)
ring = tk.Button(window, text="Ring", command=TrackImages, fg="blue", bg="gray", width=20, height=3,
                     activebackground="Red", font=('times', 15, ' bold '))
ring.place(x=1000, y=800)
quitWindow = tk.Button(window, text="Quit", command=window.destroy, fg="red", bg="gray", width=20, height=3,
                       activebackground="Red", font=('times', 15, ' bold '))
quitWindow.place(x=1000, y=650)

window.mainloop()

