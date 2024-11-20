from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store active users and their rooms
rooms = []


@app.route('/')
def index():
    return render_template('index.html')


# WebSocket event to handle chat messages
@socketio.on('message')
def handle_message(msg):
    room = request.sid
    for user in rooms:
        if user != room:
            send(msg, room=user)


# WebSocket event for "next" action (pairing with a new user)
@socketio.on('next')
def handle_next():
    # Disconnect from current user and find a new pair
    if request.sid in rooms:
        rooms.remove(request.sid)

    # Pair with a random user (or connect if no one else is available)
    if len(rooms) > 0:
        room = random.choice(rooms)
        join_room(room)
        send("You're now chatting with a stranger", room=room)
        send("A new user has joined the chat", room=room)
    rooms.append(request.sid)
    join_room(request.sid)
    send("Looking for a stranger...", room=request.sid)


# WebSocket event to handle user disconnection
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in rooms:
        rooms.remove(request.sid)
        send("Stranger has disconnected", room=request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
