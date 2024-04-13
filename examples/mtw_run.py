import sys
sys.path.append("../sonicwalk")

import mtw
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp


if __name__ == "__main__":

    
    duration = 20
    samplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2"

    plotPoints = True

    with mtw.MtwAwinda(120, 19, samplesPath) as mtw:
        data = mtw.mtwRecord(duration, plot=True, analyze=True, exType = 0, calculateBpm=False)
            # 0 --> walking
            # 1 --> Walking in place (High Knees, Butt Kicks)3
            # 2 --> Walking in place (High Knees con sensori sulle cosce)
            # 3 --> Swing
            # 4 --> Double step

    data0 = data[0][0]
    data1 = data[0][1]
    index0 = data[1][0]
    index1 = data[1][1]

    interestingPoints0 = data[2][0]
    interestingPoints1 = data[2][1]

    bpmValue = data[3]
    print(str(bpmValue))

    print("total size of buffers: 0: {:d} 1: {:d}".format(data0.size * data0.itemsize, data1.size * data1.itemsize))

    pitch0 = data0[:index0]
    pitch1 = data1[:index1]

    print(pitch0.shape)
    print(pitch1.shape)

    #compute sample rate (samples/s)
    Fs0 = len(pitch0)/duration
    Fs1 = len(pitch1)/duration

    time0 = np.arange(0, len(pitch0)) / Fs0
    time1 = np.arange(0, len(pitch1)) / Fs1

    # #subtract DC component
    # balanced_data0 = pitch0 - np.mean(pitch0)
    # balanced_data1 = pitch1 - np.mean(pitch1)

    # #compute FFT 
    # fftPitch0 = np.fft.fft(balanced_data0)
    # fftPitch1 = np.fft.fft(balanced_data1)

    # #get modulo of FFT coefficients
    # fftPitch0Mod = np.abs(fftPitch0)
    # fftPitch1Mod = np.abs(fftPitch1)

    # fig, axs = plt.subplots(3, figsize=(10, 10))  # Create 3 subplots
    fig, axs = plt.subplots(2, figsize=(10, 10))  # Create 3 subplots


    # Plot for the first signal and its scatter
    axs[0].plot(time0, pitch0, label='pitch0')
    axs[0].set_title("Pitch angle - Signal 1")
    axs[0].grid(True)

    if len(interestingPoints0) > 0 and plotPoints:
        axs[0].scatter(time0[interestingPoints0], pitch0[interestingPoints0], color='red')

    # Plot for the second signal and its scatter
    axs[1].plot(time1, pitch1, label='pitch1', color='green')
    axs[1].set_title("Pitch angle - Signal 2")
    axs[1].grid(True)

    if len(interestingPoints1) > 0 and plotPoints:
        axs[1].scatter(time1[interestingPoints1], pitch1[interestingPoints1], color='blue')

    # # Plot for both FFTs
    # axs[2].plot(fftPitch0Mod[0:len(fftPitch0Mod) // 2], label='fftPitch0')
    # axs[2].plot(fftPitch1Mod[0:len(fftPitch0Mod) // 2], label='fftPitch1')
    # axs[2].set_title("FFT")
    # axs[2].legend()
    # axs[2].grid(True)

    plt.tight_layout()
    plt.show()

    # # Zero crossings count
    # steps0 = (pitch0[:-1] * pitch0[1:] < 0).sum() / 2
    # steps1 = (pitch1[:-1] * pitch1[1:] < 0).sum() / 2

    # print("Total number of steps (offline count): {:f}".format(steps0 + steps1))