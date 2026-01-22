import os
import socketio
import uvicorn
import secrets

# Initialize Server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    transports=["websocket", "polling"]
)

# State Storage
rooms = {}
clients = {}

def generate_room_id():
    return secrets.token_urlsafe(4)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def join_room(sid, data):
    # Handle both creating and joining in one logic block for simplicity
    room_id = data.get("room") or generate_room_id()
    username = data.get("username", f"User-{sid[:4]}")
    
    # Register client
    clients[sid] = {"username": username, "room": room_id}
    
    # Initialize room if not exists
    if room_id not in rooms:
        rooms[room_id] = {"users": set()}
    
    rooms[room_id]["users"].add(sid)
    
    await sio.enter_room(sid, room_id)
    
    # 1. Tell the user they are in
    await sio.emit("joined_success", {"room": room_id, "username": username}, to=sid)
    
    # 2. Tell everyone else "X joined"
    await sio.emit("message", {
        "user": "Server",
        "type": "system",
        "content": f"🔵 {username} entered the chat."
    }, room=room_id)

@sio.event
async def message(sid, data):
    # Relay message to room
    if sid not in clients: return
    room = clients[sid]["room"]
    username = clients[sid]["username"]
    
    # Data is expected to be a dict: { "content": "hello", "type": "text", "replyTo": ... }
    # We construct the final payload to broadcast
    payload = {
        "user": username,
        "type": data.get("type", "text"),
        "content": data.get("content", ""),
        "replyTo": data.get("replyTo", None),
        "id": data.get("id", secrets.token_hex(4))
    }
    
    await sio.emit("message", payload, room=room)

@sio.event
async def disconnect(sid):
    if sid in clients:
        room = clients[sid]["room"]
        username = clients[sid]["username"]
        
        # Cleanup
        if room in rooms:
            rooms[room]["users"].discard(sid)
            if len(rooms[room]["users"]) == 0:
                del rooms[room]
        
        del clients[sid]
        
        # Notify room
        await sio.emit("message", {
            "user": "Server",
            "type": "system",
            "content": f"🔴 {username} left the chat."
        }, room=room)

if __name__ == "__main__":
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=5000)
