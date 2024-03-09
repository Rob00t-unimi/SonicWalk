import numpy as np
import matplotlib.pyplot as plt

# Carica i dati dal file numpy
# filename = input("Enter filename to load (without .npy extension): ")
data = np.load("unknown" + ".npy")

# Separare i dati
pitch0 = abs(data[0]) - 5
pitch1 = abs(data[1]) - 5

# Calcola il numero di campioni
num_samples = len(pitch0)

# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
sample_rate = 120  # Assumi una frequenza di campionamento di 120 Hz
time = np.arange(num_samples) / sample_rate

# Calcola la FFT per entrambi i segnali
fft_pitch0 = np.fft.fft(pitch0)
fft_pitch1 = np.fft.fft(pitch1)

# Calcola il modulo della FFT
fft_pitch0_mod = np.abs(fft_pitch0)
fft_pitch1_mod = np.abs(fft_pitch1)

# Crea un array di frequenze
frequencies = np.fft.fftfreq(num_samples, d=1/sample_rate)

# Plot dei dati
plt.figure(figsize=(14, 12))

# Plot del segnale 0
plt.subplot(2, 2, 1)
plt.plot(time, pitch0, label='Pitch 0')
plt.title("Signal 0 (Entire)")
plt.xlabel('Time (s)')
plt.ylabel('Pitch')
plt.legend()
plt.grid(True)

# Plot della FFT per il segnale 0
plt.subplot(2, 2, 2)
plt.plot(frequencies, fft_pitch0_mod)
plt.title("FFT of Signal 0 (Entire)")
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True)

# Plot del segnale 1
plt.subplot(2, 2, 3)
plt.plot(time, pitch1, label='Pitch 1')
plt.title("Signal 1 (Entire)")
plt.xlabel('Time (s)')
plt.ylabel('Pitch')
plt.legend()
plt.grid(True)

# Plot della FFT per il segnale 1
plt.subplot(2, 2, 4)
plt.plot(frequencies, fft_pitch1_mod)
plt.title("FFT of Signal 1 (Entire)")
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True)

plt.tight_layout()
plt.show()


# Salva le FFT in un file numpy
np.save("fft_signals.npy", [fft_pitch0, fft_pitch1])

print("FFT saved successfully.")