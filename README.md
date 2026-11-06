# 3-Sided Soccer Simulation
 
An agent-based simulation of **3-sided football** (Australian version) with a Flask backend, Python script containing of deterministic rules for corners, throwins, kickoffs, goals scored and a front end consisting of HTML,CSS, and Javascript . Three teams (red, blue, green) play on one hexagonal pitch. The team that concedes the fewest goals wins.The other two teams that are not leading tend to gang up on the leader, and individual players may betray that alliance.
 
The pitch, goals, thirds and restart rules follow *3-sided football, Principles of play (Australian version)*.



## Quick start
 
Install Python 3.9+ and Flask.
 
```bash
pip install flask
python app.py
```
 
Then open <http://127.0.0.1:5000> in your browser and:
 
1. Adjust the sliders to change from 3 players to 5 players (optional) for each team.
2. Adjust the betrayal probability sliders that represent the probability of each team betraying the alliance.
2. Click **setup** to build a new match with those settings.
3. Click **go** to run the simulation, and **reset** to start over.

## Project structure
 
```
soccer_app/
├── app.py               Flask server: routes that create, step and report the match
├── soccer_engine.py     The simulation: pitch geometry, rules and player behaviour
├── templates/
│   └── index.html       The page (controls, counters, canvas, event log)
└── static/
    ├── simulation.js    Calls the server each frame and draws the match on the canvas
    └── style.css        Styling
```
 
Flask requires the folders to be named exactly `templates` and `static`.
 
## How it works
 
The browser runs the game loop. Each frame, `simulation.js` sends `POST /step`, the engine advances one tick, and the server returns the full state as JSON. The page then redraws the pitch, players, ball, counters and event log.
 
| Route | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Serves the page |
| `/state` | GET | Current state without advancing the match |
| `/setup` | POST | Rebuilds the match from the slider values |
| `/step` | POST | Advances one tick and returns the new state |
 
The server keeps one match in memory, protected by a lock, so it is a single-user tool.
 
## Controls
 
| Slider | Range | Meaning |
| --- | --- | --- |
| Number of players (red / blue / green) | 3 to 5 | Players per team |
| Betrayal threshold (red / blue / green) | 0 to 1 | How high a player's betrayal probability must be before they betray the alliance. Lower means more betrayals |
 
The counters show **goals conceded** for each team, plus the tick count. The log under the pitch lists recent goals, saves, corners, goal kicks, throw-ins and betrayals.
 
## The rules as modelled
 
**Pitch.** A regular hexagon with 23 m sides. Goals (3 m wide, 2 m deep) sit outside the pitch on three alternating sides: blue on top, green on the lower left, red on the lower right. Each team owns its goal line and the side opposite it, and holds one third of the pitch.
 
**Scoring.** A goal is the ball crossing a goal line between the posts. The team whose goal it went into concedes one point, and the fewest concessions wins. A team putting the ball into its own goal is recorded as an own goal and still concedes.
 
**Ball out of play.**
 
| Ball crosses | Put out by | Result |
| --- | --- | --- |
| A goal line | Anyone but the goal's owner | Goal kick to the owner |
| A goal line | The goal's owner | Corner to the owner of the adjacent sideline |
| A sideline | Anyone but the line's owner | Throw-in to the line's owner |
| A sideline | The line's owner | Throw-in to the team whose goal is closest |
 
After a goal, the conceding team kicks off from the centre.
 
**Alliance and betrayal.** The team with the fewest concessions is the leader. The other two teams attack the leader and may pass to each other. A non-leading player who is closer to their ally's goal than the leader's goal, and whose betrayal probability beats their team's threshold, shoots at the ally's goal instead.
 
**Not modelled yet.** Rotation of teams after each third, match timing and extra time, fouls and free kicks, penalties, substitutes, and a designated goalkeeper (saves are a probability).
 
## Tuning the behaviour
 
The constants at the top of `soccer_engine.py` control how the match feels:
 
| Constant | Effect |
| --- | --- |
| `SHOOT_RANGE`, `SHOOT_PROB` | How close a player must be to shoot and how often they do |
| `SAVE_PROB` | Chance an on-target shot is saved |
| `PASS_PROB`, `LONG_PASS_PROB` | How often players pass instead of dribbling, and how often they pass long |
| `TACKLE_PROB`, `INTERCEPT_PROB` | How often possession changes hands |
| `CLEARANCE_PROB`, `DEFLECT_PROB` | How often defenders clear the ball or deflect it out (more corners and throw-ins) |
 
## Code overview
 
`soccer_engine.py` has three classes:
 
- **`Field`**: the hexagon, goals, thirds, owned sides, and helper geometry. Hexagon sides are numbered 0 to 5, where side `i` runs from corner `c[i]` to `c[i+1]`.
- **`Player`**: builds each team's players, with random speed and betrayal probability.
- **`Team`**: the match itself. `step()` advances one tick, `get_state()` converts the match to JSON, and the out-of-play and goal logic lives in `_resolve_crossing()`.
Coordinates inside the engine are in metres with y pointing up. `get_state()` converts them to canvas pixels (400 x 400 canvas, 7.5 pixels per metre).
 
## Ideas for next steps
 
- Log matches, players and events to SQLite for analysis
- Fit a neural network to control how different teams may play with each other
