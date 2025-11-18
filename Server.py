import sys
sys.path.append("lib")
import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

import redis
from redis import asyncio as aioredis
from redis.client import Redis, PubSub
from fastapi import FastAPI, WebSocket, Request
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/")
def handle_pubsub():
    envelope = request.get_json()

    if not envelope or "message" not in envelope:
        return ("Invalid Pub/Sub message", 400)

    encoded_data = envelope["message"].get("data", "")
    if encoded_data:
        data = base64.b64decode(encoded_data).decode("utf-8")
        payload = json.loads(data)  # Your API request payload
        print("Received payload:", payload)

        # --- Your backend logic here ---
        # e.g. write to database, run workflow, etc.

    return ("OK", 200)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message, mode="text")

manager = ConnectionManager()

@dataclass
class ChatMessage:
    channel_id: str
    client_id: int
    time: str
    message: str


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, channel_id: str, client_id: int):
    await manager.connect(websocket)

    chat_server = ChatServer(websocket, channel_id, client_id)
    await chat_server.run()
