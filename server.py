 import os
import socketio
import uvicorn
import secrets

sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    transports=["websocket"]
)

# Stores all active rooms
rooms = {}

# Stores all clients
clients = {}

# Helper to generate unique room IDs
def generate_room_id():
    return secrets.token_urlsafe(5)  # short random string

# Create a new room
@sio.event
async def create_room(sid, data):
    username = data.get("username", f"User-{sid[:5]}")
    room_id = generate_room_id()
    rooms[room_id] = {"users": set(), "messages": []}  # ephemeral storage
    clients[sid] = {"username": username, "room": room_id}
    rooms[room_id]["users"].add(sid)
    await sio.enter_room(sid, room_id)
    await sio.emit("room_created", {"room_id": room_id}, to=sid)
    await sio.emit("message", {"user": "Server", "msg": f"{username} has joined the room"}, room=room_id)

# Join existing room
@sio.event
async def join_room(sid, data):
    room_id = data.get("room_id")
    username = data.get("username", f"User-{sid[:5]}")
    
    if room_id not in rooms:
        await sio.emit("error", {"msg": "Room not found"}, to=sid)
        return
    
    clients[sid] = {"username": username, "room": room_id}
    rooms[room_id]["users"].add(sid)
    await sio.enter_room(sid, room_id)
    await sio.emit("message", {"user": "Server", "msg": f"{username} has joined the room"}, room=room_id)

# Send message
@sio.event
async def message(sid, data):
    msg = data.get("msg", "")
    room = clients[sid]["room"]
    user = clients[sid]["username"]
    await sio.emit("message", {"user": user, "msg": msg}, room=room)

# Send image or voice as base64
@sio.event
async def media(sid, data):
    room = clients[sid]["room"]
    user = clients[sid]["username"]
    await sio.emit("media", {"user": user, "type": data["type"], "data": data["data"]}, room=room)

# React to messages
@sio.event
async def react(sid, data):
    room = clients[sid]["room"]
    await sio.emit("react", data, room=room)  # data should contain msg id and reaction type

# Disconnect
@sio.event
async def disconnect(sid):
    if sid in clients:
        room = clients[sid]["room"]
        username = clients[sid]["username"]
        rooms[room]["users"].discard(sid)
        await sio.emit("message", {"user": "Server", "msg": f"{username} left the room"}, room=room)
        await sio.leave_room(sid, room)
        del clients[sid]
        # Delete room if empty
        if len(rooms[room]["users"]) == 0:
            del rooms[room]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = socketio.ASGIApp(sio)
    print(f"Temp Chat Server running on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)