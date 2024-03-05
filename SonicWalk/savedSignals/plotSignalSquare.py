import numpy as np
import matplotlib.pyplot as plt

def enlarge_numbers(numbers):
    enlarged_numbers = []
    for num in numbers:
        if num > 0:
            enlarged_numbers.append(num ** 1.5)  # Eleva al quadrato solo i numeri positivi
        else:
            enlarged_numbers.append(num)  # Mantieni gli zeri e i numeri negativi invariati
    return enlarged_numbers

# Carica i dati dal file numpy
filename = input("Enter filename to load (without .npy extension): ")
data = np.load(filename + ".npy")

# Separare i dati
pitch0 = enlarge_numbers(data[0])
pitch1 = enlarge_numbers(data[1])

# Calcola il numero di campioni
num_samples = len(pitch0)

# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
sample_rate = 120  # Assumi una frequenza di campionamento di 120 Hz
time = np.arange(num_samples) / sample_rate

# Plot dei dati
plt.figure(figsize=(10, 6))
plt.plot(time, pitch0, label='Pitch 0')
plt.plot(time, pitch1, label='Pitch 1')
plt.title(filename)
plt.xlabel('Time (s)')
plt.ylabel('Pitch')
plt.legend()
plt.grid(True)
plt.show()
