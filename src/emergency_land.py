from pyparrot.Bebop import Bebop

bebop = Bebop()

success = bebop.connect(10)
print("success!")
if success:
    print("landing")
    bebop.safe_land(10)
    bebop.smart_sleep(1)
    print("disconnecting")
    bebop.disconnect()