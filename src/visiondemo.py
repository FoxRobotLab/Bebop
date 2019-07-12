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
from src.object_tracking import *
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


def user_code(bebopVision:DroneVisionGUI, args):
    bebop = args[0]
    print("Vision successfully started! Sleeping for a sec.")
    bebop.smart_sleep(1)

    if bebopVision.vision_running:

        # Key listener thread init
        k = Keybop(bebop)
        key_listener = threading.Thread(target=k.start,daemon=True)
        key_listener.start()

        # Vision thread init. All cv related code should go in the vision thread. It may also be able to go in this
        # thread, but that seems less reliable.

        vision = threading.Thread(target=qr_tracking, args=(bebopVision, bebop), daemon=True)
        vision.start()
        vision.join()

        print("Stopping!")
        bebopVision.close_exit()

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
        bebopVision = DroneVisionGUI(bebop, is_bebop=True, user_code_to_run=user_code,
                                     user_args=(bebop, ))

        userVision = UserVision(bebopVision)
        bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        bebopVision.open_video()

    else:
        print("Error connecting to bebop.  Retry")