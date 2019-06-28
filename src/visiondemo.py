"""
Demo of the Bebop vision using DroneVisionGUI (relies on libVLC).  It is a different
multi-threaded approach than DroneVision

Author: Amy McGovern
"""
from pyparrot.Bebop import Bebop
from pyparrot.DroneVisionGUI import DroneVisionGUI
import threading
import cv2
import time
from PyQt5.QtGui import QImage
from datetime import datetime
import sys
from src.bebop_teleop import Keybop
isAlive = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        #print("saving picture")
        img = self.vision.get_latest_valid_picture()
        # cv2.imwrite("test"+datetime.now().strftime("%H%M%S")+".png",img)




def draw_current_photo():
    """
    Quick demo of returning an image to show in the user window.  Clearly one would want to make this a dynamic image
    """
    image = cv2.imread('test_image_000001.png')

    if (image is not None):
        if len(image.shape) < 3 or image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width, byteValue = image.shape
        byteValue = byteValue * width

        qimage = QImage(image, width, height, byteValue, QImage.Format_RGB888)

        return qimage
    else:
        return None

def demo_user_code_after_vision_opened(bebopVision, args):
    bebop = args[0]

    print("Vision successfully started!")
    #removed the user call to this function (it now happens in open_video())
    #bebopVision.start_video_buffering()

    # takeoff
    # bebop.safe_takeoff(5)

    # skipping actually flying for safety purposes indoors - if you want
    # different pictures, move the bebop around by hand
    print("Fly me around by hand!")
    bebop.smart_sleep(1)

    if bebopVision.vision_running:
        print("Moving the camera using velocity")

        Keybop(bebop).start()
        # bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=-2, duration=2)
        # bebop.smart_sleep(30)
        # bebop.fly_direct(pitch=0,roll=0,yaw=0,vertical_movement=0,duration=12)
        # bebop.fly_direct(pitch=0, roll=0, yaw=100, vertical_movement=0, duration=12)
        # land
        # bebop.safe_land(5)

        print("Finishing demo and stopping vision")
        bebopVision.close_video()

    # disconnect nicely so we don't need a reboot
    print("disconnecting")
    bebop.disconnect()


if __name__ == "__main__":
    # make my bebop object
    bebop = Bebop()
    print("Battery level:"+str(bebop.sensors.battery))
    # connect to the bebop
    success = bebop.connect(5)

    if success:
        # start up the video
        bebopVision = DroneVisionGUI(bebop, is_bebop=True, user_code_to_run=demo_user_code_after_vision_opened,
                                     user_args=(bebop, ))#, user_draw_window_fn=draw_current_photo)

        userVision = UserVision(bebopVision)
        bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        bebopVision.open_video()

    else:
        print("Error connecting to bebop.  Retry")