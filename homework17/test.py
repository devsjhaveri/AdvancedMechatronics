import serial

PORT = '/dev/tty.usbmodem1101'
BAUD = 115200

ser = serial.Serial(PORT, BAUD)
while True:
    line = ser.readline().decode().strip()
    print(line)