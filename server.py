# Flask API that exposes HTTP endpoints for MusicPlayer.py back-end. 

from flask import Flask, jsonify, request, send_from_directory
import os
from music_player import MusicPlayer 

app = Flask(__name__, static_folder="public", static_url_path="")

player = MusicPlayer()

@app.route("/")
def index():
    return send_from_directory("public", "index.html")

@app.route("/api/playlists", methods=["GET"])
def playlists():
    return jsonify(player.get_playlist())

@app.route("/api/play", methods=["POST"])
def play():
    data = request.get_json() or {}
    playlist_id = str(data.get("playlist_id", "1"))
    try:
        state = player.start_playing(playlist_id)
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/api/state", methods=["GET"])
def state():
    return jsonify(player.get_state())

@app.route("/api/toggle", methods=["POST"])
def toggle_play():
    state = player.play_or_pause()
    return jsonify(state)

@app.route("/api/skip", methods=["POST"])
def skip_song():
    data = request.get_json() or {}
    early = bool(data.get("early", False))
    state = player.skip(early=early)
    return jsonify(state)

@app.route("/api/shuffle", methods=["POST"])
def shuffle_queue():
    state = player.smart_shuffle()
    return jsonify(state)

@app.route("/api/add", methods=["POST"])
def add_song():
    data = request.get_json() or {}
    queue_song = int(data.get("queue_song"))
    if not queue_song:
        return jsonify({"error": "song id required"}), 400
    try:
        state = player.add_to_queue(queue_song)
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/remove", methods=["POST"])  
def remove_song():
    data = request.get_json() or {}
    dequeue_song = int(data.get("dequeue_song"))
    if not dequeue_song:
        return jsonify({"error": "song id required"}), 400
    try:
        state = player.remove_from_queue(dequeue_song)
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)