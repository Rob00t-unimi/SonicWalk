import sys
sys.path.append("../sonicwalk")

import mtw
import numpy as np
import matplotlib.pyplot as plt

duration = 60
samplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2"

with mtw.MtwAwinda(120, 19, samplesPath) as mtw:
    data = mtw.mtwRecord(duration, plot=True, analyze=True, exType = 0)
        # 0 --> walking
        # 1 --> Walking in place (High Knees, Butt Kicks)
        # 2 --> Walking in place (High Knees con sensori sulle cosce)
        # 3 --> Swing
        # 4 --> Unknown
        # 5 --> ROB's walking 
    
data0 = data[0][0]
data1 = data[0][1]
index0 = data[1][0]
index1 = data[1][1]

print("total size of buffers: 0: {:d} 1: {:d}".format(data0.size * data0.itemsize, data1.size * data1.itemsize))

pitch0 = data0[:index0]
pitch1 = data1[:index1]

# Saving signal
# Find the maximum length
max_length = max(len(pitch0), len(pitch1))

# Add zero-padding
new_pitch0 = np.pad(pitch0, (0, max_length - len(pitch0)), mode='constant')
new_pitch1 = np.pad(pitch1, (0, max_length - len(pitch1)), mode='constant')

# Combine both arrays
combined_data = np.vstack((new_pitch0, new_pitch1))

# Ask user for filename with path
filename = input("Enter filename with path to save (without extension): ")

# Save the combined data
np.save("/home/phuselab/Desktop/RobertoTallarini/SonicWalk/savedSignals/" + f'{filename}.npy', combined_data)

print(f"{filename}.npy saved successfully.")

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

# Calcola le FFT per entrambi i segnali (pitch0 e pitch1)
fft_pitch0 = np.fft.fft(pitch0)
fft_pitch1 = np.fft.fft(pitch1)

fig, axs = plt.subplots(2)

axs[0].plot(pitch0, label = 'pitch0')
axs[0].plot(pitch1, label = 'pitch1')
axs[0].set_title("Pitch angle")

axs[1].plot(fftPitch0Mod[0:len(fftPitch0Mod)//2], label = 'fftPitch0')
axs[1].plot(fftPitch1Mod[0:len(fftPitch0Mod)//2], label = 'fftPitch1')
axs[1].set_title("FFT")
plt.show()

#zero crossings count
steps0 = (pitch0[:-1] * pitch0[1:] < 0).sum()/2
steps1 = (pitch1[:-1] * pitch1[1:] < 0).sum()/2

print("Total number of steps (offline count): {:f}".format(steps0 + steps1))