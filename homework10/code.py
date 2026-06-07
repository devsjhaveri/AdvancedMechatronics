import board
import digitalio
import time

BUTTON_PIN = board.GP19

button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull      = digitalio.Pull.UP

prev_state = True    

print("Pico ready - press button to send jump command")

while True:
    current_state = button.value          

    if prev_state and not current_state:
        print("1")                  

    prev_state = current_state
    time.sleep(0.02)         