import asyncio
import json
import time

import websockets

PORT = 5678
HOST = '127.0.0.1'

clients = {}

def encode(data):
    data['timestamp'] = time.time()
    return json.dumps(data)

def decode_from_client(message):
    return json.loads(message)

def get_username(client):
    for name, _client in clients.items():
        if _client is client:
            return name

async def send(client, data):
    encoded = encode(data)
    await client.send(encoded)

async def register(client, name):
    clients[name] = client
    await publish(what='connected', username=name)

async def publish(**data):
    if len(clients) > 0:
        await asyncio.wait([send(client, data) for client in clients.values()])

async def serve(client, path):
    # Wait for connection
    while True:
        message = await client.recv()
        data = decode_from_client(message)
        if 'username' in data:
            await register(client, name=data['username'])
            break

    # Wait for message
    while True:
        message = await client.recv()
        data = decode_from_client(message)
        if 'message' in data:
            await publish(what='new_message', message=data['message'], username=get_username(client))

start_server = websockets.serve(serve, HOST, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
