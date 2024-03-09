import numpy as np
import matplotlib.pyplot as plt

# Carica i dati dal file numpy
#filename = input("Enter filename to load (without .npy extension): ")
data = np.load("swing" + ".npy")

# Separar
# e i dati
pitch0 = data[0]
pitch1 = data[1]

# Calcola il numero di campioni
num_samples = len(pitch0)

# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
sample_rate = 120  # Assumi una frequenza di campionamento di 120 Hz
time = np.arange(num_samples) / sample_rate

# Calcola il tempo di inizio
start_time = 10  # secondi

# Trova l'indice corrispondente al tempo di inizio
start_index = int(start_time * sample_rate)

# Plot dei dati a partire dal tempo di inizio
plt.figure(figsize=(10, 6))
plt.plot(time[start_index:], pitch0[start_index:], label='Pitch 0')
plt.plot(time[start_index:], pitch1[start_index:], label='Pitch 1')
plt.title("swing")
plt.xlabel('Time (s)')
plt.ylabel('Pitch')
plt.legend()
plt.grid(True)
plt.show()
