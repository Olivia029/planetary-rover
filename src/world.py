"""Grid world with heights: map, movement rules and BFS reference route."""
from collections import deque
from dataclasses import dataclass
from pathlib import Path

MAX_CLIMB = 1  # largest height difference the rover can climb
MAX_DROP = 2  # largest height difference the rover can descend safely
MAX_STEPS = 100  # step limit of an episode or a route

FREE, ROCK, CRATER = ".", "#", "~"
MOVES = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}  # up right down left

type Cell = tuple[int, int]


def _read_grid(path: Path) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    grid = [line.strip() for line in lines if line.strip()]
    if not grid:
        raise ValueError(f"{path}: empty file")
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError(f"{path}: rows of different length")
    return grid


@dataclass
class World:
    grid: list[str]
    heights: list[list[int]]
    rows: int
    cols: int
    places: dict[str, Cell]

    @classmethod
    def load(cls, map_path: Path, heights_path: Path) -> World:
        grid = _read_grid(map_path)
        digits = _read_grid(heights_path)
        rows, cols = len(grid), len(grid[0])
        if len(digits) != rows or len(digits[0]) != cols:
            raise ValueError("map and heights have different sizes")
        places: dict[str, Cell] = {}
        for r, row in enumerate(grid):
            for c, symbol in enumerate(row):
                if symbol in (FREE, ROCK, CRATER):
                    continue
                if not (symbol.isascii() and symbol.isupper()):
                    raise ValueError(f"unknown symbol {symbol!r} at {r, c}")
                if symbol in places:
                    raise ValueError(f"place {symbol} appears twice")
                places[symbol] = (r, c)
        if any(not ch.isdigit() for row in digits for ch in row):
            raise ValueError("heights must be digits 0-9")
        heights = [[int(ch) for ch in row] for row in digits]
        return cls(grid, heights, rows, cols, dict(sorted(places.items())))

    def inside(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def symbol(self, cell: Cell) -> str:
        r, c = cell
        return self.grid[r][c]

    def height(self, cell: Cell) -> int:
        r, c = cell
        return self.heights[r][c]

    def free_cells(self) -> list[Cell]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.grid[r][c] not in (ROCK, CRATER)]

    def move(self, cell: Cell, action: int) -> tuple[Cell, str]:
        dr, dc = MOVES[action]
        neighbor = (cell[0] + dr, cell[1] + dc)
        if not self.inside(neighbor) or self.symbol(neighbor) == ROCK:
            return cell, "blocked"  # 1. outside the map or rock
        delta = self.height(neighbor) - self.height(cell)
        if delta > MAX_CLIMB:
            return cell, "blocked"  # 2. too steep to climb
        if self.symbol(neighbor) == CRATER or delta < -MAX_DROP:
            return neighbor, "hazard"  # 3. crater or fall
        return neighbor, "moved"  # 4. normal move

    def shortest_steps(self, start: Cell, goal: Cell) -> int | None:
        distance = {start: 0}
        queue = deque([start])  # FIFO queue
        while queue:
            cell = queue.popleft()
            if cell == goal:
                return distance[cell]
            for action in MOVES:
                neighbor, outcome = self.move(cell, action)
                if outcome == "moved" and neighbor not in distance:
                    distance[neighbor] = distance[cell] + 1
                    queue.append(neighbor)
        return None


if __name__ == "__main__":
    data = Path(__file__).parent.parent / "data"
    world = World.load(data / "map.txt", data / "heights.txt")
    print(f"grid: {world.rows} rows x {world.cols} columns")
    print("places:", ", ".join(f"{k} {v}" for k, v in world.places.items()))
    free = world.free_cells()
    print(f"free cells: {len(free)}")
    pairs = unreachable = 0
    for goal in world.places.values():
        for start in free:
            if start != goal:
                pairs += 1
                if world.shortest_steps(start, goal) is None:
                    unreachable += 1
    print(f"pairs: {pairs}, unreachable: {unreachable}")
    for a, b in [("B", "A"), ("A", "B"), ("B", "M"), ("M", "B")]:
        steps = world.shortest_steps(world.places[a], world.places[b])
        print(f"{a} -> {b}: {steps} steps")
    for cell, action in [((0, 1), 1), ((0, 0), 0), ((1, 3), 1),
                         ((2, 5), 2), ((1, 4), 1)]:
        print(f"move({cell}, {action}) -> {world.move(cell, action)}")
