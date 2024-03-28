import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
from scipy.signal import medfilt
from scipy.ndimage import gaussian_filter1d



# Carica i dati dal file numpy
filename = input("Enter filename to load (without .npy extension): ")
data = np.load(filename + ".npy")

# Separare i dati
pitch0 = data[0]
pitch1 = data[1]


# Calcola il numero di campioni
num_samples = len(pitch0)


sampleInWindow = 15
numWindow = int(len(pitch1)/sampleInWindow)

if (len(pitch1)/sampleInWindow) > numWindow:
    numWindow = numWindow + 1
    samples = 15 * numWindow
    currLen = len(pitch1)
    pad = samples - currLen 
    np.pad(pitch1, (0, pad), mode='constant', constant_values=0)


# simulo 15 finestre di campioni
signal1 = []
for i in range(numWindow):
    arr = []
    for j in range(sampleInWindow):
        index = 15*i + j
        if pitch1[index] > 0:
            arr.append(pitch1[j])
        else:
            arr.append(0)
    signal1.append(arr)


def method1(numWindows, windows):

    peaks1 = np.full(numWindow*15, -50)

    peak = 0.0

    for i in range(numWindows):
        last = peak
        # trovo il nuovo massimo nella finestra
        peak = np.max(windows[i])
        current = peak
        # se il nuovo massimo è minore del precedente ho un picco
        if last > current: 
            print("dentro")
            peak = 0.0
            # quindi resetto il massimo
            if i != 0:
                peak_index = np.argmax(windows[i-1])
                global_index = (i-1) * 15 + peak_index
                peaks1[global_index] = last
        # altrimenti ho ag-giornato il nuovo massimo
                
    return peaks1

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

def method3(pitch_data, sample_rate):
    smoothed_data = []
    for i in range(0, len(pitch_data), sampleInWindow):
        window = pitch_data[i:i + sampleInWindow]
        
        # Applica un filtro gaussiano per lo smoothing
        # smoothed_window = gaussian_filter1d(window, sigma=2)
        smoothed_window = window
        
        # Controlla la lunghezza del vettore smoothed_window prima di applicare filtfilt
        if len(smoothed_window) > sampleInWindow:
            # Definiamo il filtro Butterworth passa-basso
            order = 4
            cutoff_freq = 5  # Frequenza di taglio del filtro in Hz, regolare in base alle tue esigenze
            nyquist_freq = sample_rate / 2  # Frequenza di Nyquist
            normal_cutoff = cutoff_freq / nyquist_freq
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
        
            # Applicare il filtro passa-basso dopo il filtro gaussiano
            smoothed_window = filtfilt(b, a, smoothed_window)
        
            smoothed_data.extend(smoothed_window)
    
    # Trova i picchi nei dati filtrati
    peaks = method2(smoothed_data)
    return peaks

sample_rate = 120 

# calcolo i picchi del segnale basandomi sull'arrivo di una finestra alla volta
peaks1 = method1(numWindow, signal1)
peaks2 = method2(pitch1)
peaks3 = method3(pitch1, sample_rate)


# Crea un array di tempo in base al numero di campioni e alla frequenza di campionamento
 # Assumi una frequenza di campionamento di 120 Hz
time1 = np.arange(len(pitch1)) / sample_rate
time2 = np.arange(len(peaks1)) / sample_rate

# Plot the complete signal
plt.figure(figsize=(10, 6))
plt.plot(time1, pitch1, label='Original Signal')

# plt.scatter(time1, pitch1, color='blue', label='Detected Peaks')

# plt.scatter(time2, peaks1, color='red', label='Detected Peaks')

time_peaks2 = np.array(peaks2) / sample_rate
time_peaks3 = np.array(peaks3) / sample_rate

# plt.scatter(time_peaks2, pitch1[peaks2], color='green', label='Detected Peaks')
plt.scatter(time_peaks3, pitch1[peaks3], color='green', label='Detected Peaks')



plt.title('Signal with Detected Peaks')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
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