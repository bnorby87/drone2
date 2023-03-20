import asyncio
from mavsdk import System
import utm
import math

class WildDrone():
	#drone = System(mavsdk_server_address='10.4.70.182', port=50051)
	#drone = System(mavsdk_server_address='192.168.33.60', port=50051)
	meteorology = True
	host = ""
	lat_home = 0
	lon_home = 0
	alt_home = 0
	
	def __init__(self):
		None
		
	async def default(self):
		await self.drone.connect(system_address="udp://:14540")
		print("connection ok")
		self.lat_home, self.lon_home, self.alt_home = await self.position()
  
	async def position(self):
		async for info in self.drone.telemetry.position():
			lat = info.latitude_deg
			lon = info.longitude_deg
			alt = info.absolute_altitude_m
			break
		print(lat, lon, alt)
		return [lat, lon, alt]

	async def goto_alarm(self, lat, lon, eps):
		if self.meteorology:
			await self.default()
			await self.drone.action.arm()
			
			await self.drone.action.takeoff()
			async for flight_mode in self.drone.telemetry.flight_mode():
				print("FlightMode:", flight_mode)
				if str(flight_mode)=="HOLD":
					break
			
			#go wild
			await self.goto_point(lat, lon, eps)
			
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

	async def goto_point(self, lat, lon, eps=0.3):
		x, y, z = await self.position()
		await self.drone.action.goto_location(lat, lon, z, 0)
		dist = eps*2
		while dist > eps:
			x, y, z = await self.position()
			x1, y1 = utm.from_latlon(lat, lon)[0:2]
			x2, y2 = utm.from_latlon(x, y)[0:2]
			dist = math.sqrt((x1-x2)**2+(y1-y2)**2)
			print("Distance:",dist)