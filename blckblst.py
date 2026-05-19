import pygame
import random
import sys


pygame.init()
pygame.font.init()

WIDTH = 550
HEIGHT = 760

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.DOUBLEBUF,
    vsync=1
)

pygame.display.set_caption("for you <3")

clock = pygame.time.Clock()
FPS = 144

# =========================================================
# FONT CACHE
# =========================================================

FONT_CACHE = {}

def get_font(size, bold=False):

    key = (size, bold)

    if key not in FONT_CACHE:
        FONT_CACHE[key] = pygame.font.SysFont(
            "Verdana",
            size,
            bold
        )

    return FONT_CACHE[key]

# =========================================================
# THEMES
# =========================================================

THEMES = {

    "mavis": {

        # HAVUZ SUYU MAVISI

        "bg": (170, 235, 255),

        "panel": (120, 210, 245),

        "header": (95, 200, 240),

        "grid_empty": (145, 225, 250),

        "grid_line": (220, 250, 255),

        "accent": (0, 170, 255),

        "text": (255,255,255),

        "blocks": [

            ((120, 220, 255), (0, 180, 240)),
            ((150, 230, 255), (60, 190, 240)),
            ((100, 210, 255), (0, 160, 230)),
            ((170, 240, 255), (70, 190, 255)),
            ((130, 220, 255), (0, 175, 240)),
        ]
    },

    "tatlis_pembe": {

        # SOFT COOKIE PEMBE

        "bg": (255, 214, 224),

        "panel": (232, 165, 185),

        "header": (224, 150, 175),

        "grid_empty": (245, 190, 205),

        "grid_line": (255, 220, 230),

        "accent": (255, 105, 145),

        "text": (255,255,255),

        "blocks": [

            ((255, 170, 195), (230, 120, 155)),
            ((255, 185, 205), (235, 130, 165)),
            ((255, 160, 190), (220, 105, 145)),
            ((250, 175, 200), (225, 120, 160)),
            ((255, 195, 210), (240, 140, 175)),
        ]
    }
}

theme_name = "mavis"
theme = THEMES[theme_name]

# =========================================================
# GRID
# =========================================================

GRID = 8
CELL = 50

BOARD_SIZE = GRID * CELL

BOARD_X = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = 120

board = [[0 for _ in range(GRID)] for _ in range(GRID)]

# =========================================================
# SCORE
# =========================================================

score = 0
best_score = 0
combo = 0

# =========================================================
# SETTINGS
# =========================================================

settings_open = False

settings_button = pygame.Rect(
    WIDTH-58,
    20,
    38,
    38
)

# =========================================================
# GAME
# =========================================================

game_over = False

effects = []

# =========================================================
# SHAPES
# =========================================================

SHAPES = [

    [[1]],

    [[1,1]],
    [[1],[1]],

    [[1,1,1]],
    [[1],[1],[1]],

    [[1,1,1,1]],
    [[1],[1],[1],[1]],

    [[1,1,1,1,1]],
    [[1],[1],[1],[1],[1]],

    [[1,1],[1,1]],

    [[1,1,1],[1,1,1],[1,1,1]],

    [[1,0],[1,1]],
    [[0,1],[1,1]],
    [[1,1],[1,0]],
    [[1,1],[0,1]],

    [[1,1,1],[0,1,0]],
    [[0,1,0],[1,1,1]],

    [[1,1,0],[0,1,1]],
    [[0,1,1],[1,1,0]]
]

# =========================================================
# TEXT
# =========================================================

def render_text(text,size,color,bold=True):

    return get_font(size,bold).render(
        text,
        True,
        color
    )

# =========================================================
# EFFECTS
# =========================================================

class Particle:

    __slots__ = (
        "x","y",
        "vx","vy",
        "alpha",
        "size",
        "color"
    )

    def __init__(self,x,y,color):

        self.x = x
        self.y = y

        self.vx = random.uniform(-4,4)
        self.vy = random.uniform(-6,-1)

        self.alpha = 255

        self.size = random.randint(2,6)

        self.color = color

    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.vy += 0.25

        self.alpha -= 8

    def draw(self,screen):

        if self.alpha <= 0:
            return

        surf = pygame.Surface(
            (18,18),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (*self.color,self.alpha),
            (9,9),
            self.size
        )

        screen.blit(surf,(self.x,self.y))

class FloatingText:

    __slots__ = (
        "text",
        "x","y",
        "alpha",
        "color",
        "scale"
    )

    def __init__(self,text,x,y,color):

        self.text = text

        self.x = x
        self.y = y

        self.alpha = 255

        self.color = color

        self.scale = 1.5

    def update(self):

        self.y -= 1.2

        self.alpha -= 4

        self.scale *= 0.985

    def draw(self,screen):

        if self.alpha <= 0:
            return

        font = get_font(
            int(42*self.scale),
            True
        )

        surf = font.render(
            self.text,
            True,
            self.color
        )

        surf.set_alpha(self.alpha)

        screen.blit(
            surf,
            (
                self.x - surf.get_width()//2,
                self.y
            )
        )

# =========================================================
# HELPERS
# =========================================================

def create_particles(x,y,color,count=6):

    for _ in range(count):

        effects.append(
            Particle(x,y,color)
        )

# =========================================================
# BLOCK DRAW
# =========================================================

def draw_block(screen,colors,rect):

    main,shadow = colors

    pygame.draw.rect(
        screen,
        main,
        rect,
        border_radius=8
    )

    shadow_rect = pygame.Rect(
        rect.x+4,
        rect.y+rect.h-5,
        rect.w-8,
        5
    )

    pygame.draw.rect(
        screen,
        shadow,
        shadow_rect,
        border_radius=4
    )

# =========================================================
# SMART SHAPES
# =========================================================

def shape_size(shape):

    return sum(sum(r) for r in shape)

def get_smart_shape():

    empty = sum(
        cell == 0
        for row in board
        for cell in row
    )

    possible = []

    for s in SHAPES:

        size = shape_size(s)

        if empty < 10:

            if size <= 4:
                possible.append(s)

        else:
            possible.append(s)

    return random.choice(possible)

# =========================================================
# BLOCK CLASS
# =========================================================

class Block:

    __slots__ = (
        "slot",
        "shape",
        "color",
        "active",
        "size",
        "x","y",
        "slot_x","slot_y"
    )

    def __init__(self,slot):

        self.slot = slot

        self.new()

    def new(self):

        self.shape = get_smart_shape()

        self.color = random.choice(
            theme["blocks"]
        )

        self.active = True

        self.size = CELL - 22

        self.slot_x = 95 + self.slot*160
        self.slot_y = 660

        self.reset()

    def reset(self):

        w = len(self.shape[0]) * self.size
        h = len(self.shape) * self.size

        self.x = self.slot_x - w//2
        self.y = self.slot_y - h//2

    def rect(self):

        w = len(self.shape[0]) * self.size
        h = len(self.shape) * self.size

        return pygame.Rect(
            self.x,
            self.y,
            w,
            h
        )

    def draw(self,screen,dragging=False):

        if not self.active:
            return

        size = CELL if dragging else self.size

        for r in range(len(self.shape)):
            for c in range(len(self.shape[0])):

                if self.shape[r][c]:

                    rect = pygame.Rect(
                        self.x + c*size,
                        self.y + r*size,
                        size-2,
                        size-2
                    )

                    draw_block(
                        screen,
                        self.color,
                        rect
                    )

# =========================================================
# PLACE CHECK
# =========================================================

def can_place(shape,row,col):

    if row < 0 or col < 0:
        return False

    if row + len(shape) > GRID:
        return False

    if col + len(shape[0]) > GRID:
        return False

    for r in range(len(shape)):
        for c in range(len(shape[0])):

            if shape[r][c]:

                if board[row+r][col+c]:
                    return False

    return True

# =========================================================
# CLEAR
# =========================================================

def clear_lines():

    global score
    global combo

    rows = []
    cols = []

    for r in range(GRID):

        if all(board[r][c] for c in range(GRID)):
            rows.append(r)

    for c in range(GRID):

        if all(board[r][c] for r in range(GRID)):
            cols.append(c)

    cleared = len(rows) + len(cols)

    if cleared == 0:

        combo = 0
        return

    combo += 1

    for r in rows:
        for c in range(GRID):

            board[r][c] = 0

            create_particles(
                BOARD_X + c*CELL + CELL//2,
                BOARD_Y + r*CELL + CELL//2,
                theme["accent"],
                5
            )

    for c in cols:
        for r in range(GRID):

            board[r][c] = 0

            create_particles(
                BOARD_X + c*CELL + CELL//2,
                BOARD_Y + r*CELL + CELL//2,
                theme["accent"],
                5
            )

    gain = cleared*cleared*100*combo

    score += gain

    if cleared == 1:
        msg = "HARIKA!"

    elif cleared == 2:
        msg = "MUHTESEM!"

    elif cleared == 3:
        msg = "EFSANE!"

    else:
        msg = "INANILMAZ!"

    effects.append(
        FloatingText(
            msg,
            WIDTH//2,
            HEIGHT//2 - 50,
            theme["accent"]
        )
    )

    effects.append(
        FloatingText(
            f"+{gain}",
            WIDTH//2,
            HEIGHT//2 + 10,
            (255,215,0)
        )
    )

# =========================================================
# PLACE BLOCK
# =========================================================

def place_block(block,row,col):

    global score

    for r in range(len(block.shape)):
        for c in range(len(block.shape[0])):

            if block.shape[r][c]:

                board[row+r][col+c] = 1

                px = BOARD_X + (col+c)*CELL + CELL//2
                py = BOARD_Y + (row+r)*CELL + CELL//2

                create_particles(
                    px,
                    py,
                    block.color[0],
                    3
                )

    score += shape_size(block.shape) * 10

    clear_lines()

# =========================================================
# MOVES
# =========================================================

def has_moves():

    for b in blocks:

        if not b.active:
            continue

        for r in range(GRID):
            for c in range(GRID):

                if can_place(b.shape,r,c):
                    return True

    return False

# =========================================================
# RESET
# =========================================================

def reset_game():

    global board
    global score
    global combo
    global game_over
    global best_score

    if score > best_score:
        best_score = score

    board = [[0 for _ in range(GRID)] for _ in range(GRID)]

    score = 0
    combo = 0

    game_over = False

    effects.clear()

    for b in blocks:
        b.new()

# =========================================================
# BLOCKS
# =========================================================

blocks = [
    Block(0),
    Block(1),
    Block(2)
]

selected = None
dragging = False

offset_x = 0
offset_y = 0

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    clock.tick(FPS)

    mx,my = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:
                reset_game()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if settings_button.collidepoint(mx,my):

                    settings_open = not settings_open

                elif settings_open:

                    mavis_btn = pygame.Rect(180,220,180,55)
                    pembe_btn = pygame.Rect(180,300,180,55)

                    if mavis_btn.collidepoint(mx,my):

                        theme_name = "mavis"
                        theme = THEMES["mavis"]

                        for b in blocks:
                            b.color = random.choice(theme["blocks"])

                    elif pembe_btn.collidepoint(mx,my):

                        theme_name = "tatlis_pembe"
                        theme = THEMES["tatlis_pembe"]

                        for b in blocks:
                            b.color = random.choice(theme["blocks"])

                elif not game_over:

                    for b in blocks:

                        if b.active and b.rect().collidepoint(mx,my):

                            selected = b

                            dragging = True

                            offset_x = b.rect().width//2
                            offset_y = b.rect().height//2

                            break

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1 and dragging:

                dragging = False

                row = round((selected.y - BOARD_Y) / CELL)
                col = round((selected.x - BOARD_X) / CELL)

                if can_place(selected.shape,row,col):

                    place_block(selected,row,col)

                    selected.active = False

                    if all(not b.active for b in blocks):

                        for b in blocks:
                            b.new()

                    if not has_moves():
                        game_over = True

                else:
                    selected.reset()

                selected = None

    # UPDATE

    if dragging and selected:

        selected.x = mx - offset_x
        selected.y = my - offset_y

    for i in range(len(effects)-1,-1,-1):

        e = effects[i]

        e.update()

        if e.alpha <= 0:
            effects.pop(i)

    # DRAW

    screen.fill(theme["bg"])

    pygame.draw.rect(
        screen,
        theme["header"],
        (0,0,WIDTH,100)
    )

    title = render_text(
        "SKOR",
        18,
        theme["text"]
    )

    screen.blit(
        title,
        (
            WIDTH//2-title.get_width()//2,
            10
        )
    )

    score_text = render_text(
        str(score),
        48,
        theme["accent"]
    )

    screen.blit(
        score_text,
        (
            WIDTH//2-score_text.get_width()//2,
            32
        )
    )

    # SETTINGS BUTTON

    pygame.draw.rect(
        screen,
        theme["panel"],
        settings_button,
        border_radius=10
    )

    for i in range(3):

        pygame.draw.line(
            screen,
            theme["text"],
            (WIDTH-50,30+i*8),
            (WIDTH-30,30+i*8),
            3
        )

    # BOARD PANEL

    pygame.draw.rect(
        screen,
        theme["panel"],
        (
            BOARD_X-10,
            BOARD_Y-10,
            BOARD_SIZE+20,
            BOARD_SIZE+20
        ),
        border_radius=14
    )

    # GRID

    for r in range(GRID):
        for c in range(GRID):

            rect = pygame.Rect(
                BOARD_X + c*CELL,
                BOARD_Y + r*CELL,
                CELL-2,
                CELL-2
            )

            if board[r][c]:

                draw_block(
                    screen,
                    ((245,245,245),(210,210,210)),
                    rect
                )

            else:

                pygame.draw.rect(
                    screen,
                    theme["grid_empty"],
                    rect,
                    border_radius=6
                )

                pygame.draw.rect(
                    screen,
                    theme["grid_line"],
                    rect,
                    1,
                    border_radius=6
                )

    # GHOST

    if dragging and selected:

        row = round((selected.y - BOARD_Y) / CELL)
        col = round((selected.x - BOARD_X) / CELL)

        valid = can_place(selected.shape,row,col)

        ghost = pygame.Surface(
            (WIDTH,HEIGHT),
            pygame.SRCALPHA
        )

        color = (255,255,255,90)

        if not valid:
            color = (255,80,80,90)

        for r in range(len(selected.shape)):
            for c in range(len(selected.shape[0])):

                if selected.shape[r][c]:

                    gx = BOARD_X + (col+c)*CELL
                    gy = BOARD_Y + (row+r)*CELL

                    pygame.draw.rect(
                        ghost,
                        color,
                        (
                            gx,
                            gy,
                            CELL-2,
                            CELL-2
                        ),
                        border_radius=7
                    )

        screen.blit(ghost,(0,0))

    # SLOTS

    for i in range(3):

        pygame.draw.circle(
            screen,
            theme["grid_empty"],
            (95+i*160,660),
            65
        )

    # BLOCKS

    for b in blocks:

        if b != selected:
            b.draw(screen)

    if selected:
        selected.draw(screen,True)

    # EFFECTS

    for e in effects:
        e.draw(screen)

    # COMBO

    if combo > 1:

        combo_text = render_text(
            f"{combo}x COMBO",
            28,
            (255,215,0)
        )

        screen.blit(
            combo_text,
            (
                WIDTH-combo_text.get_width()-20,
                65
            )
        )

    # SETTINGS MENU

    if settings_open:

        overlay = pygame.Surface(
            (WIDTH,HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0,0,0,120))

        screen.blit(overlay,(0,0))

        menu = pygame.Rect(
            110,
            150,
            330,
            280
        )

        pygame.draw.rect(
            screen,
            theme["panel"],
            menu,
            border_radius=20
        )

        title = render_text(
            "TEMALAR",
            32,
            theme["text"]
        )

        screen.blit(
            title,
            (
                WIDTH//2-title.get_width()//2,
                170
            )
        )

        # MAVIS

        mavis_btn = pygame.Rect(
            180,
            220,
            180,
            55
        )

        pygame.draw.rect(
            screen,
            (90,200,255),
            mavis_btn,
            border_radius=14
        )

        txt = render_text(
            "MAVIS",
            20,
            (255,255,255)
        )

        screen.blit(
            txt,
            (
                mavis_btn.centerx - txt.get_width()//2,
                mavis_btn.centery - txt.get_height()//2
            )
        )

        # PEMBE

        pembe_btn = pygame.Rect(
            180,
            300,
            180,
            55
        )

        pygame.draw.rect(
            screen,
            (255,140,180),
            pembe_btn,
            border_radius=14
        )

        txt2 = render_text(
            "TATLIS PEMBE",
            18,
            (255,255,255)
        )

        screen.blit(
            txt2,
            (
                pembe_btn.centerx - txt2.get_width()//2,
                pembe_btn.centery - txt2.get_height()//2
            )
        )

    # GAME OVER

    if game_over:

        overlay = pygame.Surface(
            (WIDTH,HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0,0,0,180))

        screen.blit(overlay,(0,0))

        go = render_text(
            "OYUN BITTI",
            50,
            theme["accent"]
        )

        screen.blit(
            go,
            (
                WIDTH//2-go.get_width()//2,
                300
            )
        )

        sc = render_text(
            f"Skor: {score}",
            30,
            theme["text"]
        )

        screen.blit(
            sc,
            (
                WIDTH//2-sc.get_width()//2,
                370
            )
        )

        rr = render_text(
            "Tekrar oynamak icin R",
            20,
            theme["text"]
        )

        screen.blit(
            rr,
            (
                WIDTH//2-rr.get_width()//2,
                430
            )
        )

    pygame.display.flip()
