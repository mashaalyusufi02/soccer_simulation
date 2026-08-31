// ===============================
// Slider wiring
// ===============================
function bindSlider(id) {
    const slider = document.getElementById(id);
    const output = slider.nextElementSibling;
    output.textContent = slider.value;
    slider.oninput = () => {
        output.textContent = slider.value;
    };
}

["red_players", "blue_players", "green_players",
 "red_betrayal_threshold", "blue_betrayal_threshold", "green_betrayal_threshold"
].forEach(bindSlider);

// ===============================
// Canvas setup
// ===============================
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let running = false;
let animationHandle = null;

let simState = {
    teams: {},
    ball: [200, 200],
    hex: [],
    goals: {},
    boundaries: {},
    concessions: { red: 0, blue: 0, green: 0 },
    tick: 0,
    last_event: null
};

// ===============================
// Networking
// ===============================
async function fetchState() {
    try {
        const res = await fetch("/state");
        simState = await res.json();
    } catch (err) {
        console.error("Error fetching state:", err);
    }
}

async function stepState() {
    try {
        const res = await fetch("/step", { method: "POST" });
        simState = await res.json();
    } catch (err) {
        console.error("Error stepping simulation:", err);
    }
}

async function setupGame() {
    const payload = {
        red_players: Number(document.getElementById("red_players").value),
        blue_players: Number(document.getElementById("blue_players").value),
        green_players: Number(document.getElementById("green_players").value),
        red_betrayal_threshold: Number(document.getElementById("red_betrayal_threshold").value),
        blue_betrayal_threshold: Number(document.getElementById("blue_betrayal_threshold").value),
        green_betrayal_threshold: Number(document.getElementById("green_betrayal_threshold").value)
    };

    const res = await fetch("/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    simState = await res.json();
}

// ===============================
// Drawing
// ===============================
function drawHexagon() {
    const hex = simState.hex;
    if (!hex || hex.length === 0) return;

    ctx.beginPath();
    ctx.moveTo(hex[0][0], hex[0][1]);
    for (let i = 1; i < hex.length; i++) ctx.lineTo(hex[i][0], hex[i][1]);
    ctx.closePath();
    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2;
    ctx.stroke();
}

function drawGoals() {
    const goals = simState.goals;
    if (!goals) return;

    const colors = {
        red_team_goal_coords: "red",
        blue_team_goal_coords: "blue",
        green_team_goal_coords: "green"
    };

    for (const key in goals) {
        const rect = goals[key];
        ctx.fillStyle = colors[key];
        ctx.beginPath();
        ctx.moveTo(rect[0][0], rect[0][1]);
        for (let i = 1; i < rect.length; i++) ctx.lineTo(rect[i][0], rect[i][1]);
        ctx.closePath();
        ctx.globalAlpha = 0.5;
        ctx.fill();
        ctx.globalAlpha = 1.0;
    }
}

function drawBoundaries() {
    const boundaries = simState.boundaries;
    if (!boundaries) return;

    ctx.strokeStyle = "#444";
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 3]);

    for (const key in boundaries) {
        const boundary = boundaries[key];
        ctx.beginPath();
        ctx.moveTo(boundary[0][0], boundary[0][1]);
        for (let i = 1; i < boundary.length; i++) ctx.lineTo(boundary[i][0], boundary[i][1]);
        ctx.closePath();
        ctx.stroke();
    }
    ctx.setLineDash([]);
}

function drawPlayers() {
    const teams = simState.teams;
    if (!teams) return;

    const colors = { red_team: "#e63946", blue_team: "#457b9d", green_team: "#2a9d8f" };

    for (const teamName in teams) {
        const team = teams[teamName];
        ctx.fillStyle = colors[teamName];

        for (const playerName in team) {
            const p = team[playerName];
            ctx.beginPath();
            ctx.arc(p.xcor, p.ycor, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#000";
            ctx.lineWidth = 1;
            ctx.stroke();

            ctx.fillStyle = "#000";
            ctx.font = "9px Arial";
            ctx.fillText(playerName.replace("Player_", "P"), p.xcor - 8, p.ycor - 11);
            ctx.fillStyle = colors[teamName];
        }
    }
}

function drawBall() {
    const ball = simState.ball;
    if (!ball) return;
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.arc(ball[0], ball[1], 5, 0, Math.PI * 2);
    ctx.fill();
}

function updateCounters() {
    document.getElementById("tick-counter").textContent = simState.tick ?? 0;
    const c = simState.concessions || { red: 0, blue: 0, green: 0 };
    document.getElementById("red-score").textContent = c.red;
    document.getElementById("blue-score").textContent = c.blue;
    document.getElementById("green-score").textContent = c.green;

    const log = document.getElementById("event-log");
    if (simState.last_event) {
        log.textContent = `tick ${simState.tick}: ${describeEvent(simState.last_event)}`;
    }
}

function describeEvent(evt) {
    switch (evt.type) {
        case "goal": return `GOAL for ${evt.detail.team}!`;
        case "throwin": return `throw-in awarded to ${evt.detail.awarded_to_team}`;
        case "goal_kick": return `goal kick awarded to ${evt.detail.team_awarded}`;
        case "corner_kick": return `corner kick awarded to ${evt.detail.team_awarded}`;
        case "betrayal": return `${evt.detail.player} betrayed their team (${evt.detail.betrayal})`;
        case "pass": return `${evt.detail.passer ?? evt.detail.player} passed to ${evt.detail.receiver}`;
        default: return "kickoff";
    }
}

function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawHexagon();
    drawGoals();
    drawBoundaries();
    drawPlayers();
    drawBall();
    updateCounters();
}

// ===============================
// Game loop
// ===============================
async function gameLoop() {
    if (!running) return;
    await stepState();
    render();
    animationHandle = requestAnimationFrame(gameLoop);
}

// ===============================
// Button handlers
// ===============================
document.querySelector(".setup-btn").onclick = async () => {
    running = false;
    if (animationHandle) cancelAnimationFrame(animationHandle);
    await setupGame();
    render();
};

document.querySelector(".go-btn").onclick = () => {
    if (running) return;
    running = true;
    gameLoop();
};

document.querySelector(".replay-btn").onclick = async () => {
    running = false;
    if (animationHandle) cancelAnimationFrame(animationHandle);
    await setupGame();
    render();
};

// Initial paint on page load
fetchState().then(render);
