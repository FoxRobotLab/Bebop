import keyboard
from pyparrot.Bebop import Bebop

class Keybop(object):
    def __init__(self, bebop:Bebop=None):
        print('WARNING: Key listening is global; while piloting the drone, you can NOT use your keyboard for anything else!')
        print('- Control Bebop -\nTakeoff: Ctrl+T\nLand: Space\nFwd/Back/Left/Right: i/k/j/l\nUp/Dwn/Clockwise/CClockwise: '+
              'w/s/d/a\nPan/tilt camera: up/down/left/right\nLand and stop controls: Esc\nDO NOT PRESS AND HOLD BUTTONS!')
        self.interrupted = False
        self.bebop = bebop

    def start(self):
        print("Starting teleop key listener!")
        keyboard.on_press_key('w', self.fly_up)
        keyboard.on_press_key('s', self.fly_down)
        keyboard.on_press_key('a', self.yaw_ccw)
        keyboard.on_press_key('d', self.yaw_cw)

        keyboard.on_press_key('i', self.fly_fwd)
        keyboard.on_press_key('k', self.fly_back)
        keyboard.on_press_key('j', self.fly_left)
        keyboard.on_press_key('l', self.fly_right)

        keyboard.on_press_key('left',self.pan_left)
        keyboard.on_press_key('right', self.pan_right)
        keyboard.on_press_key('up', self.tilt_cam_up)
        keyboard.on_press_key('down', self.tilt_cam_down)
        keyboard.on_press_key('esc', self.interrupt)
        keyboard.on_press_key(' ',self.land)
        keyboard.add_hotkey('ctrl+t',self.takeoff)
        print(self.interrupted)
        while not self.interrupted:
            pass

    def fly_up(self,e):
        print("up")
        self.bebop.fly_direct(roll=0,pitch=0,yaw=0,vertical_movement=20,duration=0.00001)

    def fly_down(self,e):
        self.bebop.fly_direct(roll=0,pitch=0,yaw=0,vertical_movement=-20,duration=0.00001)

    def fly_left(self, e):
        self.bebop.fly_direct(roll=-20, pitch=0, yaw=0, vertical_movement=0, duration=0.00001)

    def fly_right(self, e):
        self.bebop.fly_direct(roll=20, pitch=0, yaw=0, vertical_movement=0, duration=0.00001)

    def yaw_cw(self, e):
        self.bebop.fly_direct(roll=0, pitch=0, yaw=50, vertical_movement=0, duration=0.00001)

    def yaw_ccw(self, e):
        self.bebop.fly_direct(roll=0, pitch=0, yaw=-50, vertical_movement=0, duration=0.00001)

    def fly_fwd(self, e):
        self.bebop.fly_direct(roll=0, pitch=20, yaw=0, vertical_movement=0, duration=0.00001)

    def fly_back(self, e):
        self.bebop.fly_direct(roll=0, pitch=-20, yaw=0, vertical_movement=0, duration=0.00001)

    def pan_left(self,e):
        self.bebop.pan_tilt_camera_velocity(pan_velocity=-4, tilt_velocity=0, duration=0.00001)
    def pan_right(self,e):
        self.bebop.pan_tilt_camera_velocity(pan_velocity=4, tilt_velocity=0, duration=0.00001)
    def tilt_cam_down(self, e):
        self.bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=-4, duration=0.00001)
    def tilt_cam_up(self, e):
        self.bebop.pan_tilt_camera_velocity(pan_velocity=0, tilt_velocity=4, duration=0.00001)

    def takeoff(self):
        self.bebop.safe_takeoff(5)
        self.bebop.fly_direct(pitch=0,roll=0,yaw=0,vertical_movement=20,duration=1)
    def land(self,e):
        self.bebop.safe_land(10)

    def interrupt(self,e):
        self.interrupted = True
        self.land(e)
if __name__ == '__main__':
    Keybop().start()

