import serial
import matplotlib.pyplot as plt
import time

PORT = '/dev/tty.usbmodem101'
BAUD = 115200

ser = serial.Serial(PORT, BAUD)
time.sleep(1.5)
print("Connected — waiting for data...")

indices, desired, actual = [], [], []

while True:
    line = ser.readline().decode().strip()
    print(line)
    if line == 'index,desired,actual':
        break

while True:
    line = ser.readline().decode().strip()
    print(line)
    if line.startswith('Done'):
        break
    parts = line.split(',')
    if len(parts) == 3:
        indices.append(int(parts[0]))
        desired.append(float(parts[1]))
        actual.append(float(parts[2]))

ser.close()

plt.plot(indices, desired, label='desired')
plt.plot(indices, actual, label='actual')
plt.xlabel('sample')
plt.ylabel('current (mA)')
plt.legend()
plt.title('PI current controller')
plt.show()