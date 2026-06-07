import pwmio
import board
from time import sleep

pwm = pwmio.PWMOut(board.GP16, frequency=50)

def sweepServo():
    for duty in range(3277, 6554, 100):
        pwm.duty_cycle = duty
        sleep(0.1)
    for duty in range(6554, 3277, -100):
        pwm.duty_cycle = duty
        sleep(0.1)
        
while True:
    sweepServo()