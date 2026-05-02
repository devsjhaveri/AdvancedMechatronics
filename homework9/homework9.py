import csv
import matplotlib.pyplot as plt
import numpy as np

plt.ion()

t_A = []
dataA = []
with open('sigA.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        t_A.append(float(row[0]))
        dataA.append(float(row[1]))

X_A = 100
X_B = 100
X_D = 50

averaged_dataA = []
for i in range(len(dataA)):
    if i < X_A:
        averaged_dataA.append(0)
    else:
        averaged_dataA.append(np.mean(dataA[i-X_A+1:i+1]))

Fs_A = len(t_A) / (t_A[-1] - t_A[0])
n_A = len(dataA)
k_A = np.arange(n_A)
frq_A = k_A / (n_A / Fs_A)
frq_A = frq_A[range(int(n_A/2))]
Y_A = np.fft.fft(dataA) / n_A
Y_A = Y_A[range(int(n_A/2))]
Y_A_filtered = np.fft.fft(averaged_dataA) / n_A
Y_A_filtered = Y_A_filtered[range(int(n_A/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_A, dataA, 'k')
ax1.plot(t_A, averaged_dataA, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigA MAF X={X_A}')
ax2.loglog(frq_A, abs(Y_A), 'k')
ax2.loglog(frq_A, abs(Y_A_filtered), 'r')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('|Y(freq)|')
ax2.set_title('sigA - FFT')
plt.tight_layout()

t_B = []
dataB = []
with open('sigB.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        t_B.append(float(row[0]))
        dataB.append(float(row[1]))

averaged_dataB = []
for i in range(len(dataB)):
    if i < X_B:
        averaged_dataB.append(0)
    else:
        averaged_dataB.append(np.mean(dataB[i-X_B+1:i+1]))

Fs_B = len(t_B) / (t_B[-1] - t_B[0])
n_B = len(dataB)
k_B = np.arange(n_B)
frq_B = k_B / (n_B / Fs_B)
frq_B = frq_B[range(int(n_B/2))]
Y_B = np.fft.fft(dataB) / n_B
Y_B = Y_B[range(int(n_B/2))]
Y_B_filtered = np.fft.fft(averaged_dataB) / n_B
Y_B_filtered = Y_B_filtered[range(int(n_B/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_B, dataB, 'k')
ax1.plot(t_B, averaged_dataB, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigB MAF X={X_B}')
ax2.loglog(frq_B, abs(Y_B), 'k')
ax2.loglog(frq_B, abs(Y_B_filtered), 'r')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('|Y(freq)|')
ax2.set_title('sigB - FFT')
plt.tight_layout()

t_D = []
dataD = []
with open('sigD.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        t_D.append(float(row[0]))
        dataD.append(float(row[1]))

averaged_dataD = []
for i in range(len(dataD)):
    if i < X_D:
        averaged_dataD.append(0)
    else:
        averaged_dataD.append(np.mean(dataD[i-X_D+1:i+1]))

Fs_D = len(t_D) / (t_D[-1] - t_D[0])
n_D = len(dataD)
k_D = np.arange(n_D)
frq_D = k_D / (n_D / Fs_D)
frq_D = frq_D[range(int(n_D/2))]
Y_D = np.fft.fft(dataD) / n_D
Y_D = Y_D[range(int(n_D/2))]
Y_D_filtered = np.fft.fft(averaged_dataD) / n_D
Y_D_filtered = Y_D_filtered[range(int(n_D/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_D, dataD, 'k')
ax1.plot(t_D, averaged_dataD, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigD MAF X={X_D}')
ax2.loglog(frq_D, abs(Y_D), 'k')
ax2.loglog(frq_D, abs(Y_D_filtered), 'r')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('|Y(freq)|')
ax2.set_title('sigD - FFT')
plt.tight_layout()

plt.show(block=True)