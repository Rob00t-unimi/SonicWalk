import simpleaudio
import time
import numpy as np

class Analyzer():
    def __init__(self) -> None:
        self.__winsize = 15 #window duration is 8.33ms * 15 ~ 125 ms
        self.__peak = 0.0
        self.__history_sz = 10 #last three steps
        self.__threshold = 5.0
        self.__peakHistory = np.full(self.__history_sz, 5.0, dtype=np.float64) #start with threshold value low to filter noise
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
        
        #TEST: subtract a certain angle to trigger sound earlier in the cycle
        self.__pitch = self.__pitch - 5

        # update peak (only in swing phase : after a positive zero-crossing is encountered 
        # - until the next zero-crossing with negative gradient)
        if self.__swingPhase == True:
            self.__peak = np.max([self.__peak, np.max(self.__pitch)])
        
        # zero crossings count
        cross =  np.diff(np.signbit(self.__pitch))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            # determine position of zero crossing
            crossPosition = np.where(cross)[0][0]
            # determine polarity of zero-crossing (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
            negativeZc = np.signbit(np.gradient(self.__pitch)[crossPosition + 1])
            if negativeZc:
                if self.__swingPhase == True:
                    elapsed_time = time.time() - self.__timestamp
                    if self.__peak >= self.__threshold - 3.0 and elapsed_time > self.__timeThreshold:
                        # a step is valid only if last peak is greater than adaptive threshold 
                        # minus a constant angle to allow angles less than the minimum to be re gistered
                        self.__swingPhase = False #swing phase is set to false only when step is valid
                        self.__timestamp = time.time() # reset timestamp (new step)
                        _ = self.__samples[self.__sharedIndex.value()].play()
                        self.__sharedIndex.increment()

                        # update peak history with last peak
                        self.__peakHistory[self.__steps % self.__history_sz] = self.__peak

                        # update threshold
                        newthresh = np.min(self.__peakHistory)
                        # ensure that threshold cannot go below 2.0
                        self.__threshold = newthresh if newthresh > 5.0 else 5.0
                        #print("threshold: " + str(self.__threshold))
                        # increment step count
                        self.__steps += 1
                        print(self.__stg)
                    self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
            else: #positiveZc
                self.__swingPhase = True

    def stepDetector(self):
        while self.__active:
            self.__detectStep()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)
        

    def __call__(self, data, index, num, sharedIndex, samples):
        print('starting analyzer daemon.. {:d}'.format(num))

        if num == 0:
            self.__stg = "********************************STEP**********ZERO*********************************************"
        else:
            self.__stg = "********************************STEP***********ONE*********************************************"

        self.__num = num
        self.__data = data
        self.__index = index
        self.__sharedIndex = sharedIndex
        self.__samples = samples
        self.__timestamp = time.time()
        self.__active = True

        print('...analyzer daemon {:d} started'.format(num))
        self.stepDetector()
        
        