import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def calculate_proportional_gaussian_positive(data, sigma):
    data_array = np.array(data)  # Converti i dati in formato di array numpy
    positive_data = np.maximum(data_array, 0)  # Rimuovi i valori negativi
    filtered_positive_data = gaussian_filter1d(positive_data, sigma)
    filtered_data = data_array.copy()  # Copia dei dati originali
    filtered_data[data_array > 0] = filtered_positive_data[data_array > 0]  # Mantieni i valori positivi filtrati
    return filtered_data.tolist()  # Converti i dati filtrati in formato di lista

def enlarge_numbers(numbers):
    enlarged_numbers = []
    for num in numbers:
        if num > 0:
            enlarged_numbers.append(num ** 1)  # Eleva al quadrato solo i numeri positivi
        else:
            enlarged_numbers.append(num)  # Mantieni gli zeri e i numeri negativi invariati
    return enlarged_numbers

# Carica i dati dal file numpy
filename = input("Enter filename to load (without .npy extension): ")
data = np.load(filename + ".npy")

# Separare i dati
pitch0 = enlarge_numbers(data[0])
pitch1 = enlarge_numbers(data[1])

# Calcola l'interquartile range dei dati
Q1_pitch0, Q3_pitch0 = np.percentile(pitch0, [25, 75])
IQR_pitch0 = Q3_pitch0 - Q1_pitch0

Q1_pitch1, Q3_pitch1 = np.percentile(pitch1, [25, 75])
IQR_pitch1 = Q3_pitch1 - Q1_pitch1

# Usa l'interquartile range come parametro sigma per il filtro gaussiano
sigma_pitch0 = IQR_pitch0 / 1.349  # Scala l'IQR per adattarlo alla distribuzione gaussiana
sigma_pitch1 = IQR_pitch1 / 1.349

# Applica il filtro gaussiano proporzionale solo quando il segnale è positivo
filtered_pitch0 = calculate_proportional_gaussian_positive(pitch0, sigma_pitch0)
filtered_pitch1 = calculate_proportional_gaussian_positive(pitch1, sigma_pitch1)

# Calcola il numero di campioni
num_samples = len(pitch0)

# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
sample_rate = 120  # Assumi una frequenza di campionamento di 120 Hz
time = np.arange(num_samples) / sample_rate

# Plot dei dati
plt.figure(figsize=(10, 6))
plt.plot(time, filtered_pitch0, label='Filtered Pitch 0')
plt.plot(time, filtered_pitch1, label='Filtered Pitch 1')
plt.title(filename)
plt.xlabel('Time (s)')
plt.ylabel('Pitch')
plt.legend()
plt.grid(True)
plt.show()
