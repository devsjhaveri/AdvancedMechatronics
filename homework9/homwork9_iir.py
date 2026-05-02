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

AA = 0.95
BA = 0.05
AB = 0.95
BB = 0.05
AD = 0.95
BD = 0.05

iir_dataA = [0] * len(dataA)
for i in range(1, len(dataA)):
    iir_dataA[i] = AA * iir_dataA[i-1] + BA * dataA[i]

Fs_A = len(t_A) / (t_A[-1] - t_A[0])
n_A = len(dataA)
k_A = np.arange(n_A)
frq_A = k_A / (n_A / Fs_A)
frq_A = frq_A[range(int(n_A/2))]
Y_A = np.fft.fft(dataA) / n_A
Y_A = Y_A[range(int(n_A/2))]
Y_A_filtered = np.fft.fft(iir_dataA) / n_A
Y_A_filtered = Y_A_filtered[range(int(n_A/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_A, dataA, 'k')
ax1.plot(t_A, iir_dataA, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigA A={AA} B={BA}')
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

iir_dataB = [0] * len(dataB)
for i in range(1, len(dataB)):
    iir_dataB[i] = AB * iir_dataB[i-1] + BB * dataB[i]

Fs_B = len(t_B) / (t_B[-1] - t_B[0])
n_B = len(dataB)
k_B = np.arange(n_B)
frq_B = k_B / (n_B / Fs_B)
frq_B = frq_B[range(int(n_B/2))]
Y_B = np.fft.fft(dataB) / n_B
Y_B = Y_B[range(int(n_B/2))]
Y_B_filtered = np.fft.fft(iir_dataB) / n_B
Y_B_filtered = Y_B_filtered[range(int(n_B/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_B, dataB, 'k')
ax1.plot(t_B, iir_dataB, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigB A={AB} B={BB}')
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

iir_dataD = [0] * len(dataD)
for i in range(1, len(dataD)):
    iir_dataD[i] = AD * iir_dataD[i-1] + BD * dataD[i]

Fs_D = len(t_D) / (t_D[-1] - t_D[0])
n_D = len(dataD)
k_D = np.arange(n_D)
frq_D = k_D / (n_D / Fs_D)
frq_D = frq_D[range(int(n_D/2))]
Y_D = np.fft.fft(dataD) / n_D
Y_D = Y_D[range(int(n_D/2))]
Y_D_filtered = np.fft.fft(iir_dataD) / n_D
Y_D_filtered = Y_D_filtered[range(int(n_D/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t_D, dataD, 'k')
ax1.plot(t_D, iir_dataD, 'r')
ax1.set_xlabel('Time')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigD A={AD} B={BD}')
ax2.loglog(frq_D, abs(Y_D), 'k')
ax2.loglog(frq_D, abs(Y_D_filtered), 'r')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('|Y(freq)|')
ax2.set_title('sigD - FFT')
plt.tight_layout()

sample_rateA = len(dataA) / (t_A[-1] - t_A[0])
print(sample_rateA)
sample_rateB = len(dataB) / (t_B[-1] - t_B[0])
print(sample_rateB)
sample_rateD = len(dataD) / (t_D[-1] - t_D[0])
print(sample_rateD)

plt.show(block=True)


