import random
from collections import deque

CELL = 40  # cell size in pixels
WALL_T = 3  # wall thickness in pixels (same width the walls are drawn with)

# Index of each side inside a cell's wall list: [N, S, E, W]
N, S, E, W = 0, 1, 2, 3


def generate_maze(cols, rows):
    """Recursive backtracker maze generation. Returns 2D grid of walls."""
    visited = [[False]*cols for _ in range(rows)]
    # walls: each cell has [N, S, E, W]
    walls = [[[True,True,True,True] for _ in range(cols)] for _ in range(rows)]

    def neighbors(r, c):
        dirs = [(-1,0,0,1),(1,0,1,0),(0,1,2,3),(0,-1,3,2)]  # dr,dc,wall_dir,opp_dir
        result = []
        for dr,dc,wd,od in dirs:
            nr,nc = r+dr,c+dc
            if 0<=nr<rows and 0<=nc<cols and not visited[nr][nc]:
                result.append((nr,nc,wd,od))
        return result

    stack = [(0,0)]
    visited[0][0] = True
    while stack:
        r,c = stack[-1]
        nbrs = neighbors(r,c)
        if nbrs:
            nr,nc,wd,od = random.choice(nbrs)
            walls[r][c][wd] = False
            walls[nr][nc][od] = False
            visited[nr][nc] = True
            stack.append((nr,nc))
        else:
            stack.pop()
    return walls


def solve_maze(walls, start, goal):
    """Breadth-first search. Returns the shortest path as a list of (row, col)
    cells from start to goal (inclusive), or [] if there is no path."""
    rows, cols = len(walls), len(walls[0])
    moves = [(-1, 0, N), (1, 0, S), (0, 1, E), (0, -1, W)]  # dr, dc, wall side
    came_from = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            break
        r, c = cell
        for dr, dc, side in moves:
            if walls[r][c][side]:
                continue
            nxt = (r + dr, c + dc)
            if 0 <= nxt[0] < rows and 0 <= nxt[1] < cols and nxt not in came_from:
                came_from[nxt] = cell
                queue.append(nxt)
    if goal not in came_from:
        return []
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = came_from[cell]
    path.reverse()
    return path


def cell_rect(r, c, import_pygame=None):
    import pygame
    return pygame.Rect(c*CELL, r*CELL, CELL, CELL)


def wall_rects(walls, r, c):
    """Pixel rectangles for the walls that are present around cell (r, c).
    They cover exactly the pixels the walls are drawn on."""
    import pygame
    x, y = c*CELL, r*CELL
    t = WALL_T
    h = t // 2
    w = walls[r][c]
    rects = []
    if w[N]: rects.append(pygame.Rect(x - h, y - h, CELL + t, t))
    if w[S]: rects.append(pygame.Rect(x - h, y + CELL - h, CELL + t, t))
    if w[E]: rects.append(pygame.Rect(x + CELL - h, y - h, t, CELL + t))
    if w[W]: rects.append(pygame.Rect(x - h, y - h, t, CELL + t))
    return rects
