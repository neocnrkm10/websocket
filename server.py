# server.py
import socketio
import eventlet
import threading
import random
import time
import os

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Demo data for testing
votes = {"A": 0, "B": 0}

# Function to simulate live updates every second
def update_data():
    while True:
        votes["A"] += random.randint(0, 2)
        votes["B"] += random.randint(0, 2)
        sio.emit("vote_update", votes)
        time.sleep(1)

# Socket.IO events
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")
    sio.emit("vote_update", votes, room=sid)

@sio.event
def vote(sid, data):
    candidate = data.get("candidate")
    if candidate in votes:
        votes[candidate] += 1
        sio.emit("vote_update", votes)

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

if __name__ == "__main__":
    # Run the simulation thread
    threading.Thread(target=update_data, daemon=True).start()
    print("Standalone Socket.IO server running...")

    # Get port from Render environment variable
    PORT = int(os.environ.get("PORT", 5000))
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)