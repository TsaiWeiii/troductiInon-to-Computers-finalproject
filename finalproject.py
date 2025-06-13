import pygame
import sys
import random

# 初始化
pygame.init()

# 設定參數
SIZE = 15  # 棋盤 15x15
GRID_SIZE = 40
MARGIN = 40
WIDTH = HEIGHT = GRID_SIZE * (SIZE - 1) + MARGIN * 2
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("五子棋：人類 vs AI")

# 顏色
BG_COLOR = (240, 200, 140)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

EDGE_SQUARE_BONUS = 20
NEAR_EDGE_SQUARE_BONUS = 10
FIVE_BY_FIVE_FRIENDLY_BONUS = 5
FIVE_BY_FIVE_OPPONENT_BONUS = 2

DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

EASY_SCORE_RANDOM_SUBTRACT_MAX = 150
MEDIUM_SCORE_RANDOM_SUBTRACT_MAX = 75

BUTTON_WIDTH = 220
BUTTON_HEIGHT = 60
BUTTON_COLOR = (100, 100, 200)
BUTTON_TEXT_COLOR = WHITE
MENU_FONT_SIZE = 36

board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
current_player = 1
game_over = False
winner = 0
game_state = "difficulty_select"
selected_difficulty = None

def draw_board():
    SCREEN.fill(BG_COLOR)
    font = pygame.font.SysFont(None, 28, bold=True)
    for i in range(SIZE):
        pygame.draw.line(SCREEN, BLACK,
                         (MARGIN, MARGIN + i * GRID_SIZE),
                         (WIDTH - MARGIN, MARGIN + i * GRID_SIZE))
        pygame.draw.line(SCREEN, BLACK,
                         (MARGIN + i * GRID_SIZE, MARGIN),
                         (MARGIN + i * GRID_SIZE, HEIGHT - MARGIN))
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] != 0:
                color = BLACK if board[y][x] == 1 else WHITE
                pygame.draw.circle(SCREEN, color,
                                   (MARGIN + x * GRID_SIZE, MARGIN + y * GRID_SIZE),
                                   GRID_SIZE // 2 - 2)

def check_win(x, y):
    player = board[y][x]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        for d in [1, -1]:
            nx, ny = x, y
            for _ in range(4):
                nx += dx * d
                ny += dy * d
                if 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
                    count += 1
                else:
                    break
        if count >= 5:
            return True
    return False

def count_continuous(x, y, player, dx, dy):
    count = 0
    nx, ny = x + dx, y + dy
    while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
        count += 1
        nx += dx
        ny += dy
    return count

def is_four(x, y, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        count += count_continuous(x, y, player, dx, dy)
        count += count_continuous(x, y, player, -dx, -dy)
        if count == 4:
            return True
    return False

def is_live_three(x, y, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        blocks = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx += dx
            ny += dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        nx, ny = x - dx, y - dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx -= dx
            ny -= dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        if count == 3 and blocks == 0:
            return True
    return False

def is_live_four(x, y, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        blocks = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx += dx
            ny += dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        nx, ny = x - dx, y - dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx -= dx
            ny -= dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        if count == 4 and blocks == 0:
            return True
    return False

def is_live_two(x, y, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        blocks = 0
        nx, ny = x + dx, y + dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx += dx
            ny += dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        nx, ny = x - dx, y - dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count += 1
            nx -= dx
            ny -= dy
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks += 1
        if count == 2 and blocks == 0:
            return True
    return False

def is_double_three(x, y, player):
    if board[y][x] != 0: return False
    board[y][x] = player
    live_three_axis_count = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx_axis, dy_axis in directions:
        count_on_this_axis = 1
        blocks_on_this_axis = 0
        nx, ny = x + dx_axis, y + dy_axis
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count_on_this_axis += 1
            nx += dx_axis
            ny += dy_axis
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks_on_this_axis += 1
        nx, ny = x - dx_axis, y - dy_axis
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count_on_this_axis += 1
            nx -= dx_axis
            ny -= dy_axis
        if not (0 <= nx < SIZE and 0 <= ny < SIZE) or board[ny][nx] != 0:
            blocks_on_this_axis += 1
        if count_on_this_axis == 3 and blocks_on_this_axis == 0:
            live_three_axis_count += 1
    board[y][x] = 0
    return live_three_axis_count >= 2

def is_double_four(x, y, player):
    board[y][x] = player
    cnt = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count_on_this_axis = 1
        nx, ny = x + dx, y + dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count_on_this_axis += 1
            nx += dx
            ny += dy
        nx, ny = x - dx, y - dy
        while 0 <= nx < SIZE and 0 <= ny < SIZE and board[ny][nx] == player:
            count_on_this_axis += 1
            nx -= dx
            ny -= dy
        if count_on_this_axis == 4:
            cnt +=1
    board[y][x] = 0
    return cnt >= 2

def is_three_four(x, y, player):
    board[y][x] = player
    has_three = is_live_three(x, y, player)
    has_four = is_four(x, y, player)
    board[y][x] = 0
    return has_three and has_four

def is_jump_four(x, y, player):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        line = []
        for i in range(-2, 3):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                if i == 0:
                    line.append(player)
                else:
                    line.append(board[ny][nx])
            else:
                line.append(-99)
        if len(line) == 5:
            if line[0] == player and line[1] == 0 and line[2] == player and line[3] == player and line[4] == player:
                return True
    return False

def ai_move():
    global board, selected_difficulty
    # 1. AI 自己有五連，直接下贏
    for y_loop in range(SIZE):
        for x_loop in range(SIZE):
            if board[y_loop][x_loop] == 0:
                board[y_loop][x_loop] = 2
                if check_win(x_loop, y_loop):
                    board[y_loop][x_loop] = 0
                    return (x_loop, y_loop)
                board[y_loop][x_loop] = 0
    # 2. 強制阻擋玩家五連
    for y_loop in range(SIZE):
        for x_loop in range(SIZE):
            if board[y_loop][x_loop] == 0:
                board[y_loop][x_loop] = 1
                if check_win(x_loop, y_loop):
                    board[y_loop][x_loop] = 0
                    return (x_loop, y_loop)
                board[y_loop][x_loop] = 0
    # 3. 只用評分法
    max_score = -float('inf')
    best_move = None
    for y_loop in range(SIZE):
        for x_loop in range(SIZE):
            if board[y_loop][x_loop] == 0:
                score = evaluate_position(x_loop, y_loop, 2)
                if score > max_score:
                    max_score = score
                    best_move = (x_loop, y_loop)
    if best_move is None:
        empty = [(x, y) for y in range(SIZE) for x in range(SIZE) if board[y][x] == 0]
        if empty:
            return random.choice(empty)
        return None
    return best_move

def check_hard_mode_live_four_creation_bonus(x_eval, y_eval, player_evaluating_for, current_board):
    bonus = 0
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in directions:
        valid_pattern1 = True
        for i in range(1, 4):
            nx, ny = x_eval + i * dx, y_eval + i * dy
            if not (0 <= nx < SIZE and 0 <= ny < SIZE and current_board[ny][nx] == player_evaluating_for):
                valid_pattern1 = False
                break
        if valid_pattern1:
            ne_x, ne_y = x_eval + 4 * dx, y_eval + 4 * dy
            if not (0 <= ne_x < SIZE and 0 <= ne_y < SIZE and current_board[ne_y][ne_x] == 0):
                valid_pattern1 = False
        if valid_pattern1:
            bonus += 4000
        valid_pattern2 = True
        for i in range(1, 4):
            nx, ny = x_eval - i * dx, y_eval - i * dy
            if not (0 <= nx < SIZE and 0 <= ny < SIZE and current_board[ny][nx] == player_evaluating_for):
                valid_pattern2 = False
                break
        if valid_pattern2:
            ne_x, ne_y = x_eval - 4 * dx, y_eval - 4 * dy
            if not (0 <= ne_x < SIZE and 0 <= ne_y < SIZE and current_board[ne_y][ne_x] == 0):
                valid_pattern2 = False
        if valid_pattern2:
            bonus += 4000
    return bonus

def evaluate_position(x, y, player):
    global selected_difficulty, board
    score = 0
    opponent = 1 if player == 2 else 2
    if is_live_four(x, y, player):
        score += 10000
    elif is_jump_four(x, y, player):
        score += 9000
    elif is_four(x, y, player):
        score += 8000
    elif is_double_three(x, y, player):
        score += 5000
    elif is_live_three(x, y, player):
        score += 1000
    elif is_live_two(x, y, player):
        score += 200
    if is_live_four(x, y, opponent):
        score += 9500
    elif is_jump_four(x, y, opponent):
        score += 8500
    elif is_four(x, y, opponent):
        score += 7000
    elif is_double_three(x, y, opponent):
        score += 4000
    elif is_live_three(x, y, opponent):
        score += 900
    elif is_live_two(x, y, opponent):
        score += 150
    if selected_difficulty:
        if selected_difficulty == DIFFICULTY_MEDIUM or selected_difficulty == DIFFICULTY_HARD:
            current_edge_bonus = 0
            if x == 0 or x == SIZE - 1:
                current_edge_bonus += EDGE_SQUARE_BONUS
            elif x == 1 or x == SIZE - 2:
                current_edge_bonus += NEAR_EDGE_SQUARE_BONUS
            if y == 0 or y == SIZE - 1:
                current_edge_bonus += EDGE_SQUARE_BONUS
            elif y == 1 or y == SIZE - 2:
                current_edge_bonus += NEAR_EDGE_SQUARE_BONUS
            score += current_edge_bonus
        context_score = 0
        r_start, r_end, c_start, c_end = 0,0,0,0
        if selected_difficulty == DIFFICULTY_EASY:
            r_start, r_end = -1, 2
            c_start, c_end = -1, 2
        elif selected_difficulty == DIFFICULTY_MEDIUM:
            r_start, r_end = -1, 3
            c_start, c_end = -1, 3
        elif selected_difficulty == DIFFICULTY_HARD:
            r_start, r_end = -2, 3
            c_start, c_end = -2, 3
        if selected_difficulty in [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]:
            for r_offset in range(r_start, r_end):
                for c_offset in range(c_start, c_end):
                    if r_offset == 0 and c_offset == 0:
                        continue
                    nx, ny = x + c_offset, y + r_offset
                    if 0 <= nx < SIZE and 0 <= ny < SIZE:
                        if board[ny][nx] == player:
                            context_score += FIVE_BY_FIVE_FRIENDLY_BONUS
                        elif board[ny][nx] == opponent:
                            context_score += FIVE_BY_FIVE_OPPONENT_BONUS
            score += context_score
        if selected_difficulty == DIFFICULTY_EASY:
            score += random.randint(-4000, 4000)
        elif selected_difficulty == DIFFICULTY_MEDIUM:
            score -= random.randint(0, MEDIUM_SCORE_RANDOM_SUBTRACT_MAX)
        if selected_difficulty == DIFFICULTY_HARD:
            score += check_hard_mode_live_four_creation_bonus(x, y, player, board)
    return score

def draw_difficulty_menu():
    SCREEN.fill(BG_COLOR)
    menu_font = pygame.font.SysFont(None, MENU_FONT_SIZE, bold=True)
    title_font = pygame.font.SysFont(None, 48, bold=True)
    title_text = title_font.render("Select Difficulty", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    SCREEN.blit(title_text, title_rect)
    difficulties_options = [
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard")
    ]
    num_buttons = len(difficulties_options)
    total_button_height = num_buttons * BUTTON_HEIGHT + (num_buttons - 1) * 20
    button_y_start = HEIGHT // 2 - total_button_height // 2
    buttons_list = []
    for i, (level_id, level_name) in enumerate(difficulties_options):
        button_rect = pygame.Rect(
            WIDTH // 2 - BUTTON_WIDTH // 2,
            button_y_start + i * (BUTTON_HEIGHT + 20),
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        pygame.draw.rect(SCREEN, BUTTON_COLOR, button_rect)
        text_surf = menu_font.render(level_name, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=button_rect.center)
        SCREEN.blit(text_surf, text_rect)
        buttons_list.append({"rect": button_rect, "id": level_id})
    return buttons_list

def draw_game_over_screen(winner_player):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    SCREEN.blit(overlay, (0,0))
    font_large = pygame.font.SysFont(None, 72, bold=True)
    font_medium = pygame.font.SysFont(None, 48, bold=True)
    win_text_str = ""
    if winner_player == 1: win_text_str = "🎉 Player Wins! 🎉"
    elif winner_player == 2: win_text_str = "💀 AI Wins! 💀"
    else: win_text_str = "🤝 It's a Draw! 🤝"
    win_text_surf = font_large.render(win_text_str, True, WHITE)
    win_text_rect = win_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    SCREEN.blit(win_text_surf, win_text_rect)
    restart_text_surf = font_medium.render("Press 'R' to Return to Menu", True, WHITE)
    restart_text_rect = restart_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    SCREEN.blit(restart_text_surf, restart_text_rect)

def reset_game():
    global board, current_player, game_over, winner
    board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    current_player = 1
    game_over = False
    winner = 0

running = True
while running:
    if game_state == "difficulty_select":
        buttons = draw_difficulty_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for button_info in buttons:
                    if button_info["rect"].collidepoint(mouse_pos):
                        selected_difficulty = button_info["id"]
                        reset_game()
                        game_state = "playing"
                        break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
    elif game_state == "playing":
        draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if not game_over and current_player == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                clicked_x = round((mx - MARGIN) / GRID_SIZE)
                clicked_y = round((my - MARGIN) / GRID_SIZE)
                if 0 <= clicked_x < SIZE and 0 <= clicked_y < SIZE and board[clicked_y][clicked_x] == 0:
                    board[clicked_y][clicked_x] = 1
                    if check_win(clicked_x, clicked_y):
                        game_over = True
                        winner = 1
                        game_state = "game_over_screen"
                    else:
                        if not any(0 in row for row in board):
                            game_over = True
                            winner = 0
                            game_state = "game_over_screen"
                        else:
                            current_player = 2
        if not game_over and current_player == 2:
            pygame.display.flip()
            pygame.time.delay(300)
            ai_coords = ai_move()
            if ai_coords:
                ax, ay = ai_coords
                board[ay][ax] = 2
                if check_win(ax, ay):
                    game_over = True
                    winner = 2
                    game_state = "game_over_screen"
                else:
                    if not any(0 in row for row in board):
                        game_over = True
                        winner = 0
                        game_state = "game_over_screen"
                    else:
                        current_player = 1
            else:
                if not any(0 in row for row in board) and not game_over:
                    game_over = True
                    winner = 0
                    game_state = "game_over_screen"
    elif game_state == "game_over_screen":
        draw_board()
        draw_game_over_screen(winner)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "difficulty_select"
                if event.key == pygame.K_ESCAPE:
                    running = False
    pygame.display.flip()
pygame.quit()
sys.exit()
