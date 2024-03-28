import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
from scipy.signal import medfilt
from scipy.ndimage import gaussian_filter1d

# Carica i dati dal file numpy
filename = input("Enter filename to load (without .npy extension): ")
data = np.load(filename + ".npy")

# Separare i dati
# pitch0 = data[0]
pitch1 = data[1]

# Calcola il numero di campioni
num_samples = len(pitch1)

sampleInWindow = 15
numWindow = int(len(pitch1) / sampleInWindow)

if (len(pitch1) / sampleInWindow) > numWindow:
    numWindow = numWindow + 1
    samples = 15 * numWindow
    currLen = len(pitch1)
    pad = samples - currLen
    np.pad(pitch1, (0, pad), mode='constant', constant_values=0)

def applyGaussianFilter(pitch1):
    newPitch1 = []
    for i in range(0, len(pitch1), sampleInWindow):
        window = pitch1[i:i + sampleInWindow]
        window = gaussian_filter1d(window, sigma=2)
        for sample in window:
            newPitch1.append(sample)

    return np.array(newPitch1)

# pitch1 = applyGaussianFilter(pitch1)


def method1(pitch_data):
    peaks = []
    num_windows = len(pitch_data) // sampleInWindow

    for i in range(num_windows):
        window = pitch_data[i * sampleInWindow: (i + 1) * sampleInWindow]
        window_max = np.max(window)
        if i > 0:
            prev_window = pitch_data[(i - 1) * sampleInWindow: i * sampleInWindow]
            prev_max = np.max(prev_window)
            if window_max < prev_max:
                peak_index = (i - 1) * sampleInWindow + np.argmax(prev_window)
                peaks.append(peak_index)
    return peaks

def method2(pitch_data):
    peaks = []
    prev_max = -np.inf  # Massimo della finestra precedente
    for i in range(0, len(pitch_data), sampleInWindow):
        window = pitch_data[i:i + sampleInWindow]  # Prendi una finestra di 15 campioni
        window_max = np.max(window)  # Trova il massimo della finestra corrente
        if window_max < prev_max:  # Se il massimo della finestra corrente è minore del massimo precedente
            peak_index = i - sampleInWindow + np.argmax(pitch_data[i - sampleInWindow:i])  # Trova l'indice del picco
            peaks.append(peak_index)  # Aggiungi l'indice del picco alla lista dei picchi
        prev_max = max(window_max, prev_max)  # Aggiorna il massimo precedente
    return peaks


# def method3(pitch_data, sample_rate):
#     smoothed_data = []
#     for i in range(0, len(pitch_data), sampleInWindow):
#         window = pitch_data[i:i + sampleInWindow]
#         # Applica un filtro gaussiano per lo smoothing
#         # smoothed_window = gaussian_filter1d(window, sigma=2)
#         smoothed_window = window
#         # Controlla la lunghezza del vettore smoothed_window prima di applicare filtfilt
#         if len(smoothed_window) > sampleInWindow:
#             # Definiamo il filtro Butterworth passa-basso
#             order = 4
#             cutoff_freq = 5  # Frequenza di taglio del filtro in Hz, regolare in base alle tue esigenze
#             nyquist_freq = sample_rate / 2  # Frequenza di Nyquist
#             normal_cutoff = cutoff_freq / nyquist_freq
#             b, a = butter(order, normal_cutoff, btype='low', analog=False)
#             # Applicare il filtro passa-basso dopo il filtro gaussiano
#             smoothed_window = filtfilt(b, a, smoothed_window)
#             smoothed_data.extend(smoothed_window)
#     # Trova i picchi nei dati filtrati
#     peaks = method2(smoothed_data)
#     return peaks


def method4(pitch_data):
    peaks = []
    lag = 4  # Numero di punti dati per calcolare la media mobile e la deviazione standard mobile
    threshold = 3.6  # Numero di deviazioni standard sopra il quale viene generato un segnale
    influence = 1  # Influenza dei nuovi segnali sul calcolo della media e della deviazione standard
    signals = np.zeros(len(pitch_data))
    filtered_data = np.zeros(len(pitch_data))
    avg_filter = np.zeros(len(pitch_data))
    std_filter = np.zeros(len(pitch_data))
    avg_filter[lag] = np.mean(pitch_data[:lag])
    std_filter[lag] = np.std(pitch_data[:lag])
    for i in range(lag + 1, len(pitch_data)):
        if abs(pitch_data[i] - avg_filter[i - 1]) > threshold * std_filter[i - 1]:
            if pitch_data[i] > avg_filter[i - 1]:
                signals[i] = 1  # Segnale positivo
            else:
                signals[i] = -1  # Segnale negativo
            filtered_data[i] = influence * pitch_data[i] + (1 - influence) * filtered_data[i - 1]
        else:
            signals[i] = 0  # Nessun segnale
            filtered_data[i] = pitch_data[i]
        avg_filter[i] = np.mean(filtered_data[i - lag + 1:i + 1])
        std_filter[i] = np.std(filtered_data[i - lag + 1:i + 1])
    # Trova gli indici dei picchi nei segnali
    peak_indices = np.where(signals != 0)[0]
    # Aggiungi gli indici dei picchi corretti
    for idx in peak_indices:
        peaks.append(idx)
    return peaks


# def method5(pitch_data):
#     peaks = []
#     for i in range(0, len(pitch_data), sampleInWindow):
#         window = pitch_data[i:i + sampleInWindow]
#         # Simula lo stream di dati in tempo reale
#         # Ogni volta che arriva una nuova finestra, chiama l'AMPD per trovare i picchi
#         window_peaks = AMPD(window)
#         # Aggiungi gli indici dei picchi rilevati nella finestra corrente agli indici globali
#         peaks.extend([i + idx for idx in window_peaks])
#     return peaks

# def AMPD(data):
#     n = len(data)
#     ampd_score = [0] * n

#     # Passo 1: Calcola le differenze tra i punti adiacenti
#     diff = np.diff(data)

#     # Passo 2: Inizializza il vettore che contiene il numero di picchi
#     num_peaks = np.zeros(n)

#     # Passo 3: Calcola il valore di ampd per ogni dimensione della finestra
#     for m in range(1, n):
#         # Calcola la matrice delle differenze per ogni dimensione della finestra
#         diff_matrix = np.zeros((n - m, m))
#         for i in range(n - m):
#             diff_matrix[i] = np.abs(diff[i:i + m])

#         # Calcola il valore di ampd per la dimensione della finestra corrente
#         ampd_score[m] = np.mean(np.min(diff_matrix, axis=1))

#     # Passo 4: Seleziona la dimensione della finestra ottimale
#     optimal_window_size = np.argmax(ampd_score)

#     # Passo 5: Trova i picchi utilizzando la finestra ottimale
#     for i in range(1, n - optimal_window_size):
#         diff_window = np.abs(data[i:i + optimal_window_size] - data[i - 1])
#         num_peaks[i + optimal_window_size // 2] = np.sum(diff_window > ampd_score[optimal_window_size])

#     peaks = np.where(num_peaks > 0)[0]

#     return peaks

# def AMPD(data):
#     # Implementa qui l'algoritmo AMPD
#     # Questa è una versione semplificata dell'AMPD che trova solo i massimi locali
#     # Adatta l'implementazione in base alle tue esigenze specifiche
#     peaks = []
#     for i in range(1, len(data) - 1):
#         if data[i] > data[i - 1] and data[i] > data[i + 1]:
#             peaks.append(i)
#         elif data[i] < data[i - 1] and data[i] < data[i + 1]:
#             peaks.append(i)
#     return peaks

def method5(pitch_data):
    peaks = []
    previous = [0]
    old = [0]
    for i in range(0, len(pitch_data), sampleInWindow):

        window = pitch_data[i:i + sampleInWindow]

        if i > 2:
            # Simula lo stream di dati in tempo reale
            # Ogni volta che arriva una nuova finestra, chiama l'AMPD per trovare i picchi
            window_peaks = Personal(window, previous, old)
            # Aggiungi gli indici dei picchi rilevati nella finestra corrente agli indici globali
            peaks.extend([i + idx for idx in window_peaks])

        old = previous
        previous = window


    return peaks

def Personal(data, previous, old): # personal 

    peaks = []
    if np.max(previous) > np.max(old) and np.max(previous) > np.max(data):
        # il picco è in previous
        index = np.argmax(previous)
        peaks.append(index)
    elif  np.min(previous) < np.min(old) and np.min(previous) < np.min(data):
        # il picco è in previous
        index = np.argmax(previous)
        peaks.append(index)
    return peaks

# Calcola i picchi utilizzando il metodo 5 (simulazione flusso dati in tempo reale con AMPD)
peaks5 = method5(pitch1)


# finestra di picco s1
def method6(pitch_data):
    peaks = []
    for i in range(0, len(pitch_data), sampleInWindow):
        window = pitch_data[i:i + sampleInWindow]
        peak_index = i + np.argmax(window)
        peaks.append(peak_index)
    return peaks

# finestra di picco s2
def method7(pitch_data):
    peaks = []
    prev_max = -np.inf  # Massimo della finestra precedente
    for i in range(0, len(pitch_data), sampleInWindow):
        window = pitch_data[i:i + sampleInWindow]  # Prendi una finestra di 15 campioni
        window_max = np.max(window)  # Trova il massimo della finestra corrente
        if window_max < prev_max:  # Se il massimo della finestra corrente è minore del massimo precedente
            peak_index = i - sampleInWindow + np.argmax(pitch_data[i - sampleInWindow:i])  # Trova l'indice del picco
            peaks.append(peak_index)  # Aggiungi l'indice del picco alla lista dei picchi
        prev_max = max(window_max, prev_max)  # Aggiorna il massimo precedente
    return peaks

# finestra di picco s5 chebichev
def method8(pitch_data):
    peaks = []
    window_mean = np.mean(pitch_data[:sampleInWindow])
    window_std = np.std(pitch_data[:sampleInWindow])
    
    for i in range(0, len(pitch_data), sampleInWindow):
        window = pitch_data[i:i + sampleInWindow]
        threshold = window_mean + 3 * window_std  
        peak_candidates = np.where(window > threshold)[0]
        peaks.extend([i + idx for idx in peak_candidates])
        
        # Aggiorna la media e la deviazione standard
        window_mean = np.mean(window)
        window_std = np.std(window)
        
    return peaks




sample_rate = 120 

# Calcolo i picchi del segnale basandomi sull'arrivo di una finestra alla volta
peaks1 = method1(pitch1)
peaks2 = method2(pitch1)
# peaks3 = method3(pitch1, sample_rate)
peaks4 = method4(pitch1)
peaks5 = method5(pitch1)
peaks6 = method6(pitch1)
peaks7 = method7(pitch1)
peaks8 = method8(pitch1)

# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
# Assumi una frequenza di campionamento di 120 Hz
time1 = np.arange(len(pitch1)) / sample_rate

# Plot del segnale pitch1 per ogni metodo di rilevamento dei picchi
plt.figure(figsize=(15, 10))

# Metodo 1
plt.subplot(331)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks1], pitch1[peaks1], color='red', label=f'MY METHOD 1: {len(peaks1)}')
plt.title(f'Method 1: Signal with Detected Peaks ({len(peaks1)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 2
plt.subplot(332)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks2], pitch1[peaks2], color='green', label=f'Detected Peaks (Method 2): {len(peaks2)}')
plt.title(f'Method 2: Signal with Detected Peaks ({len(peaks2)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 4
plt.subplot(333)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks4], pitch1[peaks4], color='orange', label=f'Detected Peaks (Method 4): {len(peaks4)}')
plt.title(f'Method 4: Signal with Detected Peaks ({len(peaks4)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 5
plt.subplot(334)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks5], pitch1[peaks5], color='purple', label=f'MY METHOD 2: {len(peaks5)}')
plt.title(f'Method 5: Signal with Detected Peaks ({len(peaks5)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 6
plt.subplot(335)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks6], pitch1[peaks6], color='brown', label=f'Detected Peaks (Method 6): {len(peaks6)}')
plt.title(f'Method 6: Signal with Detected Peaks ({len(peaks6)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 7
plt.subplot(336)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks7], pitch1[peaks7], color='cyan', label=f'Detected Peaks (Method 7): {len(peaks7)}')
plt.title(f'Method 7: Signal with Detected Peaks ({len(peaks7)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

# Metodo 8
plt.subplot(337)
plt.plot(time1, pitch1, label='Original Signal')
plt.scatter(time1[peaks8], pitch1[peaks8], color='magenta', label=f'Detected Peaks (Method 8): {len(peaks8)}')
plt.title(f'Method 8: Signal with Detected Peaks ({len(peaks8)} Peaks)')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()




# modifichiamo il codice sopra: 
# una volta ottenuti pitch0 e pitch1 simuliamo un'applicazione real time che riceve solo 15 campioni alla volta
# l'applicazione dovrà occuparsi di trovare i punti di picco dei segnali.
# quando il segnale viene plottato vengono evidenziati i punti di picco trovati

# una strategia per trovarli sarebbe di prendere un valore che parte da zero e continuare ad aumentarlo sostituendolo con il massimo 
# della finestra successiva solo se quel massimo è maggiore del valore attuale
# quando si giunge ad uno zero crossing negativo allora significa che il picco era nel valore massimo registrato fino a quel momento
# si salva il picco e si resetta il valore a 0
# questo approccio però non va bene poichè rileva il picco solamente dopo aver rilevato lo zero crossing negativo. è troppo tardi!
# voglio rilevare il picco quando avviene o comunqe a distanza di pochissimo.

# un'altro approccio che mi è venuto in mente è che quando il valore massimo di una finestra è minore del valore massimo della finestra precedente
# allora ho un picco. se non lo è allora proseguo.
# questo consente di rilevare i picchi con ritardo di solamente una finestra, tuttavia, se c'è rumore rilevo picchi minuscoli inutilmente.

# altre strategie o miglioramenti su queste?

# Un approccio che potresti considerare è l'utilizzo di un filtro passa-alto per pre-processare i dati. 
# Questo tipo di filtro può essere efficace nel rimuovere il rumore a bassa frequenza e mettere in evidenza i cambiamenti rapidi nel segnale, come i picchi.