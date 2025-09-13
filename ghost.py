import random
import math
from constants import DifficultyLevel
from path_finder import *


class Ghost:

    def __init__(self, x, y, color, ghost_id, visibility_range=5):
        self.x = x
        self.y = y
        self.color = color
        self.ghost_id = ghost_id
        self.visibility_range = visibility_range
        self.last_seen_pacman = None
        self.patrol_target = None
        self.cooperation_memory = {}
        self.stuck_counter = 0
        self.last_position = (x, y)

    def can_see_pacman(self, pacman_pos, maze):
        """Перевіряє чи може привид бачити пакмена"""
        distance = math.sqrt((self.x - pacman_pos[0]) ** 2 + (self.y - pacman_pos[1]) ** 2)
        if distance > self.visibility_range:
            return False

        # Перевіряємо лінію зору
        steps = int(distance)
        for i in range(1, steps):
            check_x = int(self.x + (pacman_pos[0] - self.x) * i / steps)
            check_y = int(self.y + (pacman_pos[1] - self.y) * i / steps)
            if maze[check_y][check_x] == 1:  # Стіна блокує зір
                return False
        return True

    def get_visible_ghosts(self, all_ghosts):
        """Отримує список видимих привидів"""
        visible = []
        for ghost in all_ghosts:
            if ghost != self:
                distance = math.sqrt((self.x - ghost.x) ** 2 + (self.y - ghost.y) ** 2)
                if distance <= self.visibility_range:
                    visible.append(ghost)
        return visible

    def predict_pacman_position(self, pacman_pos, pacman_direction):
        """Прогнозує майбутню позицію пакмена"""
        if pacman_direction:
            predicted_x = pacman_pos[0] + pacman_direction[0] * 3
            predicted_y = pacman_pos[1] + pacman_direction[1] * 3
            return (predicted_x, predicted_y)
        return pacman_pos

    def choose_intercept_position(self, pacman_pos, visible_ghosts):
        """Вибирає позицію для перехоплення на основі позицій інших привидів"""
        if not visible_ghosts:
            return pacman_pos

        # Створюємо віртуальну сітку навколо пакмена
        intercept_points = [
            (pacman_pos[0] + dx, pacman_pos[1] + dy)
            for dx in [-2, -1, 0, 1, 2]
            for dy in [-2, -1, 0, 1, 2]
            if abs(dx) + abs(dy) <= 3
        ]

        # Вибираємо точку, яка найменше покрита іншими привидами
        best_point = pacman_pos
        min_coverage = float('inf')

        for point in intercept_points:
            coverage = sum(1 for ghost in visible_ghosts
                           if math.sqrt((ghost.x - point[0]) ** 2 + (ghost.y - point[1]) ** 2) < 3)
            if coverage < min_coverage:
                min_coverage = coverage
                best_point = point

        return best_point

    def move(self, maze, pacman_pos, pacman_direction, all_ghosts, difficulty):
        """Основна логіка руху привида"""
        # Перевіряємо чи застряг
        if (self.x, self.y) == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_position = (self.x, self.y)

        visible_ghosts = self.get_visible_ghosts(all_ghosts)

        # Різні стратегії залежно від рівня складності
        if difficulty == DifficultyLevel.EASY:
            target = self._easy_strategy(maze, pacman_pos)
        elif difficulty == DifficultyLevel.MEDIUM:
            target = self._medium_strategy(maze, pacman_pos, pacman_direction, visible_ghosts)
        else:  # HARD
            target = self._hard_strategy(maze, pacman_pos, pacman_direction, visible_ghosts)

        # Рухаємось до цілі
        self._move_towards_target(maze, target)

    def _easy_strategy(self, maze, pacman_pos):
        """Проста стратегія - рухається випадково з невеликою ймовірністю йти до пакмена"""
        if self.can_see_pacman(pacman_pos, maze) and random.random() < 0.3:
            return pacman_pos

        # Випадковий рух або патрулювання
        if not self.patrol_target or random.random() < 0.1:
            self.patrol_target = self._get_random_valid_position(maze)
        return self.patrol_target

    def _medium_strategy(self, maze, pacman_pos, pacman_direction, visible_ghosts):
        """Середня стратегія - кооперація та прогнозування"""
        if self.can_see_pacman(pacman_pos, maze):
            self.last_seen_pacman = pacman_pos
            # Вибираємо позицію для перехоплення
            return self.choose_intercept_position(pacman_pos, visible_ghosts)
        elif self.last_seen_pacman:
            # Йдемо до останньої відомої позиції
            if random.random() < 0.7:
                return self.last_seen_pacman

        return self._easy_strategy(maze, pacman_pos)

    def _hard_strategy(self, maze, pacman_pos, pacman_direction, visible_ghosts):
        """Складна стратегія - повна кооперація та прогнозування"""
        if self.can_see_pacman(pacman_pos, maze):
            self.last_seen_pacman = pacman_pos
            # Прогнозуємо позицію пакмена
            predicted_pos = self.predict_pacman_position(pacman_pos, pacman_direction)
            # Координуємося з іншими привидами
            return self.choose_intercept_position(predicted_pos, visible_ghosts)
        elif self.last_seen_pacman:
            # Використовуємо A* для оптимального шляху
            return self.last_seen_pacman

        return self._medium_strategy(maze, pacman_pos, pacman_direction, visible_ghosts)

    def _get_random_valid_position(self, maze):
        """Отримує випадкову валідну позицію"""
        while True:
            x = random.randint(1, len(maze[0]) - 2)
            y = random.randint(1, len(maze) - 2)
            if maze[y][x] != 1:
                return (x, y)

    def _move_towards_target(self, maze, target):
        """Рухається до цілі використовуючи A*"""
        if self.stuck_counter > 5:  # Якщо застряг, рухається випадково
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and
                        maze[new_y][new_x] != 1):
                    self.x, self.y = new_x, new_y
                    return

        path = PathFinder.astar(maze, (self.x, self.y), target)
        if path and len(path) > 0:
            self.x, self.y = path[0]