class Pacman:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = None
        self.score = 0
        self.lives = 3

    def move(self, direction, maze):
        dx, dy = direction.value
        new_x, new_y = self.x + dx, self.y + dy

        if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and
                maze[new_y][new_x] != 1):
            self.x, self.y = new_x, new_y
            self.direction = direction.value

            if maze[new_y][new_x] == 2:
                maze[new_y][new_x] = 0
                self.score += 10
            elif maze[new_y][new_x] == 3:
                maze[new_y][new_x] = 0
                self.score += 50