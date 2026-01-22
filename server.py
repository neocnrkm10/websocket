import os
import socketio
import uvicorn
import base64

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi", transports=["websocket"])

# {sid: {"username": str, "room": str}}
clients = {}

@sio.event
async def connect(sid, environ):
    print(f"{sid} connected")

@sio.event
async def join_room(sid, data):
    room = data.get("room")
    username = data.get("username", f"User-{sid[:5]}")

    # Register client
    clients[sid] = {"username": username, "room": room}
    await sio.enter_room(sid, room)

    await sio.emit("message", {"user": "Server", "msg": f"{username} joined the room"}, room=room)
    print(f"{username} joined room {room}")

@sio.event
async def message(sid, data):
    client = clients.get(sid)
    if not client: return

    room = client["room"]
    username = client["username"]
    msg = data.get("msg", "")
    await sio.emit("message", {"user": username, "msg": msg}, room=room)
    print(f"[{room}] {username}: {msg}")

@sio.event
async def image(sid, data):
    """
    Expects: data = {"img": base64_string}
    """
    client = clients.get(sid)
    if not client: return

    room = client["room"]
    username = client["username"]
    await sio.emit("image", {"user": username, "img": data["img"]}, room=room)
    print(f"[{room}] {username} sent an image")

@sio.event
async def voice(sid, data):
    """
    Expects: data = {"voice": base64_string}
    """
    client = clients.get(sid)
    if not client: return

    room = client["room"]
    username = client["username"]
    await sio.emit("voice", {"user": username, "voice": data["voice"]}, room=room)
    print(f"[{room}] {username} sent a voice message")

@sio.event
async def react(sid, data):
    """
    Expects: data = {"reaction": "👍"} or any emoji
    """
    client = clients.get(sid)
    if not client: return

    room = client["room"]
    username = client["username"]
    reaction = data.get("reaction", "")
    await sio.emit("reaction", {"user": username, "reaction": reaction}, room=room)
    print(f"[{room}] {username} reacted: {reaction}")

@sio.event
async def disconnect(sid):
    client = clients.pop(sid, None)
    if client:
        room = client["room"]
        username = client["username"]
        await sio.emit("message", {"user": "Server", "msg": f"{username} left the room"}, room=room)
        print(f"{username} disconnected from room {room}")
    else:
        print(f"{sid} disconnected but was not in clients")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running on http://0.0.0.0:{port}")
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=port)