import pygame
from constants import *
from maze_generator import MazeGenerator
from pacman import *
from ghost import *


class Game:
    """Основний ігровий клас"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        self.difficulty = DifficultyLevel.EASY
        self.level = 1
        self.setup_game()

    def setup_game(self):
        """Налаштування гри"""
        # Генерація лабіринту
        generator = MazeGenerator(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze = generator.generate_maze()

        # Знаходимо початкові позиції
        start_positions = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] != 1:
                    start_positions.append((x, y))

        # Створюємо пакмена
        pacman_pos = random.choice(start_positions)
        self.pacman = Pacman(pacman_pos[0], pacman_pos[1])

        # Створюємо привидів
        ghost_colors = [RED, PINK, CYAN, ORANGE]
        self.ghosts = []
        for i in range(4):
            pos = random.choice([p for p in start_positions if p != pacman_pos])
            visibility = self._get_ghost_visibility()
            ghost = Ghost(pos[0], pos[1], ghost_colors[i], i, visibility)
            self.ghosts.append(ghost)

    def _get_ghost_visibility(self):
        """Отримує дальність видимості привидів залежно від рівня складності"""
        if self.difficulty == DifficultyLevel.EASY:
            return random.randint(3, 5)
        elif self.difficulty == DifficultyLevel.MEDIUM:
            return random.randint(5, 8)
        else:  # HARD
            return random.randint(7, 10)

    def check_collisions(self):
        """Перевіряє зіткнення пакмена з привидами"""
        for ghost in self.ghosts:
            if abs(self.pacman.x - ghost.x) < 1 and abs(self.pacman.y - ghost.y) < 1:
                self.pacman.lives -= 1
                if self.pacman.lives <= 0:
                    return True  # Game over
                else:
                    # Переміщуємо пакмена в безпечне місце
                    self._respawn_pacman()
        return False

    def _respawn_pacman(self):
        """Відроджує пакмена"""
        safe_positions = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] != 1:
                    safe = True
                    for ghost in self.ghosts:
                        if math.sqrt((x - ghost.x) ** 2 + (y - ghost.y) ** 2) < 5:
                            safe = False
                            break
                    if safe:
                        safe_positions.append((x, y))

        if safe_positions:
            pos = random.choice(safe_positions)
            self.pacman.x, self.pacman.y = pos

    def check_level_complete(self):
        """Перевіряє чи завершений рівень"""
        dots_remaining = sum(row.count(2) + row.count(3) for row in self.maze)
        if dots_remaining == 0:
            self.level += 1
            if self.level % 3 == 0:
                # Підвищуємо складність кожні 3 рівні
                if self.difficulty == DifficultyLevel.EASY:
                    self.difficulty = DifficultyLevel.MEDIUM
                elif self.difficulty == DifficultyLevel.MEDIUM:
                    self.difficulty = DifficultyLevel.HARD
            self.setup_game()
            return True
        return False

    def handle_input(self):
        """Обробка введення"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.pacman.move(Direction.UP, self.maze)
        elif keys[pygame.K_DOWN]:
            self.pacman.move(Direction.DOWN, self.maze)
        elif keys[pygame.K_LEFT]:
            self.pacman.move(Direction.LEFT, self.maze)
        elif keys[pygame.K_RIGHT]:
            self.pacman.move(Direction.RIGHT, self.maze)

    def update(self):
        """Оновлення стану гри"""
        # Рух привидів
        for ghost in self.ghosts:
            ghost.move(self.maze, (self.pacman.x, self.pacman.y),
                       self.pacman.direction, self.ghosts, self.difficulty)

        # Перевірка зіткнень
        if self.check_collisions():
            return False  # Game over

        # Перевірка завершення рівня
        self.check_level_complete()

        return True

    def draw(self):
        """Малювання гри"""
        self.screen.fill(BLACK)

        # Малювання лабіринту
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.maze[y][x] == 1:  # Стіна
                    pygame.draw.rect(self.screen, BLUE, rect)
                elif self.maze[y][x] == 2:  # Точка
                    pygame.draw.circle(self.screen, WHITE, rect.center, 2)
                elif self.maze[y][x] == 3:  # Бонус
                    pygame.draw.circle(self.screen, WHITE, rect.center, 5)

        # Малювання пакмена
        pacman_rect = pygame.Rect(self.pacman.x * CELL_SIZE, self.pacman.y * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(self.screen, YELLOW, pacman_rect.center, CELL_SIZE // 2)

        # Малювання привидів
        for ghost in self.ghosts:
            ghost_rect = pygame.Rect(ghost.x * CELL_SIZE, ghost.y * CELL_SIZE,
                                     CELL_SIZE, CELL_SIZE)
            pygame.draw.circle(self.screen, ghost.color, ghost_rect.center, CELL_SIZE // 2)

            # Показуємо зону видимості (для налагодження)
            if pygame.key.get_pressed()[pygame.K_d]:  # Debug mode
                vision_rect = pygame.Rect(
                    (ghost.x - ghost.visibility_range) * CELL_SIZE,
                    (ghost.y - ghost.visibility_range) * CELL_SIZE,
                    ghost.visibility_range * 2 * CELL_SIZE,
                    ghost.visibility_range * 2 * CELL_SIZE
                )
                pygame.draw.rect(self.screen, ghost.color, vision_rect, 1)

        # UI інформація
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        difficulty_text = font.render(f"Difficulty: {self.difficulty.name}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        self.screen.blit(difficulty_text, (10, 130))

        # Інструкції
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Arrow keys - move",
            "D - debug mode (show ghost vision)",
            "ESC - quit"
        ]
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH - 200, 10 + i * 25))

        pygame.display.flip()

    def run(self):
        """Основний ігровий цикл"""
        running = True
        game_over = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                    # Рестарт гри
                    self.level = 1
                    self.difficulty = DifficultyLevel.EASY
                    self.setup_game()
                    game_over = False

            if not game_over:
                self.handle_input()
                if not self.update():
                    game_over = True

            self.draw()

            if game_over:
                # Показуємо повідомлення про завершення гри
                font = pygame.font.Font(None, 72)
                game_over_text = font.render("GAME OVER", True, RED)
                restart_text = font.render("Press R to restart", True, WHITE)

                text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))

                self.screen.blit(game_over_text, text_rect)
                self.screen.blit(restart_text, restart_rect)
                pygame.display.flip()

            self.clock.tick(10)  # 10 FPS для кращої візуалізації

        pygame.quit()
