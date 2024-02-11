import asyncio
import websockets
import argparse
from server import Server


async def main():
    parser = argparse.ArgumentParser(description='WebSocket Server with Currency Exchange and Messaging')
    parser.add_argument('--port', type=int, default=8080, help='Port for WebSocket server')
    parser.add_argument('--days', type=int, default=10, help='Number of days for currency exchange rates (maximum 10 days)')
    args = parser.parse_args()

    max_days = max(1, min(args.days, 10))

    server = Server(max_days=max_days)
    async with websockets.serve(server.ws_handler, 'localhost', args.port):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
