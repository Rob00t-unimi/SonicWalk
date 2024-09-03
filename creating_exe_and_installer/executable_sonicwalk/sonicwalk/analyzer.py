# MIT License

# Copyright (c) 2024 Roberto Tallarini & Gabriele Esposito

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import pygame
import time
import numpy as np
from scipy.ndimage import gaussian_filter1d
import json

class ZeroCrossingDetectionResult:
    def __init__(self, found_crossing=False, gradient=None):
        self.founded = found_crossing
        self.gradient = gradient
        self.absGradient = None if gradient is None else abs(gradient)

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
        self.__completeMovements = 0    # ex. steps
        self.__legDetected = False
        self.__foundedPeak = False
        self.__pos = True
        self.__findMininmum = False
        self.__firstpeak = False

        self.__gradientThreshold = 0.3

        self.__previousWindow = None
        self.__window = None

        self.__interestingPoints = []
        self.__currentGlobalIndex = -1
        self.__indexCycle = 0
        self.__prevIndex = -1

        self.__betweenStepTimes = []

    ################################ START & END =================================================================
        

    def __terminate(self):
        # - 2000 termination value
        self.__interestingPoints.append(-2000)
        for i in range(len(self.__interestingPoints)):
            self.__sharedInterestingPoints[i] = self.__interestingPoints[i]

        self.__betweenStepTimes.append(-2000)
        for i in range(len(self.__betweenStepTimes)):
            self.__sharedBetweenStepsTimes[i] = self.__betweenStepTimes[i]

        print("analyzer daemon {:d} terminated...".format(self.__num))
        print("analyzer {:d} number of completed movements: {:d}".format(self.__num, self.__completeMovements))
        #write total number of complete movements to shared memory
        #data is written at index - 1 (termination flag at index should not be overwritten for the correct behaviour)
        self.__data[self.__index.value - 1] = self.__completeMovements

    def __endController(self):
        if self.__data[self.__index.value] == 1000:
            self.__active = False
            self.__terminate()
            return True
        return False
    
    def __nextWindow(self):
        #Take last winsize samples from shared memory buffer
        if self.__index.value > self.__winsize:
            self.__pitch = np.array(self.__data[self.__index.value-self.__winsize:self.__index.value])
        else:
            self.__pitch = np.concatenate((np.array(self.__data[-(self.__winsize - self.__index.value):]), np.array(self.__data[:self.__index.value])))

        self.__currentGlobalIndex = self.__index.value + self.__indexCycle*1000 # current global index is indicative 
        if self.__index.value < self.__prevIndex:
            self.__indexCycle += 1
        self.__prevIndex = self.__index.value
        return 
    
    def runAnalysis(self, method = None):
        if method is not None:
            while self.__active:
                if self.__endController() : return
                self.__nextWindow()
                #allow other processes to run (wait 3ms)
                #one packet is produced roughly every 8.33ms
                method()
                time.sleep(0.003)
    
    ################################ UTILS ======================================================== && Rob ========

    def extractParameters(self):
        """
        Extracts sensitivity parameters for the exercises from a JSON file.

        Effects:
            returns a dictionary containing the parameters
        """
        def remove_comments(json_string):
            # Remove // comments
            json_string = re.sub(r'\/\/.*', '', json_string)
            # Remove /* ... */ comments
            json_string = re.sub(r'\/\*.*?\*\/', '', json_string, flags=re.DOTALL)
            return json_string
        try:
            with open('sonicwalk/sensitivity_levels.json', 'r') as file:
                json_string = file.read()

            json_string = remove_comments(json_string)
            data = json.loads(json_string)
            return data
        except FileNotFoundError:
            print("Error: The file 'sensitivity_levels.json' was not found.")
                
    def _playSample(self):
        """
            It play a sample and increment the step counter
        """
        sample = self.__samples[self.__sharedIndex.value()]
        pygame.mixer.Sound(sample).play()
        
        self.__sharedIndex.increment()
        self.__completeMovements += 1
        return
    
    def peakFinder(self, window, previous_window, current_window, minimum = False, positive = None):
        """
        Determine if there is a positive or negative peak in the window.
        
        Requires:
            window (list): The window to analyze for the presence of a peak.
            previous_window (list): The previous window.
            current_window (list): The current window.
            minimum (bool, optional): Indicates whether the research is for peak or minimum.
                                       Defaults to False (peak).
            positive (bool, optional): Indicates whether the research is for positive or negative peak or minimum.
                            Defaults to None.
        Effects:
            Returns: bool True if a positive or negative peak is detected in the window; otherwise, False.
            Using this function allows the determination of a positive or negative peak with a single window delay.
        """

        # This approach allows for identifying the presence of a peak within a time window of the subsequent one.
        # Peak detection involves comparing the maximums or minimums of the windows, thus helping to reduce noise.
        # Indeed, directly comparing 3 samples instead of windows could lead to incorrect identifications 
        # due to erroneous value oscillations caused by noise.

            # Due to window overlap, we might not detect peaks correctly, as a maximum in one window could reappear in the next.
            # For this reason, we SLIGHTLY modify the window values by smoothing them with a Gaussian filter.
            # This allows us to further reduce noise and improve peak detection.

            # Note:
            # Using an aggressive Gaussian filter applied to windows could create additional peaks where none exist.

            # window = gaussian_filter1d(window, sigma=0.6)
            # previous_window = gaussian_filter1d(previous_window, sigma=0.6)
            # current_window = gaussian_filter1d(current_window, sigma=0.6)

                
        if not minimum:
            if np.max(window) > np.max(previous_window) and np.max(window) > np.max(current_window):
                # peak into window
                if (positive is None) or (np.max(window) >= 0 and positive) or (np.max(window) < 0 and not positive):
                    return True
        else:
            if np.min(window) < np.min(previous_window) and np.min(window) < np.min(current_window):
                # minimum into window
                if (positive is None) or (np.min(window) >= 0 and positive) or (np.min(window) < 0 and not positive):
                    return True
        return False
    
    def phaseAnalyzer(self, current_window, previous_window, increasing_phase = True):
        """
        Analyze the phase of the system based on current and previous windows.

        Requires:
            current_window (list): The current window of data.
            previous_window (list): The previous window of data.
            increasing_phase (bool, optional): Indicates whether the method has to verify in an increasing or decreasing phase.
                                                Defaults to True (increasing phase).

        Effects:
            Returns: bool True if the system detects the specified phase.
            This function determines whether the system is in an increasing or decreasing phase 
            by comparing the maximum and minimum values of the current window with those of the previous window.
        """

        # This approach allows identifying the rising or falling phase between two windows.
        # Identification involves comparing the maximums or minimums of the windows, thus helping to reduce noise.

        if increasing_phase:
            if np.max(current_window) > np.max(previous_window):
                # Rising phase
                return True
            else:
                return False
        else:
            if np.min(current_window) <= np.min(previous_window):
                # Falling phase
                return True
            else:
                return False
    
    def zeroCrossingDetector(self, window, positive = True, maxAbsGradient = None):
        """
        Detect zero crossings in the window.

        Requires:
            window (list): The window to analyze for zero crossings.
            positive (bool, optional): Indicates whether the zero crossing to detect is for positive or negative zero crossings.
                                    Defaults to True (positive zero crossing).
            maxAbsGradient (float, optional): The maximum absolute value of the gradient. Defaults to None (no maximum).

        Effects:
            This function detects zero crossings in the given window, considering the specified polarity and gradient maximum threshold.
            Returns: None if no zero crossing is detected
            Returns: ZeroCrossingDetectionResult object if a zero crossing is detected.
        """
        # zero crossings count
        cross =  np.diff(np.signbit(window))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            # determine position of zero crossing
            crossPosition = np.where(cross)[0][0]

            # determine the gradient of the zero crossing
            gradient = np.gradient(window)[crossPosition + 1]
            absGradient = abs(gradient)
            if maxAbsGradient is None or absGradient < maxAbsGradient:
                # determine polarity of zero-crossing (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
                negativeZc = np.signbit(gradient)

                founded = not negativeZc if positive else negativeZc

                return ZeroCrossingDetectionResult(found_crossing=founded, gradient=gradient)    
        else:
            return None
        
    def _setNewGradientThreshold(self, newGradient, alpha = 0.5, min_value = 0.4):

        """
            Requires:
                newGradient is a float value of current gradient
                alpha is a float value between 0 and 1 indicating the weight of the new gradient compared to the old gradient threshold.
            Effects:
                Updates the gradient threshold based on the new gradient and the old threshold.
                The new threshold is the average of the new gradient and the old one. 
                EMA (Exponential Moving Average)
        """

        # Alpha ranges between 0 and 1.
        # A smaller alpha gives more weight to the old average.
        # A larger alpha gives more weight to the new average.

        # EMA (Exponential Moving Average)
        newMean = (alpha * newGradient) + ((1-alpha)*self.__gradientThreshold)
        self.__gradientThreshold =  newMean if newMean > min_value else min_value


    ################################ STEP DETECTION =======================================================================
        
    def __detectStep(self):

        displacement = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["displacement"]
        validRange = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["validRange"]
        min_threshold = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["min_threshold"]
        time_threshold =self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["time_threshold"] # seconds
      
        #TEST: subtract a certain angle to trigger sound earlier in the cycle
        self.__pitch = self.__pitch - displacement

        # update peak (only in swing phase : after a positive zero-crossing is encountered 
        # - until the next zero-crossing with negative gradient)
        if self.__swingPhase == True:
            self.__peak = np.max([self.__peak, np.max(self.__pitch)])

        # Zero crossing detection
        negativeZc = self.zeroCrossingDetector(positive=False, window = self.__pitch)

        if negativeZc is not None and negativeZc.founded:
            if self.__swingPhase == True:
                elapsed_time = time.time() - self.__timestamp
                if self.__peak >= self.__threshold - validRange and elapsed_time > time_threshold:
                    # a step is valid only if last peak is greater than adaptive threshold 
                    # minus a constant angle to allow angles less than the minimum to be re gistered

                    self.__swingPhase = False #swing phase is set to false only when step is valid
                    self.__timestamp = time.time() # reset timestamp (new step)

                    # update peak history with last peak
                    self.__peakHistory[self.__completeMovements % self.__history_sz] = self.__peak

                    # play sound and increment the movement counter
                    if self.__sound: self._playSample()
                    # set time for bpm estimator
                    if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)

                    # save point
                    self.__interestingPoints.append(self.__currentGlobalIndex)

                    # update threshold
                    newthresh = np.min(self.__peakHistory)
                    self.__threshold = newthresh if newthresh > min_threshold else min_threshold # ensure that threshold cannot go below 2.0

                self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
        elif negativeZc is not None and not negativeZc.founded: #positiveZc
            self.__swingPhase = True

    ################################ MARCH DETECTION ======================================================== && Rob ========
        
    ### Supports:
        # - High knees march with ankle sensors
        # - High knees march with thigh sensors
        # - Back kicks with ankle sensors

        
    ### ALGORITHM

    #### Approach 1 (FAIL)
    # - Initially, I tried inverting the signal and looking for peaks with an adaptive threshold. When validating a peak, I searched for the first sample within a range near zero to trigger a sound. Once found, I resumed searching for valid peaks.

    # #### Final Approach
    # - All three signals have very high peaks (either exclusively positive or negative) and are far from noise, so I do not need a dynamic threshold.
    # - I shift the signal downwards to mostly negate all noise (this shift acts as a threshold and anticipates zero crossings):
    #   - A shift of 20 ensures there is no noise.
    #   - A shift of 10 almost guarantees no noise.
    #   - A shift of 5 is less certain and less anticipatory, but detects walking with very small steps.

    # - After shifting, I look for opposite zero crossings:
    #   - Finding a negative zero crossing indicates a peak above the displacement (threshold), making the peak valid and triggering a sound.
    #   - I then search for a positive zero crossing and return to searching for a negative zero crossing.

    # - The signal has negative peaks so i invert it.
                

    def __detectMarch(self):

        # Window manipulation
        if (self.__exType == 1):
            self.__pitch = - self.__pitch
        self.__pitch = self.__pitch - self.__threshold

        # Zero crossing detection
        negativeZc = self.zeroCrossingDetector(positive=False, window = self.__pitch)
        if negativeZc is not None and negativeZc.founded:
            if self.__swingPhase == True:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold:

                    # in this case the displacement is sufficient to be also the threshold
                    # so, a step is valid when we found a zero crossing after a peak value > 0

                    # set swing phase to false until we find a positive zero crossing
                    self.__swingPhase = False
                    self.__timestamp = time.time() # reset timestamp (new step)
                    # play sound and increment the movement counter
                    if self.__sound: self._playSample()
                    # set time for bpm estimator
                    if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)
                    self.__interestingPoints.append(self.__currentGlobalIndex)

                self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
        elif negativeZc is not None and not negativeZc.founded: 
            # we found positive Zc so we can set swing phase on true
            self.__swingPhase = True


    ################################ LEG DETECTION ======================================================== && Rob ========
            

    # AUTO leg DETECTION
            
    def detectLeg(self, displacement = None):
        
        # IDEA:
        # When starting an exercise, typically one begins with the leg stepping forward. Ideally, this leg will cross a positive zero crossing first.
        # However, due to knee bending, a negative zero crossing typically occurs first in practice.

        # ALGORITHM:
        # The algorithm utilizes the concept of shared variables between processes, protected by locks.
        # Processes are synchronized using a shared variable at startup.
        # The first process to cross the zero crossing communicates this to the other process via another shared variable, allowing processes to distinguish themselves.

        # Due to noise, unexpected zero crossings may occur. The algorithm addresses this as follows:
        # 1. Gaussian Filtering: Filters the window with a Gaussian filter to reduce noise and flatten the signal (critical at the start when both signals are close to zero).
        # 2. Signal Shifting: Shifts both signals downward to delay the detection of the positive zero crossing.
        #    Due to inherent subjective differences in the analyzed signals, the signal that should not detect the zero crossing has a broader bell curve.
        #    Therefore, with the same displacement, it is delayed even more, which works to our advantage (initially, processes did not start in sync).
        # 3. Validating Positive Zero Crossing: When a positive zero crossing is found, it is considered valid only if the signal has recorded a negative peak at least 0.1 degrees lower than the displacement.
        #    This accounts for the natural knee bending in "natural" movements. For the other foot, noise that is flattened (except for movements) will be lower than 0.1 degrees of displacement and will reach the positive zero crossing first.
        #    For the other foot (except for movements), it is unlikely that the noise, which is flattened, will be lower than 0.1 degrees relative to the displacement and that it will subsequently reach the positive zero crossing first.
                                        
        if displacement is not None:
                  
            pitch =  self.__pitch - displacement    # Increasing the subtracted value increases detection precision but requires larger step amplitude
        else:                                       #  Decreasing it compromises accurate detection.
            pitch = self.__pitch

        if pitch is not None: pitch = gaussian_filter1d(pitch, sigma=1)

        positiveZc = self.zeroCrossingDetector(window = pitch, positive=True)
        if positiveZc is not None and positiveZc.founded:
            if self.__peak < - displacement - 0.1:
                self.__peak = 0.0
                setted = self.__sharedLegDetected.set(True)
                if setted: self.__legDetected = True
            else:
                self.__peak = np.minimum(np.min(pitch), self.__peak)
        return   


    ################################ DOUBLE STEP DETECTION ======================================================== && Rob ========


    def __detectSwing(self):

        # The two legs have different signals that therefore need to be distinguished and analyzed differently.

        displacement = self.__parameters["swing"]["leg_detection"][f"sensitivity_{self.__sensitivity}"]["displacement"]

        if self.__auto_detectLegs:
            print("AUTO DETECTION...")
            # AUTO DETECTION
            if self.__sharedLegDetected.get() == False:
                self.detectLeg(displacement=displacement)

            if self.__sharedLegDetected.get() == True : 
                if self.__legDetected == False:
                    self.otherLeg()
                else:
                    self.stepLeg()
        else:
            if self.__selectedLeg is not None:
                if self.__selectedLeg:
                    self.stepLeg()
                else:
                    self.otherLeg()
        return 
        
    def _updateWindows(self):
        self.__previousWindow = self.__window
        self.__window = self.__pitch
        
    def stepLeg(self):
            
        # OLD:
        # The moving leg generates a double positive peak followed by a double negative trough, and so on.
        # We are only interested when the foot touches the ground, so for each pair, only the first of the two peaks (or troughs) matters.
        # When I detect a positive peak, I trigger a sound, then look for the second peak. Once found, I switch the search to a negative trough, and vice versa.

        # NEW:
        # I detect the positive peak, check if it's valid with a dynamic threshold. If within 0.3 seconds there's no positive trough, I trigger a sound.
        # If I find a positive trough before 0.3 seconds, I trigger a sound.
        # I look for a new positive peak, once found,
        # I search for a negative trough, check if it's valid with a dynamic threshold. If within 0.4 seconds there's no negative peak, I trigger a sound.
        # If I find a negative peak before 0.4 seconds, I trigger a sound.
        # I look for a new negative trough, once found, repeat the same procedure.

        def control_if_newWindow():
            # If the new window is not completely new then add the new part into self.__window and do nothing.
            for i, item in enumerate(self.__window):
                for i2, item2 in enumerate(self.__pitch):
                    if item == item2:
                        if np.array_equal(self.__window[i:], self.__pitch[:len(self.__window)-i]): 
                            self.__pitch = self.__pitch[len(self.__window)-i:]
                            return
        
        # If the first 2 windows haven't arrived yet    
        if self.__previousWindow is None and self.__window is None: 
            self._updateWindows() 
            return
        elif self.__previousWindow is None:
            self.__previousWindow = self.__window
            control_if_newWindow()
            if self.__pitch.size == 0: return
            self.__window = self.__pitch
            return
        
        # control if new window contains new informations else return
        control_if_newWindow()
        if self.__pitch.size == 0: return

        # initialize the windows
        pitch = self.__pitch
        previous = self.__previousWindow
        window = self.__window

        max_time_wait = 0.4 if not self.__pos else 0.3  # max wait time before play sound
        displacement = 5 # Only when searching for negative peaks and positive troughs
        time_threshold = self.__parameters["swing"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["time_threshold"]   # time threshold between peaks
        min_peak_threshold = self.__parameters["swing"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["min_peak_threshold"]    # Absolute value for positive peaks and negative troughs
        validRange = self.__parameters["swing"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["validRange"]

        if time.time() - self.__timestamp >= max_time_wait and self.__firstpeak and not self.__foundedPeak:
            # sound here after a delay
            self.__interestingPoints.append(self.__currentGlobalIndex)
            # play sound and increment the movement counter
            if self.__sound: self._playSample()
            # print("AFTER DELAY")
            # set time for bpm estimator
            if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)
            self.__foundedPeak = True
            self.__findMininmum = not self.__findMininmum
            self._updateWindows() 
            self.__timestamp = time.time()
            return

        # Remove values above or below zero
        if self.__findMininmum == self.__pos and self.__pos == True:              
            pitch = pitch + displacement               # Shift upwards when looking for positive troughs, to ensure capturing all of them
            previous = previous + displacement         # Conversely, there's no need to shift because moving backwards never reaches zero (risking balance loss)
            window = window + displacement
        pitch[pitch <= 0 if self.__pos else pitch >= 0] = 0
        previous[previous <= 0 if self.__pos else previous >= 0] = 0
        window[window <= 0 if self.__pos else window >= 0] = 0

        findedPeak = self.peakFinder(previous_window=previous, window=window, current_window=pitch, minimum = self.__findMininmum, positive=self.__pos) # if findMininmum is true search mininmum else search peaks, positive indicates if search is on positive or negative part of the plan

        # If a peak or a minimum has been found, check if it is valid
        if findedPeak:
            peak = abs(np.max(window)) if not self.__findMininmum else (abs(np.min(window)))
            # self.__interestingPoints.append(self.__currentGlobalIndex)
            elapsed_time = time.time() - self.__timestamp
            thresh = 0 if self.__findMininmum == self.__pos else self.__threshold - validRange
            if elapsed_time > time_threshold and peak > thresh:
                self.__timestamp = time.time()
                if self.__findMininmum != self.__pos: 
                    # update threshold 
                    self.__peakHistory[self.__completeMovements % self.__history_sz] = peak
                    newthresh = np.min(self.__peakHistory)
                    self.__threshold = newthresh if newthresh > min_peak_threshold else min_peak_threshold
                    
                # findMininmum starts false
                # firstpeak starts false
                # pos starts true
                # foundedPeak starts false

                if not self.__firstpeak :   # if there is no first peak - this is the first
                    print("max pos") if self.__findMininmum == False else print("min neg")
                    self.__findMininmum = not self.__findMininmum    # set search minimum
                    self.__firstpeak = True  # set first peak finded
                    # self.__interestingPoints.append(self.__currentGlobalIndex)

                elif not self.__foundedPeak:   # if there is no interesting peak - this it the interesting peak
                    print("max neg") if self.__findMininmum == False else print("min pos")
                    self.__foundedPeak = True  # set the interesting peak finded
                    self.__findMininmum = not self.__findMininmum   # set search peak  

                    # sound here could be too late, if it arrives after 0.4 seconds the sound is already reproduced and this part skipped
                    self.__interestingPoints.append(self.__currentGlobalIndex)
                    # play sound and increment the movement counter
                    if self.__sound: self._playSample()
                    # print("BEFORE DELAY")
                    # set time for bpm estimator
                    if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)

                else:   # if there is the first peak and the interesting peak - this is the last peak
                    print("max pos 2") if self.__findMininmum == False else print("min neg 2")
                    self.__pos = not self.__pos # switch search
                    self.__findMininmum = not self.__findMininmum   # set search minimum
                    self.__foundedPeak = False  # reset interesting peak
                    self.__firstpeak = False    # reset first peak
                    # self.__interestingPoints.append(self.__currentGlobalIndex)
                    
        # update windows
        self._updateWindows() 
            

    def otherLeg(self):

        ## This leg has a sinusoidal-like pattern, so I'm interested in zero crossings.
        # In this case, however, I'm interested in both zero crossings that occur before and after the peak.
        # Therefore, I look for a positive zero crossing, trigger a sound,
        # look for a negative zero crossing, trigger a sound,
        # and so on...

        # To avoid detecting too sudden zero crossings caused by unexpected rapid changes or
        # especially by knee bending, I use an adaptive threshold on the gradient (slope) of the zero crossings.
        # When the slope exceeds the threshold, the zero crossing is not valid.

        displacement1 = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["displacement"]
        displacement0 = - displacement1
        valid_gradient_range = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["valid_gradient_range"] # per permettere alla soglia anche di salire
        time_threshold = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["time_threshold"] # seconds   # con una threshold temporale alta evitiamo di registrare Zc dovuti al piegamento del ginocchio
        min_gradient_threshold = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
        alpha = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["alpha"]

        pitch = (self.__pitch + displacement0) if not self.__pos else (self.__pitch + displacement1)
        # pitch = (self.__pitch - 1) if not self.__pos else (self.__pitch + 2)      # da positivo a negativo è più veloce quindi non anticipo, da negativo a positivo è più lento e anticipo

        # Search for positive or negative zero crossing within the threshold
        positiveZc = self.zeroCrossingDetector(window = pitch, positive = True, maxAbsGradient = self.__gradientThreshold+valid_gradient_range)     # + 0.3 per permettere alla soglia anche di salire
        if positiveZc is not None and ((positiveZc.founded and self.__pos) or (not positiveZc.founded and not self.__pos)):
            elapsed_time = time.time() - self.__timestamp
            if elapsed_time > time_threshold:    # If self.__pos is True, I have already found a peak, so the zero crossing is valid
                self.__interestingPoints.append(self.__currentGlobalIndex)
                self.__pos = not self.__pos     # switch research of zero crossing type
                self.__timestamp = time.time()  # update time stamp
                # play sound and increment the movement counter
                if self.__sound: self._playSample()
                # set time for bpm estimator
                if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)
                # play sound and increment step count

                # threshold update
                self._setNewGradientThreshold(newGradient=positiveZc.absGradient, alpha=alpha, min_value=min_gradient_threshold)
                print("gradient: " + str(self.__gradientThreshold))


    ################################ SWING DETECTION ======================================================== && Rob ========


    def __detectTandem(self):
    
        # The two legs perform different but similar actions.
        # One leg mostly produces negative angles, and we are interested in detecting when it approaches zero (or positive zero crossings).
        # The other leg mostly produces positive angles, and we are interested in detecting when it approaches zero (or negative zero crossings).
        # Whether starting with the leg moving forward or backward, the forward leg is the first to reach a positive zero crossing.
        # Therefore, I use the same method as the swing for recognition.

        displacement = self.__parameters["tandem"]["leg_detection"][f"sensitivity_{self.__sensitivity}"]["displacement"]

        if self.__auto_detectLegs:
            print("AUTO DETECTION...")
            # AUTO DETECTION
            if self.__sharedLegDetected.get() == False:
                self.detectLeg(displacement=displacement) # If the displacement is high, the knee bend should be wider; if it's low, it should be less

            if self.__sharedLegDetected.get() == True : 
                if self.__legDetected == False:
                    self.tandemFunction(forward=False)
                else:
                    self.tandemFunction(forward=True)
        else:
            if self.__selectedLeg is not None:
                # self.__selectedLeg = True if the front leg is the right one, False if it's the left one
                self.tandemFunction(forward=self.__selectedLeg)
    

    # Negative angles might proportionally be lower than positive ones, so different shifts should be adopted.
    # The difference in shifts is determined by the angles typically made by the feet, which usually vary.
    # The back foot points outward, while the front foot points forward.
                
    # The problem of knee bending remains can be addressed with the gradient threshold.

    def tandemFunction(self, forward = True):

        # Backward leg:
        # Peaks are almost always above -10 (15) and troughs almost always below -10 (15).
        # Forward leg:
        # Peaks are almost always above 10 and troughs almost always below 10.

        # This allows me to shift the signals by 10° and -10° respectively.

        # standard values
        displacement0 = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["displacement0"]  # -10 for the front leg since it makes positive angles that descend to 0
        displacement1 = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["displacement1"]  # 15 for the back leg since it makes negative angles that rise close to -5
        valid_gradient_range = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["valid_gradient_range"]  # to allow the threshold to rise as well
        time_threshold = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["time_threshold"]  # seconds   # with a high time threshold, we avoid registering Zc due to knee bending
        min_gradient_threshold = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
        alpha = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["alpha"]

        pitch = (self.__pitch + displacement0) if forward else (self.__pitch + displacement1)

        # Zero crossing search
        positiveZc = self.zeroCrossingDetector(window = pitch, positive = True, maxAbsGradient = self.__gradientThreshold+valid_gradient_range)
        if positiveZc is not None and (positiveZc.founded != forward):
            elapsed_time = time.time() - self.__timestamp
            if elapsed_time > time_threshold:    # If self.__pos is True, I have already found a peak, so the zero crossing is valid         
                self.__timestamp = time.time()  # update time stamp
                # play sound and increment the movement counter
                if self.__sound: self._playSample()
                # set time for bpm estimator
                if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)
                self.__interestingPoints.append(self.__currentGlobalIndex)
                print("gradient: " + str(self.__gradientThreshold))

                # threshold update
                self._setNewGradientThreshold(newGradient=positiveZc.absGradient, alpha=alpha, min_value=min_gradient_threshold)
                # print("gradient: " + str(self.__gradientThreshold))


    ################################ OBJECT CALL ======================================================== && Rob ========

    
    def __call__(self, data, index, num, sharedIndex, samples, exType, sensitivityLev, auto_detectLegs, selectedLeg, sharedLegBool, syncProcesses, interestingPoints, betweenStepsTimes, calculateBpm, sound):
        
        self.syncProcesses = syncProcesses

        self.syncProcesses()
        print('starting analyzer daemon.. {:d}'.format(num))
        print(("start time: ") + str(time.time()))

        self.__num = num
        self.__data = data
        self.__index = index
        self.__sharedIndex = sharedIndex
        if self.__sharedIndex is not None: pygame.init()
        self.__samples = samples
        self.__timestamp = time.time()
        self.__active = True
        self.__exType = exType
        self.__selectedLeg = selectedLeg
        self.__sharedLegDetected = sharedLegBool
        self.__sharedInterestingPoints = interestingPoints
        self.__calculateBpm = calculateBpm
        self.__sound = sound
        self.__sharedBetweenStepsTimes = betweenStepsTimes
        self.__auto_detectLegs = auto_detectLegs
        self.__sensitivity = sensitivityLev
        self.__parameters = self.extractParameters()

        # 0 --> walking
        # 1 --> Walking in place and Marching
        # 2 --> Walking in place (with sensors on the thighs)
        # 3 --> Swing
        # 4 --> Load shift in tandem position

        try:

            # WALKING
        
            if exType == 0: 
                self.__threshold = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["min_threshold"]
                print("Step Analyzer")
                print('...analyzer daemon {:d} started'.format(num))
                self.runAnalysis(method=self.__detectStep)

            # MARCHING

            elif exType == 1 or exType == 2: 
                self.__threshold = self.__parameters["march"][f"sensitivity_{self.__sensitivity}"]["threshold"]
                print("Marching Analyzer")
                print('...analyzer daemon {:d} started'.format(num))
                self.runAnalysis(method=self.__detectMarch)

            # LOAD SHIFT in TANDEM

            elif exType == 4:
                self.__gradientThreshold = self.__parameters["tandem"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
                print("Load shift in tandem position Analyzer")
                print('...analyzer daemon {:d} started'.format(num))
                self.runAnalysis(method=self.__detectTandem)

            # SWING

            elif exType == 3: 
                self.__threshold = self.__parameters["swing"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["min_peak_threshold"]
                self.__gradientThreshold = self.__parameters["swing"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
                print("Swing Analyzer")
                print('...analyzer daemon {:d} started'.format(num))
                self.runAnalysis(method=self.__detectSwing)

        except Exception as e:
            print(e)
