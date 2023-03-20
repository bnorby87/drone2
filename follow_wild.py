import asyncio
from mavsdk import System
from gps_data import GPS_Data
import utm
import math
import rclpy

class FollowWildDrone():
	drone = System(mavsdk_server_address='localhost', port=50051)
	meteorology = True
	host = ""
	lat_home = 0
	lon_home = 0
	alt_home = 0
	gps=None
 
	def __init__(self):
		rclpy.init()
		self.gps=GPS_Data()
		
	async def default(self):
		await self.drone.connect(system_address="udp://:14550")
		print("connection ok")
  
	async def position(self):
		async for info in self.drone.telemetry.position():
			lat = info.latitude_deg
			lon = info.longitude_deg
			alt = info.absolute_altitude_m
			break
		#print(lat, lon, alt)
		return [lat, lon, alt]

	async def goto_alarm(self, eps=1.0, renew=1.0):
		if self.meteorology:
			await self.default()
			self.lat_home, self.lon_home, self.alt_home = await self.position()

			while len(self.gps.utm) < 2:
				print("waiting")
				rclpy.spin_once(self.gps)
			coord=self.gps.LatLon()

			await self.drone.action.arm()

			await self.drone.action.takeoff()
			async for flight_mode in self.drone.telemetry.flight_mode():
				print("FlightMode:", flight_mode)
				if str(flight_mode)=="HOLD":
					break
			
			#go wild
			await self.follow(lat=coord[0], lon=coord[1], eps=eps, renew=renew)
			
			#alarm
			print("ALARM!!!")
			
			await asyncio.sleep(5)

			#go home
			await self.goto_point(self.lat_home, self.lon_home, eps)

			await self.drone.action.land()
			async for is_armed in self.drone.telemetry.armed():
				print("Land, is_armed:", is_armed)
				if not is_armed:
					break
			
		else:
			print("bad weather")

	async def goto_point(self, lat, lon, eps):
		x, y, z = await self.position()
		await self.drone.action.goto_location(lat, lon, z, 0)
		dist = eps*2
		while dist > eps:
			x, y, z = await self.position()
			x1, y1 = utm.from_latlon(lat, lon)[0:2]
			x2, y2 = utm.from_latlon(x, y)[0:2]
			dist = math.sqrt((x1-x2)**2+(y1-y2)**2)
			print("Distance:",dist)

	async def follow(self, lat, lon, eps, renew):
		x, y, z = await self.position()
		await self.drone.action.goto_location(lat, lon, z, 0)
		dist = eps*2
		again = False
		while (dist > eps) and not again:
			x, y, z = await self.position()
			x1, y1 = utm.from_latlon(lat, lon)[0:2]
			x2, y2 = utm.from_latlon(x, y)[0:2]
			dist = math.sqrt((x1-x2)**2+(y1-y2)**2)
			print("Distance:",dist)
			rclpy.spin_once(self.gps, timeout_sec=0.2)
			new_coord=self.gps.LatLon()
			if math.sqrt((self.gps.utm[0]-x1)**2+(self.gps.utm[1]-y1)**2) >= renew:
				again = True
		if again:
			print("újratervezés", new_coord)
			await self.follow(lat=new_coord[0], lon=new_coord[1], eps=eps, renew=renew)
