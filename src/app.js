import {
  GRID_SIZE,
  TICK_MS,
  createInitialState,
  queueDirection,
  tick,
  togglePause,
  positionsEqual,
} from "./logic.js";

const board = document.querySelector("#board");
const scoreValue = document.querySelector("#score");
const statusText = document.querySelector("#status-text");
const restartButton = document.querySelector("#restart-button");
const controlButtons = Array.from(document.querySelectorAll("[data-direction]"));

let state = createInitialState();

function render() {
  scoreValue.textContent = String(state.score);
  statusText.textContent = getStatusText(state);
  board.replaceChildren(...buildCells(state));
}

function buildCells(currentState) {
  const cells = [];

  for (let y = 0; y < GRID_SIZE; y += 1) {
    for (let x = 0; x < GRID_SIZE; x += 1) {
      const cell = document.createElement("div");
      const position = { x, y };
      cell.className = "cell";

      if (positionsEqual(currentState.food, position)) {
        cell.classList.add("cell--food");
      }

      const snakeIndex = currentState.snake.findIndex((segment) => positionsEqual(segment, position));
      if (snakeIndex !== -1) {
        cell.classList.add("cell--snake");
        if (snakeIndex === 0) {
          cell.classList.add("cell--head");
        }
      }

      cells.push(cell);
    }
  }

  return cells;
}

function getStatusText(currentState) {
  if (currentState.isGameOver) {
    return "Game over. Press Restart to play again.";
  }

  if (currentState.isPaused) {
    return "Paused. Press space to resume.";
  }

  return "Use arrow keys or WASD to start.";
}

function handleDirection(direction) {
  state = queueDirection(state, direction);
  render();
}

document.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  const directionByKey = {
    arrowup: "up",
    w: "up",
    arrowdown: "down",
    s: "down",
    arrowleft: "left",
    a: "left",
    arrowright: "right",
    d: "right",
  };

  if (key === " ") {
    event.preventDefault();
    state = togglePause(state);
    render();
    return;
  }

  const direction = directionByKey[key];
  if (!direction) {
    return;
  }

  event.preventDefault();
  handleDirection(direction);
});

for (const button of controlButtons) {
  button.addEventListener("click", () => {
    handleDirection(button.dataset.direction);
  });
}

restartButton.addEventListener("click", () => {
  state = createInitialState();
  render();
});

window.setInterval(() => {
  state = tick(state);
  render();
}, TICK_MS);

render();