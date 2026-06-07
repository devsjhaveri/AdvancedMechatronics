
import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plt
import time

SERIAL_PORT  = None      
BAUD_RATE    = 115200
N_SAMPLES    = 400
TIMEOUT_SEC  = 30

def find_pico_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if p.vid == 0x2E8A:
            return p.device
    if ports:
        print(f"[WARNING] Could not identify Pico by VID. Using first port: {ports[0].device}")
        return ports[0].device
    raise RuntimeError("No serial ports found. Is the Pico plugged in?")

def main():
    port = SERIAL_PORT or find_pico_port()
    print(f"Connecting to {port} at {BAUD_RATE} baud...")

    with serial.Serial(port, BAUD_RATE, timeout=TIMEOUT_SEC) as ser:
        time.sleep(0.5)
        ser.reset_input_buffer()

        cmd = f"{N_SAMPLES}\n"
        ser.write(cmd.encode())
        print(f"Sent: collect {N_SAMPLES} samples")

        raw_vals      = []
        filtered_vals = []
        timestamps    = []

        print("Waiting for data...", flush=True)

        while len(raw_vals) < N_SAMPLES:
            line = ser.readline().decode().strip()
            if not line:
                print("[ERROR] Empty line / timeout. Stopping.")
                break

            if line.startswith("DBG"):
                print(f"[DEBUG] {line}")
                continue

            if line.startswith("DATA"):
                parts = line.split()
                if len(parts) != 4:
                    print(f"[WARNING] Unexpected DATA format: '{line}' – skipping")
                    continue
                try:
                    raw_vals.append(int(parts[1]))
                    filtered_vals.append(float(parts[2]))
                    timestamps.append(int(parts[3]))
                except ValueError:
                    print(f"[WARNING] Could not parse: '{line}' – skipping")
                    continue

                if len(raw_vals) % 80 == 0:
                    print(f"  Received {len(raw_vals)} / {N_SAMPLES} samples...")

    if len(raw_vals) < 2:
        print("Not enough data received. Exiting.")
        return

    print(f"Received {len(raw_vals)} samples. Plotting...")

    t = np.array(timestamps, dtype=float)
    t = (t - t[0]) / 1000.0

    raw  = np.array(raw_vals,      dtype=float)
    filt = np.array(filtered_vals, dtype=float)

    dt      = np.mean(np.diff(t))
    fs      = 1.0 / dt
    nyquist = fs / 2.0
    print(f"Estimated fs = {fs:.1f} Hz  (Nyquist = {nyquist:.1f} Hz)")

    N        = len(raw)
    freqs    = np.fft.rfftfreq(N, d=dt)
    fft_raw  = np.abs(np.fft.rfft(raw  - raw.mean()))  / N
    fft_filt = np.abs(np.fft.rfft(filt - filt.mean())) / N

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("HW14 – HX711 Force Sensor Data", fontsize=14)

    axes[0, 0].plot(t, raw, color="tab:blue", linewidth=0.8)
    axes[0, 0].set_title("Raw Signal vs Time")
    axes[0, 0].set_xlabel("Time (s)")
    axes[0, 0].set_ylabel("ADC counts")
    axes[0, 0].grid(True, alpha=0.4)

    axes[0, 1].plot(t, filt, color="tab:orange", linewidth=0.8)
    axes[0, 1].set_title("IIR Filtered Signal vs Time")
    axes[0, 1].set_xlabel("Time (s)")
    axes[0, 1].set_ylabel("ADC counts")
    axes[0, 1].grid(True, alpha=0.4)

    axes[1, 0].plot(freqs, fft_raw, color="tab:blue", linewidth=0.8)
    axes[1, 0].set_title("FFT of Raw Signal")
    axes[1, 0].set_xlabel("Frequency (Hz)")
    axes[1, 0].set_ylabel("Magnitude")
    axes[1, 0].set_xlim(0, nyquist)
    axes[1, 0].axvline(25, color="red", linestyle="--", alpha=0.6, label="25 Hz")
    axes[1, 0].axvline(30, color="red", linestyle=":",  alpha=0.6, label="30 Hz")
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(True, alpha=0.4)

    axes[1, 1].plot(freqs, fft_filt, color="tab:orange", linewidth=0.8)
    axes[1, 1].set_title("FFT of IIR Filtered Signal")
    axes[1, 1].set_xlabel("Frequency (Hz)")
    axes[1, 1].set_ylabel("Magnitude")
    axes[1, 1].set_xlim(0, nyquist)
    axes[1, 1].axvline(25, color="red", linestyle="--", alpha=0.6, label="25 Hz")
    axes[1, 1].axvline(30, color="red", linestyle=":",  alpha=0.6, label="30 Hz")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, alpha=0.4)

    plt.tight_layout()
    plt.savefig("HW14_data.png", dpi=150)
    print("Figure saved to HW14_data.png")
    plt.show()


if __name__ == "__main__":
    main()