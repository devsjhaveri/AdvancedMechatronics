"""
Whack-A-Person! 🔨
==================
Press SPACE to swing the hammer at the face when it pops up!
Be quick — the face disappears fast, and gets faster as your score rises.

Setup:
  1. Place face.jpg in the same folder as this file
  2. Run:  pgzrun whack_game.py

Controls:
  SPACE  →  Swing hammer
  SPACE  →  Restart after Game Over
"""

import pgzrun
import pygame
import random
import math
import os
import shutil

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW
# ─────────────────────────────────────────────────────────────────────────────
WIDTH  = 720
HEIGHT = 520
TITLE  = "Whack-A-Person! 🔨"

# ─────────────────────────────────────────────────────────────────────────────
# COPY FACE IMAGE INTO images/ FOLDER (pgzero needs it there for Actor)
# ─────────────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_IMG_DIR    = os.path.join(_SCRIPT_DIR, 'images')
os.makedirs(_IMG_DIR, exist_ok=True)

# Looks for face.jpg next to this script
_FACE_SRC = os.path.join(_SCRIPT_DIR, 'face.jpg')
_FACE_DST = os.path.join(_IMG_DIR, 'face.jpg')
if os.path.exists(_FACE_SRC) and not os.path.exists(_FACE_DST):
    shutil.copy(_FACE_SRC, _FACE_DST)

# ─────────────────────────────────────────────────────────────────────────────
# HOLE POSITIONS  (6 holes in a 3×2 grid)
# ─────────────────────────────────────────────────────────────────────────────
COLS, ROWS   = 3, 2
HOLE_W       = 160
HOLE_H       = 90
FACE_SIZE    = 120       # pixels, face is square-ish
PAD_X, PAD_Y = 80, 200

HOLES = [
    (PAD_X + c * (HOLE_W + 60), PAD_Y + r * (HOLE_H + 110))
    for r in range(ROWS)
    for c in range(COLS)
]

# ─────────────────────────────────────────────────────────────────────────────
# COLOURS & STYLE
# ─────────────────────────────────────────────────────────────────────────────
C_BG      = (90,  60,  30)    # dark dirt brown
C_DIRT    = (130, 80,  40)    # medium dirt
C_HOLE    = (40,  20,   5)    # dark hole
C_GRASS   = (60,  150, 40)    # grass
C_GRASS2  = (45,  120, 30)

# ─────────────────────────────────────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────────────────────────────────────
face_surf   = None     # loaded lazily after pygame init

score       = 0
hi_score    = 0
lives       = 3

active_hole   = -1     # which hole currently has a face (-1 = none)
face_timer    = 0      # frames remaining before face ducks
face_duration = 90     # frames the face stays up (~1.5 s @ 60 fps)

spawn_cooldown = 0     # frames to wait before spawning next face

# Hammer animation
hammer_hole   = -1     # which hole the hammer is swinging at
hammer_timer  = 0      # frames left in animation
HIT_FRAMES    = 22
MISS_FRAMES   = 18

# Visual effects
effects = []           # [{x, y, text, color, timer, max_timer}]
screen_flash = 0       # frames of red flash (on miss)

game_state = 'playing' # 'playing' | 'game_over'

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _load_face():
    global face_surf
    if face_surf is not None:
        return
    try:
        raw  = pygame.image.load(_FACE_DST)
        face_surf = pygame.transform.scale(raw, (FACE_SIZE, FACE_SIZE))
    except Exception as e:
        print(f"[Image] Could not load face: {e}")

def _add_effect(x, y, text, color):
    effects.append({'x': x, 'y': y, 'text': text, 'color': color,
                    'timer': 50, 'max_timer': 50})

def _reset():
    global score, lives, active_hole, face_timer, face_duration, spawn_cooldown
    global hammer_hole, hammer_timer, effects, screen_flash, game_state
    score          = 0
    lives          = 3
    active_hole    = -1
    face_timer     = 0
    face_duration  = 90
    spawn_cooldown = 30
    hammer_hole    = -1
    hammer_timer   = 0
    effects        = []
    screen_flash   = 0
    game_state     = 'playing'

def _spawn():
    global active_hole, face_timer, face_duration
    # Pick a hole that is NOT the last one (variety)
    choices = [i for i in range(len(HOLES)) if i != active_hole]
    active_hole  = random.choice(choices)
    # Speed up as score increases, min 38 frames
    face_duration = max(38, 90 - score * 3)
    face_timer    = face_duration

def _hole_center(idx):
    hx, hy = HOLES[idx]
    return hx + HOLE_W // 2, hy

# ─────────────────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────────────────
def update():
    global active_hole, face_timer, spawn_cooldown, screen_flash
    global hammer_timer, lives, game_state, hi_score, effects

    _load_face()   # lazy init after pygame is ready

    if game_state == 'game_over':
        return

    # ── Countdown hammer animation ────────────────────────────────────────
    if hammer_timer > 0:
        hammer_timer -= 1

    # ── Screen flash ─────────────────────────────────────────────────────
    if screen_flash > 0:
        screen_flash -= 1

    # ── Tick effect timers ────────────────────────────────────────────────
    for e in effects:
        e['timer'] -= 1
    effects[:] = [e for e in effects if e['timer'] > 0]

    # ── Spawn logic ───────────────────────────────────────────────────────
    if spawn_cooldown > 0:
        spawn_cooldown -= 1
    elif active_hole == -1:
        _spawn()

    # ── Face timer: duck if not hit in time ───────────────────────────────
    if active_hole >= 0:
        face_timer -= 1
        if face_timer <= 0:
            cx, cy = _hole_center(active_hole)
            _add_effect(cx, cy - 30, "TOO SLOW!", (255, 80, 80))
            active_hole    = -1
            screen_flash   = 25
            lives         -= 1
            spawn_cooldown = 40
            if lives <= 0:
                hi_score   = max(hi_score, score)
                game_state = 'game_over'

# ─────────────────────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────────────────────
def on_key_down(key):
    global score, active_hole, face_timer, hammer_hole, hammer_timer
    global spawn_cooldown, game_state, hi_score, lives

    if key != keys.SPACE:
        return

    if game_state == 'game_over':
        _reset()
        return

    if active_hole >= 0:
        # ── HIT! ─────────────────────────────────────────────────────────
        cx, cy = _hole_center(active_hole)
        hammer_hole    = active_hole
        hammer_timer   = HIT_FRAMES
        score         += 1
        _add_effect(cx, cy - 50, f"WHACK!  +1", (255, 220, 0))
        active_hole    = -1
        face_timer     = 0
        spawn_cooldown = 20

    else:
        # ── WHIFF ────────────────────────────────────────────────────────
        hammer_hole    = random.randint(0, len(HOLES) - 1)
        hammer_timer   = MISS_FRAMES
        cx, cy = _hole_center(hammer_hole)
        _add_effect(cx, cy - 50, "WHIFF!", (200, 200, 200))

# ─────────────────────────────────────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _draw_hammer(hx, hy, progress, is_hit):
    """Draw hammer swinging down.  progress 0→1 over animation."""
    # Swing angle: starts at -70°, slams down to +10°
    angle_deg  = -70 + progress * 80
    angle_rad  = math.radians(angle_deg)

    pivot_x    = hx
    pivot_y    = hy - 80
    handle_len = 70

    tip_x = pivot_x + int(handle_len * math.cos(angle_rad))
    tip_y = pivot_y + int(handle_len * math.sin(angle_rad))

    # Handle
    screen.draw.line((pivot_x, pivot_y), (tip_x, tip_y), (120, 70, 20))

    # Head (2 rects to make a T)
    perp_x = -math.sin(angle_rad)
    perp_y =  math.cos(angle_rad)
    head_w = 28

    lx = int(tip_x + perp_x * head_w)
    ly = int(tip_y + perp_y * head_w)
    rx = int(tip_x - perp_x * head_w)
    ry = int(tip_y - perp_y * head_w)

    head_color = (80, 80, 90) if not is_hit else (200, 60, 60)
    screen.draw.filled_rect(Rect(tip_x - 14, tip_y - 14, 28, 28), head_color)

    # Stars on hit
    if is_hit and progress > 0.5:
        for k in range(6):
            a   = k * 60 + progress * 180
            sx  = tip_x + int(22 * math.cos(math.radians(a)))
            sy  = tip_y + int(22 * math.sin(math.radians(a)))
            screen.draw.filled_rect(Rect(sx - 3, sy - 3, 6, 6), (255, 220, 50))

def _draw_hole_and_face(idx):
    hx, hy = HOLES[idx]
    cx      = hx + HOLE_W // 2

    # Dirt mound behind hole
    screen.draw.filled_rect(Rect(hx - 10, hy - 18, HOLE_W + 20, HOLE_H), C_DIRT)

    # Grass on top of mound
    screen.draw.filled_rect(Rect(hx - 10, hy - 18, HOLE_W + 20, 22), C_GRASS)
    screen.draw.filled_rect(Rect(hx,       hy - 22, HOLE_W,      10), C_GRASS2)

    # Dark hole oval (approximate with rect)
    screen.draw.filled_rect(Rect(hx + 10, hy + 14, HOLE_W - 20, HOLE_H - 20), C_HOLE)

    # ── Face pop-up ───────────────────────────────────────────────────────
    if idx == active_hole and face_surf is not None:
        # Rise-up animation in first 10 frames, duck in last 10 frames
        t = face_timer
        d = face_duration

        if t > d - 10:
            # Rising: 0 (hidden) → full height
            rise_pct = (d - t) / 10.0
        elif t < 10:
            # Ducking: full → 0
            rise_pct = t / 10.0
        else:
            rise_pct = 1.0

        visible_h = int(FACE_SIZE * rise_pct)
        if visible_h > 0:
            # Clip the face to show only `visible_h` pixels from the bottom
            src_rect   = pygame.Rect(0, FACE_SIZE - visible_h, FACE_SIZE, visible_h)
            dest_pos   = (cx - FACE_SIZE // 2, hy - visible_h + 15)
            screen.surface.blit(face_surf, dest_pos, src_rect)

            # Urgency tint bar (green→red based on time left)
            ratio      = t / d
            bar_color  = (int(255 * (1 - ratio)), int(255 * ratio), 0)
            bar_w      = int((HOLE_W - 20) * ratio)
            screen.draw.filled_rect(Rect(hx + 10, hy + HOLE_H - 16, bar_w, 7), bar_color)

# ─────────────────────────────────────────────────────────────────────────────
# DRAW
# ─────────────────────────────────────────────────────────────────────────────
def draw():
    screen.fill(C_BG)

    # ── Background dirt texture (dots) ────────────────────────────────────
    for dx in range(0, WIDTH, 35):
        for dy in range(0, HEIGHT, 35):
            screen.draw.filled_rect(Rect(dx, dy, 4, 4), (100, 65, 32))

    # ── Header bar ────────────────────────────────────────────────────────
    screen.draw.filled_rect(Rect(0, 0, WIDTH, 60), (50, 30, 10))
    screen.draw.text("🔨 WHACK-A-PERSON",
                     center=(WIDTH // 2, 18), color=(255, 210, 0), fontsize=32)
    screen.draw.text(f"SCORE  {score:03d}",  (20,  36), color=(255, 255, 200), fontsize=22)
    screen.draw.text(f"BEST   {hi_score:03d}", (170, 36), color=(180, 180, 180), fontsize=20)

    # Lives as hearts
    hearts = "♥ " * lives + "♡ " * (3 - lives)
    screen.draw.text(hearts, (WIDTH - 130, 36), color=(255, 80, 80), fontsize=22)

    # ── Hint text ─────────────────────────────────────────────────────────
    screen.draw.text("Press SPACE to swing!",
                     center=(WIDTH // 2, 80), color=(200, 160, 100), fontsize=18)

    # ── Holes + faces ─────────────────────────────────────────────────────
    for i in range(len(HOLES)):
        _draw_hole_and_face(i)

    # ── Hammer animation ──────────────────────────────────────────────────
    if hammer_timer > 0 and hammer_hole >= 0:
        max_t    = HIT_FRAMES if (active_hole == -1 and hammer_timer > 0) else MISS_FRAMES
        progress = 1.0 - hammer_timer / HIT_FRAMES
        cx, cy   = _hole_center(hammer_hole)
        is_hit   = hammer_timer <= HIT_FRAMES  # always true here
        _draw_hammer(cx, cy, min(progress * 2, 1.0), hammer_timer > MISS_FRAMES // 2)

    # ── Floating text effects ─────────────────────────────────────────────
    for e in effects:
        t    = e['timer'] / e['max_timer']
        y_up = int((e['max_timer'] - e['timer']) * 0.6)
        alpha_c = tuple(int(c * t) for c in e['color'])
        screen.draw.text(e['text'],
                         center=(e['x'], e['y'] - y_up),
                         color=alpha_c, fontsize=30)

    # ── Red flash on miss ─────────────────────────────────────────────────
    if screen_flash > 0:
        alpha = screen_flash / 25
        r_val = int(80 * alpha)
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (r_val, 0, 0))

    # ── Speed indicator ───────────────────────────────────────────────────
    speed_label = "SLOW" if face_duration > 70 else ("FAST" if face_duration < 50 else "MED")
    speed_color = (100, 200, 100) if face_duration > 70 else ((255, 80, 80) if face_duration < 50 else (255, 200, 50))
    screen.draw.text(f"Speed: {speed_label}", (WIDTH - 130, 80), color=speed_color, fontsize=18)

    # ── GAME OVER overlay ─────────────────────────────────────────────────
    if game_state == 'game_over':
        screen.draw.filled_rect(Rect(160, 170, 400, 170), (20, 10, 5))
        screen.draw.rect(       Rect(160, 170, 400, 170), (255, 200, 0))

        screen.draw.text("GAME  OVER",
                         center=(WIDTH // 2, 210), color=(255, 80, 30), fontsize=50)
        screen.draw.text(f"Score: {score}     Best: {hi_score}",
                         center=(WIDTH // 2, 268), color=(255, 230, 180), fontsize=26)
        screen.draw.text("SPACE to play again",
                         center=(WIDTH // 2, 308), color=(180, 180, 180), fontsize=22)

pgzrun.go()