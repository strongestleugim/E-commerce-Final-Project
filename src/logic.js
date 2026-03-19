export const GRID_SIZE = 16;
export const INITIAL_DIRECTION = "right";
export const TICK_MS = 140;

const DIRECTION_VECTORS = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const OPPOSITES = {
  up: "down",
  down: "up",
  left: "right",
  right: "left",
};

export function createInitialState(random = Math.random, gridSize = GRID_SIZE) {
  const mid = Math.floor(gridSize / 2);
  const snake = [
    { x: mid, y: mid },
    { x: mid - 1, y: mid },
    { x: mid - 2, y: mid },
  ];

  return {
    gridSize,
    snake,
    direction: INITIAL_DIRECTION,
    queuedDirection: INITIAL_DIRECTION,
    food: placeFood(snake, gridSize, random),
    score: 0,
    isGameOver: false,
    isPaused: false,
  };
}

export function queueDirection(state, nextDirection) {
  if (!DIRECTION_VECTORS[nextDirection]) {
    return state;
  }

  const current = state.direction;
  const queued = state.queuedDirection;

  if (nextDirection === current || nextDirection === queued) {
    return state;
  }

  if (OPPOSITES[current] === nextDirection) {
    return state;
  }

  return { ...state, queuedDirection: nextDirection };
}

export function togglePause(state) {
  if (state.isGameOver) {
    return state;
  }

  return { ...state, isPaused: !state.isPaused };
}

export function tick(state, random = Math.random) {
  if (state.isGameOver || state.isPaused) {
    return state;
  }

  const direction = state.queuedDirection;
  const vector = DIRECTION_VECTORS[direction];
  const nextHead = {
    x: state.snake[0].x + vector.x,
    y: state.snake[0].y + vector.y,
  };

  const willEat = positionsEqual(nextHead, state.food);
  const nextSnake = [nextHead, ...state.snake];

  if (!willEat) {
    nextSnake.pop();
  }

  if (hitsWall(nextHead, state.gridSize) || hitsSelf(nextHead, nextSnake.slice(1))) {
    return {
      ...state,
      direction,
      queuedDirection: direction,
      isGameOver: true,
    };
  }

  return {
    ...state,
    snake: nextSnake,
    direction,
    queuedDirection: direction,
    food: willEat ? placeFood(nextSnake, state.gridSize, random) : state.food,
    score: willEat ? state.score + 1 : state.score,
  };
}

export function placeFood(snake, gridSize, random = Math.random) {
  const occupied = new Set(snake.map(toKey));
  const available = [];

  for (let y = 0; y < gridSize; y += 1) {
    for (let x = 0; x < gridSize; x += 1) {
      const key = toKey({ x, y });
      if (!occupied.has(key)) {
        available.push({ x, y });
      }
    }
  }

  if (available.length === 0) {
    return null;
  }

  const index = Math.floor(random() * available.length);
  return available[index];
}

export function positionsEqual(a, b) {
  return Boolean(a && b) && a.x === b.x && a.y === b.y;
}

export function hitsWall(position, gridSize) {
  return (
    position.x < 0 ||
    position.y < 0 ||
    position.x >= gridSize ||
    position.y >= gridSize
  );
}

export function hitsSelf(head, body) {
  return body.some((segment) => positionsEqual(segment, head));
}

function toKey(position) {
  return `${position.x},${position.y}`;
}