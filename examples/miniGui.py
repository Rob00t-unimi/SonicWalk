### funziona con mtw_modified ma ha dei problemi

## mtw_modified è stato modificato per avere un'attributo modificabile dall'esterno con mutua esclusione che serve per far partire e fermare la registrazione


import tkinter as tk
import sys
sys.path.append("../sonicwalk")
import time
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from mtw import MtwAwinda  # Assuming MtwAwinda is imported from the appropriate module

data = None
mtw_instance = None
duration = None

def start(mtw):
    mtw.mtwStartExecution()
    return


    
def start_Recording():
    start_button.config(state=tk.DISABLED)
    global data
    samplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2"
    with MtwAwinda(120, 19, samplesPath) as mtw:
        global mtw_instance
        global duration
        mtw_instance = mtw
        start(mtw)
        
        stop_button.config(state=tk.ACTIVE)

        inizio = time.time()

        data = mtw.mtwRecord(plot=False, analyze=True, exType=4)

        duration = time.time()-inizio
    
root = tk.Tk()
root.title("Recording Control")

mtw_label = tk.Label(root, text="Recording Control Panel", font=("Helvetica", 16))
mtw_label.pack(pady=10)

start_button = tk.Button(root, text="Start Recording", command=start_Recording, state=tk.ACTIVE)
start_button.pack(pady=5)

def stop_recording():
    global mtw_instance
    mtw_instance.mtwStopExecution()
    if data is not None:

        data0 = data[0][0]
        data1 = data[0][1]
        index0 = data[1][0]
        index1 = data[1][1]

        print("total size of buffers: 0: {:d} 1: {:d}".format(data0.size * data0.itemsize, data1.size * data1.itemsize))

        pitch0 = data0[:index0]
        pitch1 = data1[:index1]

        print(pitch0.shape)
        print(pitch1.shape)

        #compute sample rate (samples/s)
        Fs0 = len(pitch0)/duration
        Fs1 = len(pitch1)/duration

        #subtract DC component
        balanced_data0 = pitch0 - np.mean(pitch0)
        balanced_data1 = pitch1 - np.mean(pitch1)

        #compute FFT 
        fftPitch0 = np.fft.fft(balanced_data0)
        fftPitch1 = np.fft.fft(balanced_data1)

        #get modulo of FFT coefficients
        fftPitch0Mod = np.abs(fftPitch0)
        fftPitch1Mod = np.abs(fftPitch1)

        fig, axs = plt.subplots(2)

        axs[0].plot(pitch0, label = 'pitch0')
        axs[0].plot(pitch1, label = 'pitch1')
        axs[0].set_title("Pitch angle")
        axs[0].grid(True)

        axs[1].plot(fftPitch0Mod[0:len(fftPitch0Mod)//2], label = 'fftPitch0')
        axs[1].plot(fftPitch1Mod[0:len(fftPitch0Mod)//2], label = 'fftPitch1')
        axs[1].set_title("FFT")
        plt.show()
    return
    
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED)
stop_button.pack(pady=5)


root.mainloop()



