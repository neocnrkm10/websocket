import asyncio
import websockets
import random
import json

clients = set()
votes = {"A": 0, "B": 0}

async def handler(websocket):
    clients.add(websocket)
    try:
        await websocket.send(json.dumps(votes))  # send initial data
        async for message in websocket:
            data = json.loads(message)
            candidate = data.get("candidate")
            if candidate in votes:
                votes[candidate] += 1
                # Broadcast to all clients
                websockets.broadcast(clients, json.dumps(votes))
    finally:
        clients.remove(websocket)

async def update_votes():
    while True:
        votes["A"] += random.randint(0, 2)
        votes["B"] += random.randint(0, 2)
        if clients:
            websockets.broadcast(clients, json.dumps(votes))
        await asyncio.sleep(1)

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 5000)
    await update_votes()  # runs forever

asyncio.run(main())