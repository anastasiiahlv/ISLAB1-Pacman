import random


class MazeGenerator:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate_maze(self):
        """Генерує лабіринт використовуючи алгоритм recursive backtracking"""
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

        # Додаємо точки та бонуси
        self._add_dots_and_bonuses()
        return self.maze

    def _add_dots_and_bonuses(self):
        """Додає точки та бонуси в лабіринт"""
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 0:
                    if random.random() < 0.8:  # 80% шанс на звичайну точку
                        self.maze[y][x] = 2
                    elif random.random() < 0.05:  # 5% шанс на бонус
                        self.maze[y][x] = 3