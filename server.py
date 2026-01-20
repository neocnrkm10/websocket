import socketio
import os
import uvicorn

sio = socketio.AsyncServer(cors_allowed_origins="*")
clients = {}

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("request_username", to=sid)

@sio.event
async def username(sid, data):
    name = data.get("name", f"User-{sid[:5]}")
    clients[sid] = name
    await sio.emit("message", {"user": "Server", "msg": f"{name} has joined the chat"})
    print(f"{name} connected (SID: {sid})")

@sio.event
async def message(sid, data):
    user = clients.get(sid, f"User-{sid[:5]}")
    msg = data.get("msg", "")
    print(f"{user}: {msg}")
    await sio.emit("message", {"user": user, "msg": msg})

@sio.event
async def disconnect(sid):
    user = clients.pop(sid, f"User-{sid[:5]}")
    print(f"{user} disconnected")
    await sio.emit("message", {"user": "Server", "msg": f"{user} has left the chat"})

# --- run uvicorn directly, no asyncio.run ---
if __name__ == "__main__":
    app = socketio.ASGIApp(sio)
    port = int(os.environ.get("PORT", 5000))
    print(f"Global Chat Server running on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)