const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const statusEl = document.getElementById("status");
const modal = document.getElementById("gameOverModal");
const restartBtn = document.getElementById("restartBtn");

let gameState = null;

canvas.focus();

const WORLD_WIDTH = 1280;
const WORLD_HEIGHT = 720;

const WS = {
  socket: null,
  connected: false,
  reconnectTimer: null,
};

function connect() {
  if (WS.socket && WS.socket.readyState === WebSocket.OPEN) return;

  WS.socket = new WebSocket("ws://localhost:8000");

  WS.socket.onopen = () => {
    WS.connected = true;
    statusEl.textContent = "Connected";
    clearTimeout(WS.reconnectTimer);
  };

  WS.socket.onclose = () => {
    WS.connected = false;
    statusEl.textContent = "Disconnected";
    WS.reconnectTimer = setTimeout(connect, 2000);
  };

  WS.socket.onmessage = (e) => {
    handleMessage({ data: e.data });
  };
}

function handleMessage(event) {
  const msg = JSON.parse(event.data);

  if (msg.type === "state") {
    gameState = msg.data;

    if (msg.phase === "game_over") {
      modal.style.display = "block";
    } else {
      modal.style.display = "none";
    }
  }
}

function send(type, payload = {}) {
  if (!WS.socket || WS.socket.readyState !== WebSocket.OPEN) return;
  WS.socket.send(JSON.stringify({ type, ...payload }));
}

window.addEventListener("keydown", (e) => {
  e.preventDefault();

  if (modal.style.display === "block") {
    if (e.key === "Enter") {
      modal.style.display = "none";
      send("restart");
    }
    return;
  }

  send("input", { key: e.key });
});

window.addEventListener("keyup", (e) => {
  e.preventDefault();

  if (modal.style.display === "block") return;

  send("input_release", { key: e.key });
});

restartBtn.addEventListener("click", () => {
  modal.style.display = "none";
  send("restart");
});

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();

function applyCameraTransform() {
  const scale = Math.max(
    canvas.width / WORLD_WIDTH,
    canvas.height / WORLD_HEIGHT
  );

  const offsetX = (canvas.width - WORLD_WIDTH * scale) / 2;
  const offsetY = (canvas.height - WORLD_HEIGHT * scale) / 2;

  ctx.setTransform(scale, 0, 0, scale, offsetX, offsetY);
}

function render() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (gameState) {
    applyCameraTransform();

    const [px, py, rotation] = gameState.player;

    ctx.strokeStyle = "white";
    ctx.save();
    ctx.translate(px, py);
    ctx.rotate((rotation * Math.PI) / 180);

    const size = 12;
    ctx.beginPath();
    ctx.moveTo(0, -size);
    ctx.lineTo(-size, size);
    ctx.lineTo(size, size);
    ctx.closePath();
    ctx.stroke();

    ctx.restore();

    ctx.strokeStyle = "gray";
    for (const [x, y, r] of gameState.asteroids) {
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.stroke();
    }

    ctx.fillStyle = "white";
    for (const [x, y] of gameState.shots) {
      ctx.fillRect(x - 2, y - 2, 4, 4);
    }
  }

  requestAnimationFrame(render);
}

connect();
render();
