import threading

from flask import Flask, render_template, jsonify, request

from soccer_engine import Team

app = Flask(__name__)

_lock = threading.Lock()
game = Team(num_red=3, num_blue=3, num_green=3)
game.spawn_player_before_kickoff()


@app.route("/")
def home():
    return render_template("index.html")

"""Return a snapshot of the current simulation without advancing it."""
@app.route("/state")
def state():
    
    with _lock:
        return jsonify(game.get_state())

"""Rebuild the simulation with the slider values from the UI."""
@app.route("/setup", methods=["POST"])
def setup():
   
    global game
    data = request.get_json(force=True, silent=True) or {}

    red_n = int(data.get("red_players", 3))
    blue_n = int(data.get("blue_players", 3))
    green_n = int(data.get("green_players", 3))

    thresholds = {
        "red": float(data.get("red_betrayal_threshold", 0.25)),
        "blue": float(data.get("blue_betrayal_threshold", 0.25)),
        "green": float(data.get("green_betrayal_threshold", 0.5)),
    }

    with _lock:
        game = Team(num_red=red_n, num_blue=blue_n, num_green=green_n, betrayal_thresholds=thresholds)
        game.spawn_player_before_kickoff()
        return jsonify(game.get_state())


@app.route("/step", methods=["POST"])
def step():
    """Advance the simulation by one tick and return the new state."""
    with _lock:
        game.step()
        return jsonify(game.get_state())


if __name__ == "__main__":
    app.run(debug=True)
