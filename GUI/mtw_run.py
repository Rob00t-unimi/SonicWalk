import threading
import numpy as np

class MtwThread(threading.Thread):
    """
    A thread class for performing the analysis and recording of the MTW devices.
    """
    def __init__(self, Duration=90, MusicSamplesPath="../sonicwalk/audio_samples/cammino_1_fase_2", Exercise=0, Analyze=True, setStart=None, CalculateBpm=False, shared_data=None, sound=True):
        """    
        REQUIRES:
            - Duration (int): Duration of the recording in seconds. Defaults to 90.
            - MusicSamplesPath (str): Path to the music samples directory. Defaults to "../sonicwalk/audio_samples/cammino_1_fase_2".
            - Exercise (int): Type of exercise: 0 for walking, 1 for walking in place (High Knees, Butt Kicks), 2 for walking in place (High Knees with sensors on the thighs), 3 for the swing, 4 for the double step. Defaults to 0 (walking).
            - Analyze (bool): Indicates whether real-time analysis of the exercise will be performed. Defaults to True.
            - setStart (callable): Function to emit a signal when the recording starts. Defaults to None.
            - CalculateBpm (bool): Indicates whether to calculate BPM during analysis. Defaults to False.
            - shared_data (SharedData): Pre-initialized object from sharedVariables module. Defaults to None.

        MODIFIES: 
            - self

        EFFECTS: 
            - initialization of the thread
        """
        super().__init__()
        self.Duration = Duration
        self.MusicSamplesPath = MusicSamplesPath
        self.Exercise = Exercise
        self.Analyze = Analyze
        self.setStart = setStart
        self.CalculateBpm = CalculateBpm
        self.shared_data = shared_data
        self.result = None
        self._stop_event = threading.Event()  # Event to indicates the end of the thread
        self.mtw = None
        self.stop_plotter = None
        self.sound = sound

    def run(self):
        """    
        MODIFIES: 
            - self.result

        EFFECTS: 
            - start the thread and run the analysis and the recording with mtw sensors by calling mtwRecord on MtwAwinda object
        """
        from sonicwalk import mtw
        try:
            with mtw.MtwAwinda(120, 19, self.MusicSamplesPath) as mtw:
                self.mtw = mtw
                data = mtw.mtwRecord(duration=self.Duration, plot=False, analyze=self.Analyze, exType=self.Exercise, calculateBpm=self.CalculateBpm, shared_data=self.shared_data, setStart=self.setStart, sound = self.sound)
                
            if data is not None:
                data0 = data[0][0]
                data1 = data[0][1]
                index0 = data[1][0]
                index1 = data[1][1]
                bpmValue = data[3]
                
                print(f"bpm value {bpmValue}")

                pitch0 = data0[:index0]
                pitch1 = data1[:index1]

                max_length = max(len(pitch0), len(pitch1))
                new_pitch0 = np.pad(pitch0, (0, max_length - len(pitch0)), mode='constant')
                new_pitch1 = np.pad(pitch1, (0, max_length - len(pitch1)), mode='constant')

                combined_data = np.vstack((new_pitch0, new_pitch1))

                Fs = max_length / self.Duration

                self.result = combined_data, Fs, bpmValue

            else: 
                if self.stop_plotter is not None: self.stop_plotter()   # stop and clean the plotter
                return

        except RuntimeError as e:
            self.result = e
        except Exception as e:
            self.result = e
        except:
            print("Something went wrong...")

    def get_results(self):
        """
        EFFECTS: 
            - returns a tuple containing the signals data, sampling frequency (Fs), and BPM value.
        """
        return self.result

    def interrupt_recording(self, stop_plotter = None):
        """
        REQUIRES: 
            - stop_plotter (callable): An optional callback function called when interrupting the recording.

        EFFECTS:  
            - Interrupts the recording and analysis of the MTW devices and terminates the thread run.
        """
        self.stop_plotter = stop_plotter    # stop and clean the plotter
        self.mtw.stopRecording()    # stop mtw recording


