import random


class MazeGenerator:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate_maze(self):
        """Генерація лабіринту за допомогою алгоритму recursive backtracking"""
        stack = [(1, 1)]
        self.maze[1][1] = 0

        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

        while stack:
            current_x, current_y = stack[-1]
            neighbors = []

            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:
                    if self.maze[ny][nx] == 1:
                        neighbors.append((nx, ny, dx // 2, dy // 2))

            if neighbors:
                nx, ny, wall_x, wall_y = random.choice(neighbors)
                self.maze[ny][nx] = 0
                self.maze[current_y + wall_y][current_x + wall_x] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        self._add_dots_and_bonuses()
        return self.maze

    def _add_dots_and_bonuses(self):
        empty_spaces = []

        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 0:
                    empty_spaces.append((x, y))

        for x, y in empty_spaces:
            if random.random() < 0.8:
                self.maze[y][x] = 2

        if len(empty_spaces) >= 3:
            bonus_positions = random.sample(empty_spaces, 1)
            for x, y in bonus_positions:
                self.maze[y][x] = 3