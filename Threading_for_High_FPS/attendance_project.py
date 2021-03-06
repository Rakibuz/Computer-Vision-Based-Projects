import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from imutils.video import WebcamVideoStream
import time


#frame counter
pTime=0
cTime=0

path = './Threading_for_High_FPS/Training_images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])  
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

#marking attendance
def markAttendance(name):
    with open('./Threading_for_High_FPS/Attendance.csv','r+') as f:
        myDataList = f.readlines() # if somebody already arrived we dont want to repeat it
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            Str_time = now.strftime("%H:%M:%S")
            Str_day = now.strftime("%m/%d/%Y")
            f.writelines(f'\n{name},{Str_time},{Str_day}')


encodeListKnown = findEncodings(images)
#print(len(encodeListKnown))
print('Encoding Complete')

#cap = cv2.VideoCapture(0)
print("[INFO] sampling THREADED frames from webcam...")
#webcamVideoStreamclass object creation
vs = WebcamVideoStream(src=0).start()

while True:
    #success, img = cap.read()
    img = vs.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4 #for scaling
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)

    cTime=time.time()
    fps=1/(cTime-pTime)
    #print(int(fps))
    pTime=cTime
    #print(int(fps))
    cv2.putText(img,str(int(fps)),(30,50),cv2.FONT_HERSHEY_PLAIN,3,(0,0,220),3)
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)  
    
 
