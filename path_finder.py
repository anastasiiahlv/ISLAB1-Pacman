import heapq
from collections import deque


class PathFinder:
    """Алгоритми пошуку шляху"""

    @staticmethod
    def bfs(maze, start, goal):
        """Breadth-First Search"""
        queue = deque([(start, [])])
        visited = set([start])

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == goal:
                return path

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and
                        maze[ny][nx] != 1 and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return []

    @staticmethod
    def astar(maze, start, goal):
        """A* Search Algorithm"""

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        heap = [(0, start, [])]
        visited = set()

        while heap:
            cost, (x, y), path = heapq.heappop(heap)

            if (x, y) in visited:
                continue
            visited.add((x, y))

            if (x, y) == goal:
                return path

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and
                        maze[ny][nx] != 1 and (nx, ny) not in visited):
                    new_cost = len(path) + 1 + heuristic((nx, ny), goal)
                    heapq.heappush(heap, (new_cost, (nx, ny), path + [(nx, ny)]))
        return []