#!/usr/bin/env python


import numpy as np
import cv2
from pyparrot.DroneVisionGUI import DroneVisionGUI
from pyparrot.Bebop import Bebop
import time
import pyzbar.pyzbar as zbar



def show_hist(hist):
    """Takes in the histogram, and displays it in the hist window."""
    bin_count = hist.shape[0]
    bin_w = 24
    img = np.zeros((256, bin_count * bin_w, 3), np.uint8)
    for i in range(bin_count):
        h = int(hist[i])
        cv2.rectangle(img, (i * bin_w + 2, 255), ((i + 1) * bin_w - 2, 255 - h), (int(180.0 * i / bin_count), 255, 255),
                      -1)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    cv2.imshow('hist', img)


def color_tracking(drone_vision:DroneVisionGUI, bebop:Bebop):
    showBackProj = False
    showHistMask = False

    frame = drone_vision.get_latest_valid_picture()

    if frame is not None:
        (hgt, wid, dep) = frame.shape
        cv2.namedWindow('camshift')
        cv2.namedWindow('hist')
        cv2.moveWindow('hist', 700, 100)  # Move to reduce overlap

        # Initialize the track window to be the whole frame
        track_window = (0, 0, wid, hgt)
        #
        # Initialize the histogram from the stored image
        # Here I am faking a stored image with just a couple of blue colors in an array
        # you would want to read the image in from the file instead
        histImage = np.array([[[110, 70, 50]],
                              [[111, 128, 128]],
                              [[115, 100, 100]],
                              [[117, 64, 50]],
                              [[117, 200, 200]],
                              [[118, 76, 100]],
                              [[120, 101, 210]],
                              [[121, 85, 70]],
                              [[125, 129, 199]],
                              [[128, 81, 78]],
                              [[130, 183, 111]]], np.uint8)
        histImage = cv2.imread('orange.jpg')
        histImage = cv2.cvtColor(histImage,cv2.COLOR_BGR2HSV)
        maskedHistIm = cv2.inRange(histImage, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        cv2.imshow("masked",maskedHistIm)
        cv2.imshow("histim",histImage)
        hist = cv2.calcHist([histImage], [0], maskedHistIm, [16], [0, 180])
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        hist = hist.reshape(-1)
        #show_hist(hist)

        # start processing frames
        while cv2.getWindowProperty('camshift', 0) >= 0:
            frame = drone_vision.get_latest_valid_picture()
            vis = frame.copy()
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # convert to HSV
            mask = cv2.inRange(hsv, np.array((0., 60., 32.)),
                               np.array((180., 255., 255.)))  # eliminate low and high saturation and value values


            # The next line shows which pixels are being used to make the histogram.
            # it sets to black all the ones that are masked away for being too over or under-saturated
            if showHistMask:
                vis[mask == 0] = 0

            prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
            prob &= mask
            term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            track_box, track_window = cv2.CamShift(prob, track_window, term_crit)
            print(track_box[1][0]*track_box[1][1])

            if showBackProj:
                vis[:] = prob[..., np.newaxis]
            try:
                cv2.ellipse(vis, track_box, (0, 0, 255), 2)
                area = track_box[1][0]*track_box[1][1]
                if area > 7000:
                    print("GOING BACK")
                    bebop.fly_direct(roll=0,pitch=-20,yaw=0,vertical_movement=0,duration=0.5)
                    #bebop.smart_sleep(1)
                elif area < 4000:
                    print("GOING FORWARD")
                    bebop.fly_direct(roll=0,pitch=20,yaw=0,vertical_movement=0,duration=0.5)
                    #bebop.smart_sleep(1)
            except:
                pass
                # print("Track box:", track_box)

            cv2.imshow('camshift', vis)

            ch = chr(0xFF & cv2.waitKey(5))
            if ch == 'q':
                break
            elif ch == 'b':
                showBackProj = not showBackProj
            elif ch == 'v':
                showHistMask = not showHistMask

    bebop.safe_land(10)
    cv2.destroyAllWindows()

def face_tracking(droneVision:DroneVisionGUI,bebop:Bebop):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    body_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

    cv2.namedWindow("face_tracking")

    frame = droneVision.get_latest_valid_picture()
    # bebop.fly_direct(roll=0,pitch=0,yaw=0,vertical_movement=20,duration=0.1)

    while cv2.getWindowProperty('face_tracking', 0) >= 0:
        frame = droneVision.get_latest_valid_picture()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        (x,y,w,h) = None, None, None, None
        if len(faces) > 0:
            (x,y,w,h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 1)
            print("Face Size: "+ str(w*h))

        backup_threshold = 3600
        fwd_threshold = 2000

        if w is not None and w*h > backup_threshold:
            print("GOING BACK")
            bebop.fly_direct(roll=0,pitch=-20,yaw=0,vertical_movement=0,duration=0.1)
        elif w is not None and w*h < fwd_threshold:
            print("GOING FORWARD")
            bebop.fly_direct(roll=0, pitch=20, yaw=0, vertical_movement=0, duration=0.1)

        if x is not None and x+(w/2.0) > 650:
            print("GOING RIGHT")
            bebop.fly_direct(roll=0,pitch=0,yaw=70,vertical_movement=0,duration=0.1)
        elif x is not None and x+(w/2.0) < 200:
            print("GOING LEFT")
            bebop.fly_direct(roll=0, pitch=0, yaw=-70, vertical_movement=0, duration=0.1)

        cv2.imshow("face_tracking",frame)
        cv2.waitKey(10)

    bebop.safe_land(10)
    cv2.destroyAllWindows()

def qr_tracking(droneVision:DroneVisionGUI, bebop:Bebop):
    cv2.namedWindow('qr')

    while cv2.getWindowProperty('qr', 0) >= 0:
        img = droneVision.get_latest_valid_picture()
        print(img.shape)
        x,y,w,h = None,None,None,None
        try:
            rect = zbar.decode(img)[0][2]
            x,y,w,h = rect
            print(w*h)
        except IndexError:
            pass

        if x is not None:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255))

        backup_threshold = 5000
        fwd_threshold = 3600

        if w is not None and w * h > backup_threshold:
            print("GOING BACK")
            bebop.fly_direct(roll=0, pitch=-20, yaw=0, vertical_movement=0, duration=0.07)
        elif w is not None and w * h < fwd_threshold:
            print("GOING FORWARD")
            bebop.fly_direct(roll=0, pitch=20, yaw=0, vertical_movement=0, duration=0.07)

        if x is not None and x + (w / 2.0) > 650:
            print("GOING RIGHT")
            bebop.fly_direct(roll=0, pitch=0, yaw=70, vertical_movement=0, duration=0.1)
        elif x is not None and x + (w / 2.0) < 200:
            print("GOING LEFT")
            bebop.fly_direct(roll=0, pitch=0, yaw=-70, vertical_movement=0, duration=0.1)

        if x is not None and y + (h / 2.0) > 380:
            print("GOING DOWN")
            bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-40, duration=0.1)
        elif x is not None and y + (h / 2.0) < 100:
            print("GOING UP")
            bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=40, duration=0.1)



        cv2.imshow('qr', img)
        cv2.waitKey(10)

    bebop.safe_land(10)
    cv2.destroyAllWindows()