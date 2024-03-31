import numpy as np
import matplotlib.pyplot as plt

# Carica i dati dal file numpy
filename = input("Enter filename to load (without .npy extension): ")
data = np.load(filename + ".npy")

# Separare i dati
pitch0 = data[0]
pitch1 = data[1]


max_digits_after_decimal = 0
max_num = None
for num in pitch0:
    decimal_part = str(num).split('.')[1]  # Ottieni la parte decimale come stringa
    num_digits_after_decimal = len(decimal_part)
    if num_digits_after_decimal > max_digits_after_decimal:
        max_digits_after_decimal = num_digits_after_decimal
        max_num = num
if max_num is not None:
    print("Il numero con più cifre dopo la virgola è:", max_num)

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
