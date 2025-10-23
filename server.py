import asyncio
import websockets
from client import *
clients = set()
sockets = dict()
##TODO: Save new clients to db
##TODO: Pass client object to html. Javascript? Xml?

async def handle(ws):
    newClient = Client()
    clients.add(Client())
    sockets[ws] = newClient.ID
    try:
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
