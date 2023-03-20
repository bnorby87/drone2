import asyncio
from wilddrone import WildDrone
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
import utm

class GPS_Data(Node):
	goal = NavSatFix()
	ok = False

	def __init__(self):
		super().__init__('GPS_DATA')
		self.subscription = self.create_subscription(NavSatFix, '/detection_coordinates', self.gps_callback, 10)
	
	def gps_callback(self, msg):
		print(msg.latitude, msg.longitude)
		self.ok = True
		self.goal = msg


def main():
	rclpy.init()
	gps=GPS_Data()
	while not gps.ok:
		print("waiting")
		rclpy.spin_once(gps)

	wd = WildDrone()
	asyncio.run(wd.goto_alarm(lat=gps.goal.latitude, lon=gps.goal.longitude, eps=0.1))
	
def main_fix_latlon():
	wd = WildDrone()
	asyncio.run(wd.goto_alarm(lat=47.694975899999996, lon=17.6239836, eps=0.1))

def main_fix_utm():
	wd = WildDrone()
	latlon = utm.to_latlon(696870.7343931361, 5285739.346658029, 33, 'T')
	asyncio.run(wd.goto_alarm(latlon[0], latlon[1], eps=0.1))

if __name__ == "__main__":
	main()