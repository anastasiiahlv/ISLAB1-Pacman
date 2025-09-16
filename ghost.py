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
        self.memory_decay = 0
        self.patrol_points = []
        self.current_patrol_index = 0
        self.role = "hunter"  # hunter, blocker, ambusher

        self.position_history = [(x, y)] * 5
        self.stuck_counter = 0
        self.escape_mode = False
        self.escape_timer = 0

        self.team_target = None
        self.coordination_timer = 0

    def can_see_pacman(self, pacman_pos, maze):
        distance = math.sqrt((self.x - pacman_pos[0]) ** 2 + (self.y - pacman_pos[1]) ** 2)
        if distance > self.visibility_range:
            return False

        steps = max(int(distance * 2), 1)
        for i in range(1, steps):
            t = i / steps
            check_x = int(self.x + (pacman_pos[0] - self.x) * t + 0.5)
            check_y = int(self.y + (pacman_pos[1] - self.y) * t + 0.5)

            if (check_y < 0 or check_y >= len(maze) or
                    check_x < 0 or check_x >= len(maze[0]) or
                    maze[check_y][check_x] == 1):
                return False
        return True

    def get_visible_ghosts(self, all_ghosts):
        visible = []
        for ghost in all_ghosts:
            if ghost != self:
                distance = math.sqrt((self.x - ghost.x) ** 2 + (self.y - ghost.y) ** 2)
                if distance <= self.visibility_range:
                    visible.append({
                        'ghost': ghost,
                        'distance': distance,
                        'position': (ghost.x, ghost.y),
                        'role': ghost.role
                    })  # Отримуємо список словників
        return visible

    def predict_pacman_position(self, pacman_pos, pacman_direction, steps_ahead=3):
        if not pacman_direction:
            return pacman_pos

        predicted_positions = [pacman_pos]
        current_pos = pacman_pos

        for step in range(1, steps_ahead + 1):
            next_x = current_pos[0] + pacman_direction[0]
            next_y = current_pos[1] + pacman_direction[1]

            # Перевірка на валідність клітинки (щоб була не стіна і не за межами)
            if (0 <= next_x < len(self.maze[0]) and 0 <= next_y < len(self.maze) and
                    self.maze[next_y][next_x] != 1):
                current_pos = (next_x, next_y)
                predicted_positions.append(current_pos)
            else:
                break

        return predicted_positions[-1]

    # Для розрахунку позицій для перехоплення
    def calculate_intercept_positions(self, pacman_pos, visible_ghosts):
        # Сітка навколо пакмана - потенційні позиції для перехоплення
        intercept_grid = []
        for radius in range(1, 4):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) == radius:
                        pos = (pacman_pos[0] + dx, pacman_pos[1] + dy)
                        intercept_grid.append(pos)

        best_positions = []
        for pos in intercept_grid:
            if self._is_valid_position(pos):
                coverage = self._calculate_position_coverage(pos, visible_ghosts)
                distance_to_me = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)

                score = -coverage * 10 - distance_to_me  # Менше покриття і ближче = краще
                best_positions.append((pos, score))

        if best_positions:
            best_positions.sort(key=lambda x: x[1], reverse=True)
            return best_positions[0][0]

        return pacman_pos

    def _is_valid_position(self, pos):
        x, y = pos
        if (0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze)):
            return self.maze[y][x] != 1
        return False

    def _calculate_position_coverage(self, pos, visible_ghosts):
        coverage = 0
        for ghost_info in visible_ghosts:
            ghost_pos = ghost_info['position']
            distance = math.sqrt((pos[0] - ghost_pos[0]) ** 2 + (pos[1] - ghost_pos[1]) ** 2)
            if distance < 2:
                coverage += 1
        return coverage

    # Динамічне призначання ролей на основі ситуації
    def assign_role_based_on_situation(self, pacman_pos, visible_ghosts):
        if not visible_ghosts:
            self.role = "hunter"
            return

        my_distance = math.sqrt((self.x - pacman_pos[0]) ** 2 + (self.y - pacman_pos[1]) ** 2)

        closest_distance = min(ghost['distance'] for ghost in visible_ghosts
                               if math.sqrt((ghost['ghost'].x - pacman_pos[0]) ** 2 +
                                            (ghost['ghost'].y - pacman_pos[1]) ** 2) < 100)

        if my_distance <= closest_distance + 0.5:
            self.role = "hunter"
        else:
            if len(visible_ghosts) >= 2 and random.random() < 0.6:
                self.role = "blocker"
            else:
                self.role = "ambusher"

    def generate_patrol_points(self, maze):
        if not self.patrol_points or random.random() < 0.1:
            self.patrol_points = []
            attempts = 0
            while len(self.patrol_points) < 4 and attempts < 50:
                x = random.randint(1, len(maze[0]) - 2)
                y = random.randint(1, len(maze) - 2)
                if maze[y][x] != 1:
                    too_close = False
                    for px, py in self.patrol_points:
                        if abs(x - px) + abs(y - py) < 5:
                            too_close = True
                            break
                    if not too_close:
                        self.patrol_points.append((x, y))
                attempts += 1

    # Для вирішення проблеми із застряганням привида на одному місці
    def update_position_history(self):
        self.position_history.append((self.x, self.y))
        if len(self.position_history) > 8:
            self.position_history.pop(0)

        if len(set(self.position_history[-4:])) <= 2:
            self.stuck_counter += 1
        else:
            self.stuck_counter = max(0, self.stuck_counter - 1)

        if self.stuck_counter >= 3:
            self.escape_mode = True
            self.escape_timer = 10

    # Рух для виходу із застрягання
    def _escape_move(self, maze):
        possible_moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            new_x, new_y = self.x + dx, self.y + dy
            if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and
                    maze[new_y][new_x] != 1):

                if (new_x, new_y) not in self.position_history[-3:]:
                    possible_moves.append((new_x, new_y))

        if possible_moves:
            farthest = max(possible_moves,
                           key=lambda p: abs(p[0] - self.x) + abs(p[1] - self.y))
            self.x, self.y = farthest

    def move(self, maze, pacman_pos, pacman_direction, all_ghosts, difficulty):
        self.maze = maze

        self.update_position_history()

        # Обробка режиму втечі із застрягання
        if self.escape_mode:
            self.escape_timer -= 1
            if self.escape_timer <= 0:
                self.escape_mode = False
                self.stuck_counter = 0
            else:
                return self._escape_move(maze)

        visible_ghosts = self.get_visible_ghosts(all_ghosts)

        if difficulty == DifficultyLevel.EASY:
            target = self._easy_strategy(maze, pacman_pos)
        elif difficulty == DifficultyLevel.MEDIUM:
            target = self._medium_strategy(maze, pacman_pos, pacman_direction, visible_ghosts)
        else:
            target = self._hard_strategy(maze, pacman_pos, pacman_direction, visible_ghosts)

        self._move_towards_target(maze, target)

    # Легкий рівень: основний рух - випадкове патрулювання, іноді переслідує пакмана, коли бачить його
    def _easy_strategy(self, maze, pacman_pos):
        if self.can_see_pacman(pacman_pos, maze) and random.random() < 0.7:
            return pacman_pos

        self.generate_patrol_points(maze)
        if self.patrol_points:
            if self.current_patrol_index >= len(self.patrol_points):
                self.current_patrol_index = 0

            target = self.patrol_points[self.current_patrol_index]
            if abs(self.x - target[0]) < 1 and abs(self.y - target[1]) < 1:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

            return target

        return self.x, self.y

    # Середній рівень: + пам'ять про останню позицію пакмана та кооперація
    def _medium_strategy(self, maze, pacman_pos, pacman_direction, visible_ghosts):
        if self.can_see_pacman(pacman_pos, maze):
            self.last_seen_pacman = pacman_pos
            self.memory_decay = 0
            return self.calculate_intercept_positions(pacman_pos, visible_ghosts)

            '''if random.random() < 0.7:
                return self.calculate_intercept_positions(pacman_pos, visible_ghosts)'''

        elif self.last_seen_pacman and self.memory_decay < 15:
            self.memory_decay += 1

            if abs(self.x - self.last_seen_pacman[0]) < 1 and abs(self.y - self.last_seen_pacman[1]) < 1:
                self.last_seen_pacman = None
                self.memory_decay = 0
            else:
                return self.last_seen_pacman

        else:
            self.last_seen_pacman = None
            self.memory_decay = 0

        self.generate_patrol_points(maze)
        if self.patrol_points:
            if self.current_patrol_index >= len(self.patrol_points):
                self.current_patrol_index = 0

            target = self.patrol_points[self.current_patrol_index]
            if abs(self.x - target[0]) < 1 and abs(self.y - target[1]) < 1:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

            return target

        return (self.x, self.y)

    def _hard_strategy(self, maze, pacman_pos, pacman_direction, visible_ghosts):
        if self.can_see_pacman(pacman_pos, maze):
            self.assign_role_based_on_situation(pacman_pos, visible_ghosts)
            self.last_seen_pacman = pacman_pos
            self.memory_decay = 0

            if self.role == "hunter":
                # Прямий переслідувач
                predicted_pos = self.predict_pacman_position(pacman_pos, pacman_direction)
                return predicted_pos

            elif self.role == "blocker":
                # Блокує шляхи втечі
                escape_routes = self._find_pacman_escape_routes(maze, pacman_pos)
                if escape_routes:
                    return min(escape_routes,
                               key=lambda p: math.sqrt((p[0] - self.x) ** 2 + (p[1] - self.y) ** 2))

            elif self.role == "ambusher":
                # Йде на довшу дистанцію вперед
                predicted_pos = self.predict_pacman_position(pacman_pos, pacman_direction, 5)
                return predicted_pos

        elif self.last_seen_pacman and self.memory_decay < 25:
            self.memory_decay += 1

            if abs(self.x - self.last_seen_pacman[0]) < 1 and abs(self.y - self.last_seen_pacman[1]) < 1:
                # Розширюємо пошук навколо останньої позиції
                search_area = []
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        if abs(dx) + abs(dy) <= 3:
                            pos = (self.last_seen_pacman[0] + dx, self.last_seen_pacman[1] + dy)
                            if self._is_valid_position(pos):
                                search_area.append(pos)

                if search_area:
                    return random.choice(search_area)
                else:
                    self.last_seen_pacman = None
            else:
                return self.last_seen_pacman

        return self._intelligent_patrol(maze, pacman_pos, visible_ghosts)

    def _find_pacman_escape_routes(self, maze, pacman_pos):
        escape_routes = []
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            escape_x = pacman_pos[0] + dx
            escape_y = pacman_pos[1] + dy

            if self._is_valid_position((escape_x, escape_y)):
                path_clear = True
                steps = max(abs(dx), abs(dy))
                for step in range(1, steps + 1):
                    check_x = pacman_pos[0] + (dx * step // steps)
                    check_y = pacman_pos[1] + (dy * step // steps)
                    if not self._is_valid_position((check_x, check_y)):
                        path_clear = False
                        break

                if path_clear:
                    escape_routes.append((escape_x, escape_y))

        return escape_routes

    def _intelligent_patrol(self, maze, pacman_pos, visible_ghosts):
        # точки патрулювання біля перехресть
        if not self.patrol_points or random.random() < 0.05:
            intersections = self._find_intersections(maze)
            if intersections:
                self.patrol_points = random.sample(intersections,
                                                   min(4, len(intersections)))

        return self._easy_strategy(maze, pacman_pos)

    def _find_intersections(self, maze):
        # Знаходить перехрестя в лабіринті
        intersections = []
        for y in range(1, len(maze) - 1):
            for x in range(1, len(maze[0]) - 1):
                if maze[y][x] != 1:
                    passages = 0
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        if maze[y + dy][x + dx] != 1:
                            passages += 1

                    if passages >= 3:
                        intersections.append((x, y))

        return intersections

    def _move_towards_target(self, maze, target):
        if not target or target == (self.x, self.y):
            return

        path = PathFinder.astar(maze, (self.x, self.y), target)

        if path and len(path) > 0:
            next_pos = path[0]

            if next_pos not in self.position_history[-3:]:
                self.x, self.y = next_pos
            else:
                alternatives = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    alt_x, alt_y = self.x + dx, self.y + dy
                    if (0 <= alt_x < len(maze[0]) and 0 <= alt_y < len(maze) and
                            maze[alt_y][alt_x] != 1 and
                            (alt_x, alt_y) not in self.position_history[-3:]):
                        alternatives.append((alt_x, alt_y))

                if alternatives:
                    best_alt = min(alternatives,
                                   key=lambda p: math.sqrt((p[0] - target[0]) ** 2 +
                                                           (p[1] - target[1]) ** 2))
                    self.x, self.y = best_alt
