import sys
sys.path.append("lib")
# from api import *
import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List
import websockets
import redis
from redis import asyncio as aioredis
from redis.client import Redis, PubSub

import api_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

##Creates a new redis connection client
class RedisService:
    def __init__(self):
        self.redis_host = f"{os.environ.get('REDIS_HOST', 'redis://localhost')}"

    async def get_conn(self):
        return await aioredis.from_url(self.redis_host, encoding="utf-8", decode_responses=True)

##END RedisService

##Creates a new chat server instance.
class ChatServer(RedisService):
    def __init__(self, websocket, channel_id, client_id):
        super().__init__()
        self.ws: WebSocket = websocket
        self.channel_id = channel_id
        self.client_id = client_id
        self.redis = RedisService()

    ##Publish a nonempty message to memorystore via conn (a Redis connection client)
    async def publish_handler(self, conn: Redis):
        try:
            while True:
                message = await self.ws.receive_text()
                if message:
                    now = datetime.now()
                    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    chat_message = ChatMessage(
                        channel_id=self.channel_id, client_id=self.client_id, time=date_time, message=message
                    )
                    await conn.publish(self.channel_id, json.dumps(asdict(chat_message)))
                ##ENDIF
            ##ENDWHILE
        except Exception as e:
            logger.error(e)
        ##ENDTRY
    ##END publish_handler

    ##Handles subscriptions coming in from pubsub
    async def subscribe_handler(self, pubsub: PubSub):
        await pubsub.subscribe(self.channel_id)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message.get("data"))
                    chat_message = ChatMessage(**data)
                    await self.ws.send_text(f"[{chat_message.time}] {chat_message.message} ({chat_message.client_id})")
                ##ENDIF
            ##ENDWHILE
        except Exception as e:
            logger.error(e)
        ##ENDTRY
    ##END subscribe_handler

    ##Setup the connection and the pubsub at the connection edge
    async def run(self):
        conn: Redis = await self.redis.get_conn()
        pubsub: PubSub = conn.pubsub()

        ##Execute the handlers asynchronously
        tasks = [self.publish_handler(conn), self.subscribe_handler(pubsub)]
        results = await asyncio.gather(*tasks) #Executing command

        logger.info(f"Done task: {results}")
    ##END run
##END ChatServer

##Handles redis connection(s)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[websocket] = []

    ##Connects a client to the chat room
    async def connect(self, websocket: websockets):
        await websocket.accept()
        self.active_connections.append(websocket)
    ##END connect

    ##Removes a client from the chat room
    def disconnect(self, websocket: websockets):
        self.active_connections.remove(websocket)
    ##END disconnect

    ##A user sends a message to the chat room
    async def send_personal_message(self, message: str, websocket: websockets):
        await websocket.send_text(message)
    ##END send_personal_message

    ##Sends a message from the chat server to all connected recepients
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message, mode="text")
    ##END broadcast

manager = ConnectionManager()


@dataclass
class ChatMessage:
    channel_id: str
    client_id: int
    time: str
    message: str
##END ChatMessage
