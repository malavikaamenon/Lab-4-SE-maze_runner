Step 1: Fix the wall bug

Prompt :
My Maze Runner player walks through the walls. In player.py, make _hits_wall check the real maze walls, not just the grid edges. Keep the player sliding along walls and keep it inside the maze.
Response: Added wall_rects() to maze.py and rewrote _hits_wall to test the player's rectangle against the wall rectangles of nearby cells. Horizontal and vertical movement are still tried separately, so the player slides.

Step 2: Task 1, shortest path hint

Prompt :
Add a BFS solver to my pygame maze. When H is pressed, highlight the shortest path from start to exit by drawing coloured squares on each cell in the path. Toggle it off on second press.
Response: Added solve_maze() to maze.py, computed once per maze. game_engine.py draws an orange square on every path cell while show_path is on, and H flips that flag.

Step 3: Task 2, fog of war

Prompt :
Add fog of war to my maze game. Draw a dark overlay over the whole maze, then cut a transparent circle around the player using pygame.draw.circle on an SRCALPHA surface. Only show cells within 3 cells of the player.
Response: Added draw_fog(), which fills an SRCALPHA surface with near-black and cuts a transparent circle of radius 3 cells at the player. F toggles it, and it switches off on the win screen.

Step 4: Task 3, timer leaderboard

Prompt :
After the player solves the maze, save their time to a list of up to 5 entries sorted ascending. Show the leaderboard on the win screen and keep it in leaderboard.json.
Response: Created game/leaderboard.py with load, save and add_time. Times are kept per difficulty, the best five are shown on the win screen, and the new time is marked "<- you".

Step 5: Task 4, difficulty tiers

Prompt :
Add a difficulty select screen before the maze generates. Show three buttons, Easy (10x8), Medium (15x13) and Hard (20x18). Let the player click one, then start the maze at that size.
Response: Added a menu state with three hover-highlighted buttons (click or press 1, 2, 3). The window resizes to the chosen maze, and M or Esc returns to the menu.
