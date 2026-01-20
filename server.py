import socketio
import asyncio
import os

# 1️⃣ Create Async Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="*")

# 2️⃣ Track connected users
clients = {}  # key: sid, value: username

# 3️⃣ When a client connects
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Ask client for username
    await sio.emit("request_username", to=sid)

# 4️⃣ When client sends username
@sio.event
async def username(sid, data):
    name = data.get("name", f"User-{sid[:5]}")  # default username
    clients[sid] = name
    # Notify all clients
    await sio.emit("message", {"user": "Server", "msg": f"{name} has joined the chat"})
    print(f"{name} connected (SID: {sid})")

# 5️⃣ When client sends a chat message
@sio.event
async def message(sid, data):
    user = clients.get(sid, f"User-{sid[:5]}")
    msg = data.get("msg", "")
    print(f"{user}: {msg}")
    # Broadcast message to all connected clients
    await sio.emit("message", {"user": user, "msg": msg})

# 6️⃣ When client disconnects
@sio.event
async def disconnect(sid):
    user = clients.pop(sid, f"User-{sid[:5]}")
    print(f"{user} disconnected")
    await sio.emit("message", {"user": "Server", "msg": f"{user} has left the chat"})

# 7️⃣ Start the ASGI server with uvicorn
async def main():
    app = socketio.ASGIApp(sio)
    port = int(os.environ.get("PORT", 5000))  # For deployment platforms
    print(f"Global Chat Server running on http://0.0.0.0:{port}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

# 8️⃣ Run the server
asyncio.run(main())