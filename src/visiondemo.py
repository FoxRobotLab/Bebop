"""
Demo of the Bebop vision using DroneVisionGUI (relies on libVLC).  It is a different
multi-threaded approach than DroneVision

Author: Amy McGovern
"""
from pyparrot.Bebop import Bebop
from pyparrot.DroneVisionGUI import DroneVisionGUI
import cv2
import threading
from src.bebop_teleop import Keybop
isAlive = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        #print("saving picture")
        img = self.vision.get_latest_valid_picture()
        #print(img)
        # cv2.imwrite("test"+datetime.now().strftime("%H%M%S")+".png",img)


def demo_user_code_after_vision_opened(bebopVision:DroneVisionGUI, args):
    bebop = args[0]
    print("Vision successfully started! Sleeping for a sec.")
    bebop.smart_sleep(1)

    if bebopVision.vision_running:
        print("Starting key listeners!")
        threading.Thread(target=Keybop(bebop).start).start()

        cv2.namedWindow("cv_img")
        while cv2.getWindowProperty('cv_img', 0) >= 0:
            img = bebopVision.get_latest_valid_picture()
            cv2.imshow("cv_img", img)
            cv2.waitKey(1)

        print("Stopping!")
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
                                     user_args=(bebop, ))

        userVision = UserVision(bebopVision)
        bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        bebopVision.open_video()

    else:
        print("Error connecting to bebop.  Retry")