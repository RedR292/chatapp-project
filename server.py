import asyncio
import websockets
from client import *
clients = set()

async def handle(ws):
    newClient = Client(ws)
    clients.add(newClient)
    # for client in clients:
    #     print(client.username)
    try:
        # print(ws)
        async for msg in ws:
            await asyncio.gather(*[
                c.send(msg) for c in [client.ws for client in clients] if c != ws
            ])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(newClient)


async def main():
    async with websockets.serve(handle, "localhost", 6789):
        print("Server running at ws://localhost:6789")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
