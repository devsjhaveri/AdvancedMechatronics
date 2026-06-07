import pgzrun
import serial
import math

PORT = '/dev/tty.usbmodem1101'  
BAUD = 115200

WIDTH = 800
HEIGHT = 600

angle = 0
force = 0

ser = serial.Serial(PORT, BAUD)
ser.timeout = 0.01 

def update():
    global angle, force
    try:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            parts = line.split(',')
            if len(parts) == 2:
                angle = int(parts[0])
                force = int(parts[1])
    except:
        pass

def draw():
    screen.clear()
    screen.fill((30, 30, 30))

    screen.draw.text("HW17 - Haptic Paddle", (20, 20), fontsize=30, color='white')

    cx, cy = 250, 320
    radius = 150
    angle_deg = (angle / 4096.0) * 360.0
    angle_rad = math.radians(angle_deg)
    ex = cx + radius * math.sin(angle_rad)
    ey = cy - radius * math.cos(angle_rad)

    screen.draw.circle((cx, cy), radius, 'gray')
    screen.draw.line((cx, cy), (int(ex), int(ey)), 'cyan')
    screen.draw.filled_circle((cx, cy), 8, 'white')
    screen.draw.text(f"Angle: {angle} ({angle_deg:.1f})", (cx-80, cy+170), fontsize=22, color='cyan')

    bx, by = 580, 150
    bw, bh = 80, 300
    max_force = 20000
    normalized = max(-1.0, min(1.0, force / max_force))

    screen.draw.rect(Rect(bx, by, bw, bh), 'gray')

    if normalized >= 0:
        bar_h = int(normalized * bh / 2)
        if bar_h > 0:
            screen.draw.filled_rect(Rect(bx, by + bh//2 - bar_h, bw, bar_h), 'green')
    else:
        bar_h = int(-normalized * bh / 2)
        if bar_h > 0:
            screen.draw.filled_rect(Rect(bx, by + bh//2, bw, bar_h), 'red')

    screen.draw.line((bx, by + bh//2), (bx + bw, by + bh//2), 'white')
    screen.draw.text(f"Force: {force}", (bx - 20, by + bh + 20), fontsize=22, color='yellow')

pgzrun.go()