import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


class GPS(Node):
	lat = 0.0
	lon = 0.0

	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon
		super().__init__('gps')
		self.publisher_ = self.create_publisher(NavSatFix, '/detection_coordinates', 10)
		timer_period = 0.5
		self.timer = self.create_timer(timer_period, self.gps_callback)

	def gps_callback(self):
		msg = NavSatFix()
		msg.latitude = self.lat
		msg.longitude = self.lon
		self.publisher_.publish(msg)
		print(msg)


def main():
	rclpy.init()
	gps=GPS(lat = 47.694975899999996, lon = 17.6239836)
	rclpy.spin(gps)
	gps.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()

