import numpy as np
import matplotlib.pyplot as plt

def plot_signals_from_npy(filename):
    # Load data from the .npy file
    data = np.load(filename, allow_pickle=True).item()

    # Extract signals and sampling frequency
    signals = data['signals']
    Fs = data['Fs']

    # Calculate signal duration based on signal lengths and sampling frequency
    duration = signals.shape[1] / Fs

    # Create a time array for plotting
    time = np.linspace(0, duration, signals.shape[1])

    # Plot the signals
    plt.figure(figsize=(10, 6))
    plt.plot(time, signals[0], label='Signal 1')
    plt.plot(time, signals[1], label='Signal 2')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Signals')
    plt.legend()
    plt.grid(True)
    plt.show()

# Input the path of the .npy file from the user
filename = input("Enter the path of the .npy file: ")
plot_signals_from_npy(filename)
