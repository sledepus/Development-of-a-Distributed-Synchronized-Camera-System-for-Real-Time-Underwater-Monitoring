import asyncio
import aiohttp

JETSONS = [
    "169.254.74.178",  # Jetson A
    "169.254.60.114",  # Jetson B
]
PORT = 8080

async def send_start(session, ip):
    url = f"http://{ip}:{PORT}/start"
    try:
        async with session.post(url) as response:
            if response.status == 200:
                print(f"Start signal sent to {ip}")
            else:
                print(f"Failed to start on {ip}: HTTP {response.status}")
    except Exception as e:
        print(f"Could not reach {ip}: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [send_start(session, ip) for ip in JETSONS]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())