import pygame
from game.maze import CELL, wall_rects

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        self.rect = pygame.Rect(x-10, y-10, 20, 20)
        self.color = (60,120,220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = SPEED

        # Wall-aware movement: each axis is tried separately so the player
        # slides along a wall instead of sticking to it.
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect
        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        # Range of grid cells the rect overlaps
        c0, c1 = rect.left // CELL, (rect.right - 1) // CELL
        r0, r1 = rect.top // CELL, (rect.bottom - 1) // CELL
        # Outside the maze counts as a hit
        if r0 < 0 or c0 < 0 or r1 >= rows or c1 >= cols:
            return True
        # Test the rect against every wall segment of those cells and their
        # neighbours (wall ends stick out a pixel or two past their own cell)
        for r in range(max(0, r0 - 1), min(rows, r1 + 2)):
            for c in range(max(0, c0 - 1), min(cols, c1 + 2)):
                for wall in wall_rects(walls, r, c):
                    if rect.colliderect(wall):
                        return True
        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
