import simpleaudio as sa
import time
import numpy as np

class Analyzer():
    def __init__(self) -> None:
        self.__wave = sa.WaveObject.from_wave_file("audio_samples/beep.wav")
        self.__winsize = 15 #window duration is 8.33ms * 15 ~ 125 ms
        self.__peak = 0.0
        self.__offset = 0.0 #needs to be less than threshold otherwise signal will not cross zero
        self.__theshold = 3.5 #TODO: make peak theshold ADAPTIVE
        self.__timeThreshold = 0.1 #seconds (100 ms)
        self.__swingPhase = False
        self.__active = False
        self.__steps = 0
        
    def __terminate(self):
        print("analyzer daemon {:d} terminated...".format(self.__num))
        print("analyzer {:d} number of steps: {:d}".format(self.__num, self.__steps))
        #write total number of steps to shared memory
        #data is written at index - 1 (termination flag at index should not be overwritten for the correct behaviour)
        self.__data[self.__index.value - 1] = self.__steps
    
    def __detectStep(self):
        if self.__data[self.__index.value] == 1000:
            self.__active = False
            self.__terminate()
            return
        
        #Take last winsize samples from shared memory buffer
        if self.__index.value > self.__winsize:
            self.__pitch = np.array(self.__data[self.__index.value-self.__winsize:self.__index.value])
        else:
            self.__pitch = np.concatenate((np.array(self.__data[-(self.__winsize - self.__index.value):]), np.array(self.__data[:self.__index.value])))

        #subtract offset to trigger sound earlier in the cycle
        self.__pitch = self.__pitch - self.__offset 

        # zero crossings count
        cross =  np.diff(np.signbit(self.__pitch))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            crossPosition = np.where(cross)[0][0]
            # DETERMINE POLARITY OF ZC AFTER FINDING IT (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
            negativeZc = np.signbit(np.gradient(self.__pitch)[crossPosition + 1])
            if negativeZc:
                if self.__swingPhase == True:
                    elapsed_time = time.time() - self.__timestamp
                    if self.__peak >= self.__theshold and elapsed_time > self.__timeThreshold:
                        self.__swingPhase = False
                        self.__timestamp = time.time()
                        playObject = self.__wave.play()
                        self.__steps += 1
                        self.__peak = 0.0
                        print(self.__stg) 
            else:
                self.__swingPhase = True
                self.__peak = np.max([self.__peak, np.max(self.__pitch)])

    def stepDetector(self):
        while self.__active:
            self.__detectStep()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)
        

    def __call__(self, data, index, num):
        print('starting analyzer daemon.. {:d}'.format(num))

        if num == 0:
            self.__stg = "********************************STEP**********ZERO*********************************************"
        else:
            self.__stg = "********************************STEP***********ONE*********************************************"

        self.__num = num
        self.__data = data
        self.__index = index
        self.__timestamp = time.time()
        self.__active = True

        print('...analyzer daemon {:d} started'.format(num))
        self.stepDetector()
        
        