import sys
sys.path.append("../sonicwalk")
import numpy as np

def mtw_run(Duration:int=90, MusicSamplesPath = "../sonicwalk/audio_samples/cammino_1_fase_2", Exercise:int=0, Analyze: bool=True, setStart = None, CalculateBpm: bool = False, shared_data: object = None):

    import mtw

    """
        Requires: duration of exercise in seconds (int), default = 90 seconds
                  path of the audio samples (str)
                  exercise number (int)
        
        Returns: bidimensional array of signals samples (2 legs)
                 Sample Frequency of the signals

    """

    duration = Duration   # 1.5 minutes
    samplesPath = MusicSamplesPath
    exercise = Exercise
    analyze = Analyze
    calculateBpm = CalculateBpm
    Shared_data = shared_data

    with mtw.MtwAwinda(120, 19, samplesPath) as mtw:
        setStart()
        data = mtw.mtwRecord(30, plot=False, analyze=analyze, exType = exercise, calculateBpm = calculateBpm, shared_data = Shared_data)
            # 0 --> walking
            # 1 --> Walking in place (High Knees, Butt Kicks)
            # 2 --> Walking in place (High Knees con sensori sulle cosce)
            # 3 --> Swing
            # 4 --> Double Step

    data0 = data[0][0]
    data1 = data[0][1]
    index0 = data[1][0]
    index1 = data[1][1]

    bpmValue = data[3]

    pitch0 = data0[:index0]
    pitch1 = data1[:index1]

    # Find the maximum length
    max_length = max(len(pitch0), len(pitch1))

    # Add zero-padding
    new_pitch0 = np.pad(pitch0, (0, max_length - len(pitch0)), mode='constant')
    new_pitch1 = np.pad(pitch1, (0, max_length - len(pitch1)), mode='constant')

    # Combine both arrays
    combined_data = np.vstack((new_pitch0, new_pitch1))

    #compute sample rate (samples/s)
    Fs = max_length/duration

    return combined_data, Fs, bpmValue

#mtw_run(Duration=90, Exercise=0, Analyze=True)