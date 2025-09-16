import pygame
from constants import *
from maze_generator import MazeGenerator
from pacman import *
from ghost import *


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

        self.difficulty = DifficultyLevel.EASY
        self.level = 1
        self.setup_game()

    def setup_game(self):
        generator = MazeGenerator(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze = generator.generate_maze()

        # Знаходимо початкові позиції
        start_positions = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] != 1:
                    start_positions.append((x, y))

        pacman_pos = random.choice(start_positions)
        self.pacman = Pacman(pacman_pos[0], pacman_pos[1])

        ghost_colors = [RED, PINK, CYAN, ORANGE]
        self.ghosts = []
        for i in range(2):
            pos = random.choice([p for p in start_positions if p != pacman_pos])
            visibility = self._get_ghost_visibility()
            ghost = Ghost(pos[0], pos[1], ghost_colors[i], i, visibility)
            self.ghosts.append(ghost)

    def _get_ghost_visibility(self):
        if self.difficulty == DifficultyLevel.EASY:
            return random.randint(3, 5)
        elif self.difficulty == DifficultyLevel.MEDIUM:
            return random.randint(5, 8)
        else:  # HARD
            return random.randint(7, 10)

    def check_collisions(self):
        for ghost in self.ghosts:
            if abs(self.pacman.x - ghost.x) < 1 and abs(self.pacman.y - ghost.y) < 1:
                self.pacman.lives -= 1
                if self.pacman.lives <= 0:
                    return True  # Game over
                else:
                    self._respawn_pacman()
        return False

    def _respawn_pacman(self):
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
        # Рахуємо тільки великі точки (бонуси) - код 3
        big_dots_remaining = sum(row.count(3) for row in self.maze)

        if big_dots_remaining == 0:
            if self.level < 3:  # Максимум 3 рівні
                self.level += 1
                print(f"Level {self.level} completed! Moving to next level...")

                # Встановлюємо складність відповідно до рівня
                if self.level == 2:
                    self.difficulty = DifficultyLevel.MEDIUM
                    print("Difficulty increased to MEDIUM")
                elif self.level == 3:
                    self.difficulty = DifficultyLevel.HARD
                    print("Difficulty increased to HARD")

                self.setup_game()
                return True
            else:
                print("Congratulations! You completed all levels!")
                return "victory"
        return False

    def handle_input(self):
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
        # Рух привидів
        for ghost in self.ghosts:
            ghost.move(self.maze, (self.pacman.x, self.pacman.y),
                       self.pacman.direction, self.ghosts, self.difficulty)

        # Перевірка зіткнень
        if self.check_collisions():
            return False  # Game over

        level_result = self.check_level_complete()
        if level_result == "victory":
            return "victory"

        return True

    def draw(self):
        self.screen.fill(BLACK)

        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.maze[y][x] == 1:
                    pygame.draw.rect(self.screen, BLUE, rect)
                    pygame.draw.circle(self.screen, WHITE, rect.center, 3)
                    pygame.draw.circle(self.screen, WHITE, rect.center, 8)
                    if pygame.time.get_ticks() % 1000 < 500:
                        pygame.draw.circle(self.screen, YELLOW, rect.center, 6)

        pacman_rect = pygame.Rect(self.pacman.x * CELL_SIZE, self.pacman.y * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(self.screen, YELLOW, pacman_rect.center, CELL_SIZE // 2)

        for ghost in self.ghosts:
            ghost_rect = pygame.Rect(ghost.x * CELL_SIZE, ghost.y * CELL_SIZE,
                                     CELL_SIZE, CELL_SIZE)
            pygame.draw.circle(self.screen, ghost.color, ghost_rect.center, CELL_SIZE // 2)

            if pygame.key.get_pressed()[pygame.K_d]:  # Debug mode
                vision_rect = pygame.Rect(
                    (ghost.x - ghost.visibility_range) * CELL_SIZE,
                    (ghost.y - ghost.visibility_range) * CELL_SIZE,
                    ghost.visibility_range * 2 * CELL_SIZE,
                    ghost.visibility_range * 2 * CELL_SIZE
                )
                pygame.draw.rect(self.screen, ghost.color, vision_rect, 1)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.pacman.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.pacman.lives}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        difficulty_text = font.render(f"Difficulty: {self.difficulty.name}", True, WHITE)

        # Лічильник великих точок
        big_dots_remaining = sum(row.count(3) for row in self.maze)
        big_dots_text = font.render(f"Big Dots: {big_dots_remaining}", True, YELLOW)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        self.screen.blit(difficulty_text, (10, 130))
        self.screen.blit(big_dots_text, (10, 170))

        pygame.display.flip()

    def run(self):
        running = True
        game_over = False
        victory = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_over or victory):
                    self.level = 1
                    self.difficulty = DifficultyLevel.EASY
                    self.setup_game()
                    game_over = False
                    victory = False

            if not game_over and not victory:
                self.handle_input()
                level_result = self.update()
                if level_result == False:
                    game_over = True
                elif level_result == "victory":
                    victory = True

            self.draw()

            if game_over:
                font = pygame.font.Font(None, 72)
                game_over_text = font.render("GAME OVER", True, RED)
                restart_text = font.render("Press R to restart", True, WHITE)

                text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))

                self.screen.blit(game_over_text, text_rect)
                self.screen.blit(restart_text, restart_rect)
                pygame.display.flip()

            elif victory:
                font = pygame.font.Font(None, 72)
                victory_text = font.render("VICTORY!", True, GREEN)
                completed_text = font.render("All levels completed!", True, WHITE)
                restart_text = font.render("Press R to restart", True, WHITE)

                victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
                completed_rect = completed_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))

                self.screen.blit(victory_text, victory_rect)
                self.screen.blit(completed_text, completed_rect)
                self.screen.blit(restart_text, restart_rect)
                pygame.display.flip()

            self.clock.tick(10)

        pygame.quit()
