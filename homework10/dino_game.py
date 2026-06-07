"""
ME 433 HW10 - Dinosaur Runner (Pygame Zero)
============================================
Controls:
  - Pico button  → Jump / Restart after Game Over
  - SPACE key    → Fallback jump / restart (if Pico not connected)

Pico serial protocol:
  - Pico sends "1\n" each time the button is PRESSED (edge, not held)
  - Game reads that over USB serial and triggers a jump

Run with:  pgzrun dino_game.py
Or from VSCode (run button):  leave the pgzrun.go() at the bottom.
"""

import pgzrun
import random
import math
import wave
import struct
import os
import threading

# ── Try to import pyserial; game still works without it ──────────────────────
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[INFO] pyserial not found – using keyboard only (SPACE to jump)")

# ─────────────────────────────────────────────────────────────────────────────
# SERIAL CONFIG  ← change SERIAL_PORT to match your system
#   Windows:   'COM3'  (check Device Manager)
#   Mac/Linux: '/dev/ttyACM0'  or  '/dev/tty.usbmodem...'
# ─────────────────────────────────────────────────────────────────────────────
SERIAL_PORT = '/dev/tty.usbmodem1101'
BAUD_RATE   = 115200

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW
# ─────────────────────────────────────────────────────────────────────────────
WIDTH  = 800
HEIGHT = 300
TITLE  = "Dino Runner – ME433 HW10"

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE LOSE SOUND  (creates sounds/lose.wav next to this file)
# pgzero looks for sounds in a 'sounds/' folder beside the game file.
# ─────────────────────────────────────────────────────────────────────────────
def _generate_lose_sound():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    sounds_dir  = os.path.join(script_dir, 'sounds')
    sound_path  = os.path.join(sounds_dir, 'lose.wav')
    os.makedirs(sounds_dir, exist_ok=True)
    if os.path.exists(sound_path):
        return                                      # already generated

    sample_rate = 44100
    duration    = 0.6                              # seconds
    num_samples = int(sample_rate * duration)

    with wave.open(sound_path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(num_samples):
            t      = i / sample_rate
            # Descending pitch from 500 Hz → 150 Hz
            freq   = 500 - 580 * (t / duration)
            amp    = 0.6 * (1 - t / duration)     # fade out
            value  = int(32767 * amp * math.sin(2 * math.pi * freq * t))
            f.writeframes(struct.pack('<h', value))

_generate_lose_sound()

# ─────────────────────────────────────────────────────────────────────────────
# SERIAL READER  (background thread – non-blocking)
# ─────────────────────────────────────────────────────────────────────────────
_button_pressed = False          # set by serial thread, consumed by update()

def _serial_reader():
    global _button_pressed
    if not SERIAL_AVAILABLE:
        return
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[Serial] Connected on {SERIAL_PORT}")
        while True:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line == '1':
                    _button_pressed = True
            except Exception:
                pass
    except Exception as e:
        print(f"[Serial] Could not open {SERIAL_PORT}: {e}")
        print("[Serial] Falling back to SPACE key")

_serial_thread = threading.Thread(target=_serial_reader, daemon=True)
_serial_thread.start()

# ─────────────────────────────────────────────────────────────────────────────
# GAME CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
GROUND_Y       = 240        # y-coordinate of ground (dino's feet rest here)
DINO_X         = 90         # fixed horizontal position of dino
DINO_W, DINO_H = 42, 52     # dino bounding box

JUMP_VY        = -14.5      # initial upward velocity (negative = up in pgz)
GRAVITY        = 0.65       # pixels per frame² downward

OBS_W          = 22         # cactus width
OBS_SPEED_INIT = 5          # starting obstacle speed (px/frame)
SPEED_UP_EVERY = 600        # score ticks between speed increases
SPEED_INCREMENT= 0.4        # how much faster each time

# ─────────────────────────────────────────────────────────────────────────────
# GAME STATE  (all mutable in a dict so reset_game() is clean)
# ─────────────────────────────────────────────────────────────────────────────
def _fresh_state():
    return {
        'state'         : 'playing',   # 'playing' | 'game_over'
        'dino_y'        : float(GROUND_Y),
        'dino_vy'       : 0.0,
        'is_jumping'    : False,
        'obstacles'     : [],          # list of {'x': float, 'h': int}
        'clouds'        : [           # decorative clouds
            {'x': random.randint(100, 700), 'y': random.randint(30, 90)}
            for _ in range(4)
        ],
        'obs_timer'     : 0,
        'next_obs_at'   : random.randint(70, 130),
        'speed'         : OBS_SPEED_INIT,
        'score'         : 0,
        'hi_score'      : 0,
    }

G = _fresh_state()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _consume_button():
    """Returns True if button was pressed since last call, resets the flag."""
    global _button_pressed
    pressed       = _button_pressed
    _button_pressed = False
    return pressed

def _dino_rect():
    """Collision rect for the dinosaur (slightly inset for leniency)."""
    return Rect(DINO_X + 6, int(G['dino_y']) - DINO_H + 6,
                DINO_W - 12, DINO_H - 6)

def _obs_rect(obs):
    """Collision rect for an obstacle."""
    return Rect(int(obs['x']) + 3, GROUND_Y - obs['h'],
                OBS_W - 6, obs['h'])

def _collides():
    dr = _dino_rect()
    return any(dr.colliderect(_obs_rect(o)) for o in G['obstacles'])

# ─────────────────────────────────────────────────────────────────────────────
# UPDATE  (called every frame by pgzero, ~60 fps)
# ─────────────────────────────────────────────────────────────────────────────
def update():
    global G

    # Collect input: Pico button OR SPACE key
    jump_cmd = _consume_button() or keyboard.space

    # ── GAME OVER state ──────────────────────────────────────────────────────
    if G['state'] == 'game_over':
        if jump_cmd:
            hi = max(G['hi_score'], G['score'])
            G  = _fresh_state()
            G['hi_score'] = hi
        return

    # ── PLAYING state ────────────────────────────────────────────────────────

    # Jump
    if jump_cmd and not G['is_jumping']:
        G['dino_vy']   = JUMP_VY
        G['is_jumping'] = True

    # Physics
    G['dino_vy'] += GRAVITY
    G['dino_y']  += G['dino_vy']

    if G['dino_y'] >= GROUND_Y:          # landed
        G['dino_y']    = float(GROUND_Y)
        G['dino_vy']   = 0.0
        G['is_jumping'] = False

    # Spawn obstacles
    G['obs_timer'] += 1
    if G['obs_timer'] >= G['next_obs_at']:
        h = random.randint(28, 58)
        G['obstacles'].append({'x': float(WIDTH + 10), 'h': h})
        G['obs_timer']   = 0
        G['next_obs_at'] = random.randint(65, 120)

    # Move obstacles
    for obs in G['obstacles']:
        obs['x'] -= G['speed']
    G['obstacles'] = [o for o in G['obstacles'] if o['x'] > -OBS_W - 10]

    # Move clouds (slower for parallax feel)
    for cloud in G['clouds']:
        cloud['x'] -= G['speed'] * 0.25
        if cloud['x'] < -60:
            cloud['x'] = WIDTH + random.randint(20, 80)
            cloud['y'] = random.randint(30, 90)

    # Score & speed-up
    G['score'] += 1
    if G['score'] % SPEED_UP_EVERY == 0:
        G['speed'] = min(G['speed'] + SPEED_INCREMENT, 14)

    # Collision → game over
    if _collides():
        G['state'] = 'game_over'
        sounds.lose.play()

# ─────────────────────────────────────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _draw_cloud(x, y):
    """Draw a simple blocky cloud using filled rects."""
    screen.draw.filled_rect(Rect(x,      y + 8,  40, 14), (220, 220, 220))
    screen.draw.filled_rect(Rect(x + 8,  y,      24, 14), (220, 220, 220))
    screen.draw.filled_rect(Rect(x + 16, y - 6,  16, 12), (220, 220, 220))

def _draw_dino(y, is_jumping):
    """Draw a blocky pixel-art-ish dinosaur."""
    top   = int(y) - DINO_H
    left  = DINO_X
    green = (83, 168, 52)
    dark  = (52, 110, 30)

    # Body
    screen.draw.filled_rect(Rect(left,        top + 14, DINO_W,     DINO_H - 14), green)
    # Head
    screen.draw.filled_rect(Rect(left + 10,   top,      DINO_W - 2, 22),          green)
    # Snout
    screen.draw.filled_rect(Rect(left + 26,   top + 6,  14,         12),          green)
    # Eye (white + pupil)
    screen.draw.filled_rect(Rect(left + 26,   top + 4,  8,          8),           (255, 255, 255))
    screen.draw.filled_rect(Rect(left + 29,   top + 6,  4,          4),           (30,  30,  30))
    # Arm
    screen.draw.filled_rect(Rect(left + 8,    top + 28, 12,         8),           dark)
    # Legs (alternate if jumping)
    if is_jumping:
        screen.draw.filled_rect(Rect(left + 6,  top + DINO_H - 12, 12, 12), dark)
        screen.draw.filled_rect(Rect(left + 22, top + DINO_H - 16, 12, 12), dark)
    else:
        screen.draw.filled_rect(Rect(left + 6,  top + DINO_H - 18, 12, 18), dark)
        screen.draw.filled_rect(Rect(left + 22, top + DINO_H - 14, 12, 14), dark)
    # Tail
    screen.draw.filled_rect(Rect(left - 10,   top + 18, 14,         10),          green)
    screen.draw.filled_rect(Rect(left - 18,   top + 22, 10,         6),           green)

def _draw_cactus(obs):
    """Draw a blocky cactus obstacle."""
    x, h = int(obs['x']), obs['h']
    g  = GROUND_Y
    dk = (42, 100, 42)
    md = (60, 140, 60)

    # Main trunk
    screen.draw.filled_rect(Rect(x + 4,  g - h,      OBS_W - 8, h),       md)
    # Left arm
    arm_y = g - h + h // 3
    screen.draw.filled_rect(Rect(x - 8,  arm_y,       10,        12),      md)
    screen.draw.filled_rect(Rect(x - 8,  arm_y - 10,  10,        12),      md)
    # Right arm
    arm2_y = g - h + h // 2
    screen.draw.filled_rect(Rect(x + OBS_W - 2, arm2_y,    10, 12),       md)
    screen.draw.filled_rect(Rect(x + OBS_W - 2, arm2_y-10, 10, 12),       md)
    # Shading stripe
    screen.draw.filled_rect(Rect(x + 4,  g - h,      4,         h),        dk)

# ─────────────────────────────────────────────────────────────────────────────
# DRAW  (called every frame)
# ─────────────────────────────────────────────────────────────────────────────
def draw():
    # Sky background
    screen.fill((247, 247, 247))

    # Clouds
    for cloud in G['clouds']:
        _draw_cloud(int(cloud['x']), int(cloud['y']))

    # Ground line
    screen.draw.line((0, GROUND_Y), (WIDTH, GROUND_Y), (180, 180, 180))
    # Ground texture dots
    for gx in range(0, WIDTH, 40):
        screen.draw.filled_rect(Rect(gx, GROUND_Y + 2, 6, 3), (200, 200, 200))

    # Obstacles
    for obs in G['obstacles']:
        _draw_cactus(obs)

    # Dinosaur
    _draw_dino(G['dino_y'], G['is_jumping'])

    # Score
    display_score = G['score'] // 10
    screen.draw.text(f"SCORE  {display_score:05d}", (560, 16),
                     color=(80, 80, 80), fontsize=28)
    if G['hi_score'] > 0:
        screen.draw.text(f"HI  {G['hi_score'] // 10:05d}", (680, 16),
                         color=(160, 160, 160), fontsize=22)

    # Game over overlay
    if G['state'] == 'game_over':
        # Semi-transparent panel (solid rect approximation)
        screen.draw.filled_rect(Rect(200, 100, 400, 110), (230, 230, 230))
        screen.draw.rect(Rect(200, 100, 400, 110), (150, 150, 150))

        screen.draw.text("G A M E  O V E R",
                         center=(WIDTH // 2, 135),
                         color=(200, 50, 50), fontsize=42)
        screen.draw.text("Press Pico button (or SPACE) to restart",
                         center=(WIDTH // 2, 178),
                         color=(80, 80, 80), fontsize=20)

pgzrun.go()