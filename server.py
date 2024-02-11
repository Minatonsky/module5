import json
import logging
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from datetime import datetime
from aiopath import AsyncPath
from aiofile import AIOFile
import names
from currency_exchange import CurrencyExchange 


class Server:
    log_path = AsyncPath('server_log.txt')
    clients = set()

    def __init__(self, max_days=10):
        self.max_days = max_days
        self.exchange_handler = CurrencyExchange(max_days=max_days)

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def handle_command(self, ws, message):
        command = message.get('command')
        if command == 'exchange':
            await self.exchange_handler.execute(self, ws, message.get('args', {}).get('days', 1), message.get('args', {}).get('currencies', ['USD', 'EUR']))
            async with AIOFile(self.log_path, 'a') as log_file:
                await log_file.write(f"{datetime.now()} - {ws.name} executed 'exchange' command.\n")
        elif command == 'message':
            await self.distribute(ws, message['text'])
        else:
            logging.warning(f"Unknown command: {command}")

    async def ws_handler(self, ws: WebSocketServerProtocol, path):
        await self.register(ws)
        try:
            async for message in ws:
                message = json.loads(message)
                if 'command' in message:
                    await self.handle_command(ws, message)
                else:
                    await self.distribute(ws, message)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol, message: str):
        await self.send_to_clients(f"{ws.name}: {message} ** Please type 'exchange' to get currency rates or type "
                                   f"'exchange 2' to get currency rates for the last two days.")