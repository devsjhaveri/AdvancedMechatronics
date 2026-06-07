import serial
import matplotlib.pyplot as plt
import time

PORT = '/dev/tty.usbmodem1102'
BAUD = 115200

ser = serial.Serial(PORT, BAUD)
time.sleep(1.5)
print("Connected — sending a")
ser.write(b'a')

indices, desired, actual = [], [], []

for _ in range(400):
    line = ser.readline().decode().strip()
    print(line)
    parts = line.split()
    if len(parts) == 3:
        indices.append(int(parts[0]))
        desired.append(int(parts[1]))
        actual.append(int(parts[2]))

ser.close()

plt.plot(indices, desired, label='desired')
plt.plot(indices, actual, label='actual')
plt.xlabel('sample')
plt.ylabel('current (raw units)')
plt.legend()
plt.title('PI current controller')
plt.show()