import threading
import sys
import time
sys.path.append("../sonicwalk")
import numpy as np


class MtwThread(threading.Thread):
    def __init__(self, Duration=90, MusicSamplesPath="../sonicwalk/audio_samples/cammino_1_fase_2", Exercise=0, Analyze=True, setStart=None, CalculateBpm=False, shared_data=None):
        super().__init__()
        self.Duration = Duration
        self.MusicSamplesPath = MusicSamplesPath
        self.Exercise = Exercise
        self.Analyze = Analyze
        self.setStart = setStart
        self.CalculateBpm = CalculateBpm
        self.shared_data = shared_data
        self.result = None
        self._stop_event = threading.Event()  # Evento per segnalare al thread di terminare
        self.mtw = None
        self.stop_plotter = None

    def run(self):
        import mtw
        try:
            with mtw.MtwAwinda(120, 19, self.MusicSamplesPath) as mtw:
                self.mtw = mtw
                data = mtw.mtwRecord(duration=self.Duration, plot=False, analyze=self.Analyze, exType=self.Exercise, calculateBpm=self.CalculateBpm, shared_data=self.shared_data, setStart=self.setStart)
                
            if data is not None:
                data0 = data[0][0]
                data1 = data[0][1]
                index0 = data[1][0]
                index1 = data[1][1]
                bpmValue = data[3]

                pitch0 = data0[:index0]
                pitch1 = data1[:index1]

                max_length = max(len(pitch0), len(pitch1))
                new_pitch0 = np.pad(pitch0, (0, max_length - len(pitch0)), mode='constant')
                new_pitch1 = np.pad(pitch1, (0, max_length - len(pitch1)), mode='constant')

                combined_data = np.vstack((new_pitch0, new_pitch1))

                Fs = max_length / self.Duration

                self.result = combined_data, Fs, bpmValue

            else: 
                if self.stop_plotter is not None: self.stop_plotter()
                return

        except RuntimeError as e:
            self.result = e
        except Exception as e:
            self.result = e

    def get_results(self):
        return self.result

    def interrupt_recording(self, stop_plotter = None):
        self.stop_plotter = stop_plotter
        self.mtw.stopRecording()    # stop mtw recording


