"""
ME 433 HW10 - Pico Button Code (CircuitPython)
===============================================
Wiring:
  - One leg of button  →  GP15  (or any GP pin, update BUTTON_PIN below)
  - Other leg of button →  GND

Protocol:
  - Sends "1\n" over USB serial each time the button is PRESSED (edge detect)
  - The game reads this and triggers a dinosaur jump / restart

Copy this file to the Pico as 'code.py'
"""

import board
import digitalio
import time

# ── Configure your button pin here ──────────────────────────────────────────
BUTTON_PIN = board.GP15

# ── Set up the button with internal pull-up ──────────────────────────────────
# Button is LOW when pressed (connected to GND)
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull      = digitalio.Pull.UP

# ── State for edge detection ─────────────────────────────────────────────────
prev_state = True     # True = not pressed (pull-up HIGH)

print("Pico ready - press button to send jump command")

# ── Main loop ────────────────────────────────────────────────────────────────
while True:
    current_state = button.value          # True = HIGH (not pressed)

    # Detect falling edge: was HIGH, now LOW → button just pressed
    if prev_state and not current_state:
        print("1")                        # game reads this as a jump command

    prev_state = current_state
    time.sleep(0.02)                      # 20 ms debounce (50 Hz poll rate)