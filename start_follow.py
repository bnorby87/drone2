import asyncio
from follow_wild import FollowWildDrone

def main():
	wd = FollowWildDrone()
	asyncio.run(wd.goto_alarm(eps=0.3, renew=1.0))
	

if __name__ == "__main__":
	main()