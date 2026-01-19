# server.py
import socketio
import eventlet
import threading
import random
import time

# Create Socket.IO server
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Some demo data
votes = {"A": 0, "B": 0}

# Function to simulate data changes every second
def update_data():
    while True:
        # Randomly increase votes
        votes["A"] += random.randint(0, 2)
        votes["B"] += random.randint(0, 2)
        # Push updated data to all connected clients
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
    # Run the simulation in a separate thread
    threading.Thread(target=update_data, daemon=True).start()
    print("Standalone Socket.IO server running on port 5000")
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
