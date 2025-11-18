from redis.client import Redis, PubSub
import redis
from redis import asyncio as aioredis
import os
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_host = f"{os.environ.get('REDIS_HOST', '10.12.196.163')}"
        self.redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}"

    async def get_conn(self):
        return await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True, port=self.redis_port)


class ChatServer(RedisService):
    def __init__(self, websocket, channel_id, client_id):
        super().__init__()
        self.ws: WebSocket = websocket
        self.channel_id = channel_id
        self.client_id = client_id

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
                    logger.info(f"Publishing: {chat_message}")
        except Exception as e:
            logger.error(e)

    async def subscribe_handler(self, pubsub: PubSub):
        await pubsub.subscribe(self.channel_id)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                await asyncio.sleep(0.01)
                if message:
                    data = json.loads(message.get("data"))
                    chat_message = ChatMessage(**data)
                    await self.ws.send_text(f"[{chat_message.time}] {chat_message.message} ({chat_message.client_id})")
                    logger.info(f"Received from Redis: {chat_message}")
                    await asyncio.sleep(0.01)

        except Exception as e:
            logger.error(e)

    async def run(self):
        conn: Redis = await self.get_conn()
        pubsub: PubSub = conn.pubsub()

        tasks = [self.publish_handler(conn), self.subscribe_handler(pubsub)]
        results = await asyncio.gather(*tasks)

        logger.info(f"Done task: {results}")

@dataclass
class ChatMessage:
    channel_id: str
    client_id: int
    time: str
    message: str
