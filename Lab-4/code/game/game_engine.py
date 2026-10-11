import pygame
import time
from game.maze import generate_maze, solve_maze, CELL
from game.player import Player
from game import leaderboard

FPS = 60
BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
PATH_COLOR = (255, 190, 50)
HUD_H = 60

# (name, cols, rows)
DIFFICULTIES = [
    ("Easy", 10, 8),
    ("Medium", 15, 13),
    ("Hard", 20, 18),
]
MENU_SIZE = (600, 420)

FOG_RADIUS_CELLS = 3
FOG_ALPHA = 240


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(MENU_SIZE)
        pygame.display.set_caption("Maze Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.mid_font = pygame.font.SysFont("monospace", 30, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 16)
        self.tiny_font = pygame.font.SysFont("monospace", 12, bold=True)

        self.state = "menu"          # "menu" or "play"
        self.fog_enabled = True
        self.difficulty = DIFFICULTIES[1][0]
        self.cols, self.rows = DIFFICULTIES[1][1], DIFFICULTIES[1][2]
        self.width = self.cols * CELL
        self.height = self.rows * CELL + HUD_H
        self.menu_buttons = self._build_menu_buttons()

    # ---------- menu ----------
    def _build_menu_buttons(self):
        buttons = []
        w, h, gap = 320, 56, 20
        top = 150
        for i in range(len(DIFFICULTIES)):
            x = MENU_SIZE[0] // 2 - w // 2
            buttons.append(pygame.Rect(x, top + i * (h + gap), w, h))
        return buttons

    def open_menu(self):
        self.state = "menu"
        self.screen = pygame.display.set_mode(MENU_SIZE)

    def start_game(self, index):
        name, cols, rows = DIFFICULTIES[index]
        self.difficulty = name
        self.cols, self.rows = cols, rows
        self.width = cols * CELL
        self.height = rows * CELL + HUD_H
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.fog_surface = pygame.Surface((self.width, rows * CELL), pygame.SRCALPHA)
        self.state = "play"
        self.reset()

    def _menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.menu_buttons):
                if rect.collidepoint(event.pos):
                    self.start_game(i)
                    return
        elif event.type == pygame.KEYDOWN:
            keys = [pygame.K_1, pygame.K_2, pygame.K_3]
            if event.key in keys:
                self.start_game(keys.index(event.key))

    # ---------- game state ----------
    def reset(self):
        self.walls = generate_maze(self.cols, self.rows)
        self.player = Player(0, 0)
        self.exit_rect = pygame.Rect((self.cols-1)*CELL+5, (self.rows-1)*CELL+5, CELL-10, CELL-10)
        self.path = solve_maze(self.walls, (0, 0), (self.rows-1, self.cols-1))
        self.show_path = False
        self.start_time = time.time()
        self.elapsed = 0
        self.won = False
        self.best_times = []
        self.rank = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == "menu":
                self._menu_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_h:
                    self.show_path = not self.show_path
                elif event.key == pygame.K_f:
                    self.fog_enabled = not self.fog_enabled
                elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                    self.open_menu()
        return True

    def update(self):
        if self.state != "play" or self.won:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, self.rows, self.cols)
        self.elapsed = time.time() - self.start_time
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True
            self.best_times, self.rank = leaderboard.add_time(self.difficulty, self.elapsed)

    # ---------- drawing ----------
    def draw_menu(self):
        self.screen.fill(BG)
        title = self.big_font.render("Maze Runner", True, WALL_COLOR)
        self.screen.blit(title, (MENU_SIZE[0]//2 - title.get_width()//2, 40))
        sub = self.font.render("Select difficulty", True, (90, 90, 110))
        self.screen.blit(sub, (MENU_SIZE[0]//2 - sub.get_width()//2, 100))

        mouse = pygame.mouse.get_pos()
        for i, rect in enumerate(self.menu_buttons):
            name, cols, rows = DIFFICULTIES[i]
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(self.screen, (70, 90, 160) if hover else WALL_COLOR, rect, border_radius=8)
            label = self.font.render(f"{i+1}. {name}  ({cols}x{rows})", True, (240, 240, 240))
            self.screen.blit(label, (rect.centerx - label.get_width()//2,
                                     rect.centery - label.get_height()//2))
        hint = self.small_font.render("Click a button or press 1 / 2 / 3", True, (90, 90, 110))
        self.screen.blit(hint, (MENU_SIZE[0]//2 - hint.get_width()//2, MENU_SIZE[1] - 40))

    def draw_maze(self):
        wall_w = 3
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c*CELL, r*CELL
                w = self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x+CELL,y), wall_w)
                if w[1]: pygame.draw.line(self.screen, WALL_COLOR, (x,y+CELL), (x+CELL,y+CELL), wall_w)
                if w[2]: pygame.draw.line(self.screen, WALL_COLOR, (x+CELL,y), (x+CELL,y+CELL), wall_w)
                if w[3]: pygame.draw.line(self.screen, WALL_COLOR, (x,y), (x,y+CELL), wall_w)

    def draw_path(self):
        for r, c in self.path:
            rect = pygame.Rect(c*CELL + 12, r*CELL + 12, CELL - 24, CELL - 24)
            pygame.draw.rect(self.screen, PATH_COLOR, rect, border_radius=3)

    def draw_fog(self):
        # Dark overlay over the whole maze with a see-through circle around the player
        self.fog_surface.fill((0, 0, 0, FOG_ALPHA))
        pygame.draw.circle(self.fog_surface, (0, 0, 0, 0),
                           self.player.rect.center, FOG_RADIUS_CELLS * CELL)
        self.screen.blit(self.fog_surface, (0, 0))

    def draw_win_overlay(self):
        maze_h = self.rows * CELL
        overlay = pygame.Surface((self.width, maze_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        lines = [self.mid_font.render(f"Solved in {self.elapsed:.2f}s!", True, (80, 240, 80))]
        lines.append(self.font.render(f"Best times - {self.difficulty}", True, (230, 230, 230)))
        for i, t in enumerate(self.best_times):
            you = i == self.rank
            text = f"{i+1}. {t:.2f}s" + ("  <- you" if you else "")
            color = (255, 220, 80) if you else (200, 200, 200)
            lines.append(self.small_font.render(text, True, color))
        lines.append(self.small_font.render("R: new maze   M: menu", True, (200, 200, 200)))

        gap = 6
        total = sum(s.get_height() for s in lines) + gap * (len(lines) - 1)
        y = max(4, (maze_h - total) // 2)
        for s in lines:
            self.screen.blit(s, (self.width//2 - s.get_width()//2, y))
            y += s.get_height() + gap

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            pygame.display.flip()
            return

        maze_h = self.rows * CELL
        self.screen.fill(BG)
        self.draw_maze()
        if self.show_path:
            self.draw_path()
        pygame.draw.rect(self.screen, EXIT_COLOR, self.exit_rect, border_radius=4)
        ex_label = self.tiny_font.render("EXIT", True, (20,80,20))
        self.screen.blit(ex_label, (self.exit_rect.centerx - ex_label.get_width()//2,
                                    self.exit_rect.centery - ex_label.get_height()//2))
        self.player.draw(self.screen)

        if self.fog_enabled and not self.won:
            self.draw_fog()

        hud = pygame.Rect(0, maze_h, self.width, HUD_H)
        pygame.draw.rect(self.screen, (30,30,50), hud)
        time_surf = self.font.render(f"{self.difficulty}  Time: {self.elapsed:.1f}s", True, (200,200,200))
        self.screen.blit(time_surf, (10, maze_h + 8))
        help_surf = self.small_font.render("R:New  H:Hint  F:Fog  M:Menu", True, (150,150,170))
        self.screen.blit(help_surf, (10, maze_h + 36))

        if self.won:
            self.draw_win_overlay()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
