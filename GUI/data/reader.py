import numpy as np
import matplotlib.pyplot as plt

def plot_signals_from_npy(filename):
    # Carica i dati dal file .npy
    data = np.load(filename, allow_pickle=True).item()

    # Estrae i segnali e la frequenza di campionamento
    signals = data['signals']
    Fs = data['Fs']

    # Calcola la durata del segnale in base alla lunghezza dei segnali e la frequenza di campionamento
    duration = signals.shape[1] / Fs

    # Crea un array di tempo per il plot
    time = np.linspace(0, duration, signals.shape[1])

    # Plot dei segnali
    plt.figure(figsize=(10, 6))
    plt.plot(time, signals[0], label='Signal 1')
    plt.plot(time, signals[1], label='Signal 2')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Signals')
    plt.legend()
    plt.grid(True)
    plt.show()

# Esempio di utilizzo
filename = 'YOUR_FILENAME'  # Specifica il percorso del tuo file .npy
plot_signals_from_npy(filename)
