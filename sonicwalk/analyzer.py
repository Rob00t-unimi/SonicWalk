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

# import simpleaudio
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
        self.__trasholdRange = 3.0
        self.__legDetected = False
        self.__foundedPeak = False
        self.__pos = True
        self.__findMininmum = False
        self.__firstpeak = False

        self.__gradientThreshold = 0.3
        self.__gradientHistory = np.full(self.__history_sz, 0.6, dtype=np.float64)

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
        # _ = self.__samples[self.__sharedIndex.value()].play()     # with simpleaudio

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

        # Questo approccio consente di identificare la presenza di un picco in una finestra al tempo di quella successiva
        # Per la rilevazione del picco si confrontano i massimi o i minimi delle finestre consentendo cosi di abbattere il rumore
        # Infatti confrontare direttamente 3 campioni anzichè le finestre potrebbe portare ad identificazioni errate 
        # per via di oscillazioni errate nei valori causate dal rumore.

                # per via della sovrapposizione delle finestre potremmo non rilevare i picchi correttamente, poichè
                # un massimo in una finestra potrebbe ripresentarsi in quella successiva
                # per questo motivo modifichiamo LEGGERMENTE i valori delle finestre smussandoli con un filtro gaussiano
                # questo ci consente di abbattere ulteriore rumore e anche di migliorare la rilevazione 

                # N.B
                # con un filtro gaussiano aggressivo invece siccome è applicato alle finestre genereremmo ulteriori picchi dove non ci sono

                # window = gaussian_filter1d(window, sigma=0.6)
                # previous_window = gaussian_filter1d(previous_window, sigma=0.6)
                # current_window = gaussian_filter1d(current_window, sigma=0.6)

                
        if not minimum:
            if np.max(window) > np.max(previous_window) and np.max(window) > np.max(current_window):
                # il picco è in window
                if (positive is None) or (np.max(window) >= 0 and positive) or (np.max(window) < 0 and not positive):
                    return True
        else:
            if np.min(window) < np.min(previous_window) and np.min(window) < np.min(current_window):
                # il minimo è in window
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

        # Questo approccio consente di identificare la fase di salita o discesa tra 2 finestre
        # Per l'identificazione si confrontano i massimi o i minimi delle finestre consentendo cosi di abbattere il rumore

        if increasing_phase:
            if np.max(current_window) > np.max(previous_window):
                # salita
                return True
            else:
                return False
        else:
            if np.min(current_window) <= np.min(previous_window):
                # discesa
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

        # alfa compreso tra 0 e 1 
        # alfa minore da più peso alla media vecchia
        # alfa maggiore da più peso alla media nuova
        
        # self.__gradientHistory[1:] = self.__gradientHistory[:-1]
        # self.__gradientHistory[0] = newGradient

        # EMA (Exponential Moving Average)
        # Nella prima posizione della history ho il valore più recente, nell'ultima il più vecchio
        # mean = np.mean(self.__gradientHistory)
        # newMean = (alpha * mean) + ((1-alpha)*self.__gradientThreshold)
        newMean = (alpha * newGradient) + ((1-alpha)*self.__gradientThreshold)
        self.__gradientThreshold =  newMean if newMean > min_value else min_value


    ################################ STEP DETECTION =======================================================================
        
    def __detectStep(self):

        if self.__endController() : return
        self.__nextWindow()

        displacement = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["displacement"]
        validRange = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["validRange"]
        min_threshold = self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["min_threshold"]
        time_threshold =self.__parameters["walk"][f"sensitivity_{self.__sensitivity}"]["time_threshold"] # seconds

        # print("DISPLACEMENT: " + str(displacement))
        # print("VALIDRANGE: " + str(validRange))
        # print("TIME_THRESHOLD: " + str(time_threshold))
        # print("MIN_THRESHOLD:"+str(min_threshold))
      
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
        
    ### Supporta:
    #           - Marcia sul posto (Ginocchia alte - High knees march) con sensori sulle caviglie
    #           - Marcia sul posto (Ginocchia alte - High knees march) con sensori sulle cosce
    #           - Macia sul posto (piedi indietro - back kicks) sensori sulle caviglie
            
    ### ALGORITMO
            
        # Approccio 1   (FAIL)
            # inizialmente ho pensato di ribaltare il segnale e cercare i picchi con una threshold adattiva, quando validavo un picco cercavo il primo campione in un range vicino a zero per far suonare, quando lo trovavo ripartivo nel cercare un picco valido

        # Approccio Finale
            # Tutti e 3 i segnali hanno solo picchi  molto alti (solo positivi o solo negativi) e lontani dal rumore, quindi non mi serve una threshold dinamica.
            # Traslo in basso in modo da negativizzare quasi tutto il rumore (la traslazione è di fatto una threshold, inoltre permette di anticipare gli zero crossing)
                    # con una traslazione di 20 siamo sicuri che non ci sarà rumore
                    # con una traslazione di 10 siamo quasi sicuri che non ci sarà rumore
                    # con una traslazione di 5 siamo un po' meno sicuri e e meno in anticipo ma rileviamo la marcia con passi molto piccoli
            
            # Dopo la traslazone cerco gli zero crossing opposti:
                # Quando trovo uno zero crossing negativo significa che c'è stato un picco sopra il displacement (threshold) quindi il picco è valido e suono
                # Posso passare alla ricerca di uno zero crossing positivo, quando lo trovo torno alla ricerca di uno zero crossing negativo
        
            # Se il segnale ha picchi positivi va bene, se li ha negativi lo ribalto
                

    def __detectMarch(self):

        # Initialization
        if self.__endController() : return
        self.__nextWindow()

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
            

    # DISTINGUERE AUTOMATICAMENTE LE GAMBE
            
    def detectLeg(self, displacement = None):
        
        # IDEA:
        # Quando si avvia un esercizio, di solito si comincia con la gamba che fa il passo in avanti
        # Idealmente questa gamba attraverserà uno zero crossing positivo per prima
        # Tuttavia, a causa del piegamento del ginocchio, in pratica si verifica prima uno zero crossing negativo.
        
        # ALGORITMO:
        # L'algoritmo sfrutta l'idea di variabili condivise tra processi, protette dai lock.
        # I processi sono sincronizzati tramite una variabile condivisa all'avvio. 
        # Il primo processo che attraversa lo zero crossing lo comunica all'altro tramite un'altra variabile condivisa, i processi sapranno cosi distinguersi
        
        # A causa del rumore, potrebbero verificarsi zero crossing inaspettati. L'algoritmo affronta questa eventualità in questo modo:
            # 1: Filtra la finestra con un filtro gaussiano per ridurre il rumore e appiattire il segnale. (molto importante all'inizio quando i 2 segnali sono entrambi vicini a zero)
            # 2: Trasla verso il basso entrambi i segnali per ritardare il rilevamento dello zero crossing positivo.
            #    per via delle differenze soggettive intrinseche nei segnali analizzati, il segnale di cui non deve essere rilevato lo zero crossing ha una campana più ampia, quindi 
            #    a parità di displacement viene ritardato ancora di più e questo torna a nostro vantaggio (inizialmente i processi non iniziavano in sync)
            # 3: Quando viene trovato lo zero crossing positivo, lo si considera valido solo se il segnale ha registrato un picco negativo inferiore di almeno 0.1 gradi rispetto al displacement
            #    Questo perché per i movimenti "naturali" ci sarà sempre un minimo piegamento del ginocchio. 
            #    Per l'altro piede invece il rumore che viene appiattito difficilmente (eccetto movimenti) sarà più basso di 0.1 gradi del displacement e in concomitanza ranggiungerà prima lo zero crossing positivo
            #    Per l'altro piede (eccetto movimenti), è improbabile che il rumore, che viene appiattito sia inferiore di 0.1 gradi rispetto allo spostamento e che successivamente riuscirà anche a raggiungere per primo
            #    lo zero crossing positivo

                                        
        if displacement is not None:
                  
            pitch =  self.__pitch - displacement    # aumentando il valore sottratto si aumenta la precisione nella rilevazione tuttavia aumenta l'ampiezza del passo richiesto
        else:                                       # diminuendo si perde una corretta rilevazione
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


    def __detectDoubleStep(self):

        # Le due gambe hanno segnali differenti che quindi devono essere distinti e analizzati in modo diverso
        
        if self.__endController() : return
        self.__nextWindow()

        displacement = self.__parameters["double_step"]["leg_detection"][f"sensitivity_{self.__sensitivity}"]["displacement"]

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
        
    # RILEVAZIONE MOVIMENTO GAMBA "CHE SI MOUOVE"
    def stepLeg(self):
            
            #TRASH
            # IDEA:
            # La gamba in movimento genera un doppio picco positivo seguito da un doppio minimo negativo, e così via.
            # Siamo interessati solo quando il piede tocca terra, quindi per ogni coppia conta solo il primo dei due picchi (o minimi).
            # Quando rilevo un picco positivo, suono, poi cerco il secondo picco. Quando l'ho trovato, cambio la ricerca in un minimo negativo, e viceversa.

            # NEW
            # Rilevo il picco positivo, se entro 0.3 secondi non c'è un minimo positivo suono
            # se trovo un minimo positivo prima dei 0.3 secondi suono
            # cerco un nuovo picco positivo, quando lo trovo 
            # cerco un minimo negativo, se entro 0.4 secondi non c'è un massimo negativo suono
            # se trovo un massimo negativo prima dei 0.4 secondi suono
            # cerco un nuovo minimo negativo, quando lo trovo reitero la stessa procedura


            if self.__endController() : return
            self.__nextWindow()

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
            displacement = 5 # solo se cerco massimi negativi e minimi positivi
            time_threshold = self.__parameters["double_step"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["time_threshold"]   # time threshold between peaks
            min_peak_threshold = self.__parameters["double_step"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["min_peak_threshold"]    # abs sui massimi positivi e minimi negativi
            validRange = self.__parameters["double_step"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["validRange"]

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
                pitch = pitch + displacement               # traslo in alto quando cerco minimi positivi, per assicurarmi di prenderli tutti
                previous = previous + displacement         # al contratio non serve traslare perchè andando indietro non arrivo mai a 0 (perderei l'equilibrio)
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
                        # aggiorna la soglia 
                        # print(f"THRESHOLD: {self.__threshold}")
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



#   --------------------------------------------------------------- RIVEDERE DA QUI
            

    # RILEVAZIONE MOVIMENTO GAMBA "FERMA"
    def otherLeg(self):

        ## questa gamba ha un'andamenso tipo sinusoidale quindi mi interessano gli zero crossing
        # in questo caso però mi interessano entrambi gli zero crossing che si verificano uno prima e uno dopo il picco
        # quindi cerco uno zero crossing positivo, faccio suonare
        # cerco uno zero crossing negativo, faccio suonare
        # e cosi via...

        # per non rilevare zero crossing troppo improvvisi dati da variazioni veloci inaspettate o
        # soprattutto dal piegamento del ginocchio, uso una threshold adattiva sul gradiete (pendenza) degli zero crossing
        # quando la pendenza supera la threshold lo zero crossing non è valido
        
        if self.__endController() : return
        self.__nextWindow()

        displacement1 = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["displacement"]
        displacement0 = - displacement1
        valid_gradient_range = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["valid_gradient_range"] # per permettere alla soglia anche di salire
        time_threshold = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["time_threshold"] # seconds   # con una threshold temporale alta evitiamo di registrare Zc dovuti al piegamento del ginocchio
        min_gradient_threshold = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
        alpha = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["alpha"]
  
        # THIS VALUES NOT GOOD
        # if self.__sensitivity == 1: 
        #     min_gradient_threshold = 0.6
        #     valid_gradient_range = 0.2
        # elif self.__sensitivity == 2: 
        #     min_gradient_threshold = 0.5
        #     valid_gradient_range = 0.3
        # elif self.__sensitivity == 4: 
        #     min_gradient_threshold = 0.3
        #     valid_gradient_range = 0.45
        # elif self.__sensitivity == 5: 
        #     min_gradient_threshold = 0.2
        #     valid_gradient_range = 0.55

        pitch = (self.__pitch + displacement0) if not self.__pos else (self.__pitch + displacement1)
        # pitch = (self.__pitch - 1) if not self.__pos else (self.__pitch + 2)      # da positivo a negativo è più veloce quindi non anticipo, da negativo a positivo è più lento e anticipo

        # ricerca di zero crossing positivo o negativo entro la soglia
        positiveZc = self.zeroCrossingDetector(window = pitch, positive = True, maxAbsGradient = self.__gradientThreshold+valid_gradient_range)     # + 0.3 per permettere alla soglia anche di salire
        if positiveZc is not None and ((positiveZc.founded and self.__pos) or (not positiveZc.founded and not self.__pos)):
            elapsed_time = time.time() - self.__timestamp
            if elapsed_time > time_threshold:    # se self.__pos è True ho già trovaro un picco quindi lo Zc è valido    
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


    def __detectSwing(self):
        # le due gambe fanno cose diverse ma simili.
        # una gamba fa quasi solo angoli negativi e ci interessa rilevare quando si avvicina a zero (o zero crossing positivi)
        # l'altra gamba fa quasi solo angoli positivi e ci interessa rilevare quando si avvicina a zero (o zero crossing negativi)
        # sia che si inizi con la gamba andando avanti che andando indietro, la gamba avanti è la prima che fa zero crossing positivo
        # quindi uso lo stesso metodo di riconoscimento di doubleStepAnalyzer

        if self.__endController() : return
        self.__nextWindow()

        displacement = self.__parameters["swing"]["leg_detection"][f"sensitivity_{self.__sensitivity}"]["displacement"]

        if self.__auto_detectLegs:
            print("AUTO DETECTION...")
            # AUTO DETECTION
            if self.__sharedLegDetected.get() == False:
                self.detectLeg(displacement=displacement) # se il displacement è alto la piega del ginocchio deve essere più ampia, se è basso è meno

            if self.__sharedLegDetected.get() == True : 
                if self.__legDetected == False:
                    self.swingFunction(forward=False)
                else:
                    self.swingFunction(forward=True)
        else:
            if self.__selectedLeg is not None:
                # self.__selectedLeg = True se la gamba avanti è la destra False se è la sinistra
                self.swingFunction(forward=self.__selectedLeg)
    

    # potrebbe verificarsi che gli angoli negativi sono proporzionlmente più bassi rispetto ai positivi quindi si dovrebbero adottare traslazioni differenti
    # la differenza di traslazioni è data dagli angoli che fanno i piedi generalmente, gli angoli di norma variano, 
    # il piede indietro punta in fuori
    # il piede avanti punta avanti
                
    # rimane il problema della piegatura del ginocchio che si può risolvere con la threshold sul gradiente
    def swingFunction(self, forward = True):

        # Backward leg:
        # i picchi sono quasi sempre sopra -10 (15) e i minimi quasi sempre sotto -10 (15)
        # Forward leg:
        # i picchi sono quasi sempre sopra 10 e i minimi quasi sempre sotto 10

        # questo mi consente di traslare i segnali di 10 ° e - 10 °

        # standard values
        displacement0 = -15  # per la gamba davanti dato che fa angoli positivi quasi sempre sopra i 5 gradi
        displacement1 = 10  # per la gamba dietro dato che fa angoli negativi che salgono vicino a 0
        valid_gradient_range = self.__parameters["swing"][f"sensitivity_{self.__sensitivity}"]["valid_gradient_range"] # per permettere alla soglia anche di salire
        time_threshold = self.__parameters["swing"][f"sensitivity_{self.__sensitivity}"]["time_threshold"] # seconds   # con una threshold temporale alta evitiamo di registrare Zc dovuti al piegamento del ginocchio
        min_gradient_threshold = self.__parameters["swing"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]

        pitch = (self.__pitch + displacement0) if forward else (self.__pitch + displacement1)

        # ricerca di zero crossing
        positiveZc = self.zeroCrossingDetector(window = pitch, positive = True, maxAbsGradient = self.__gradientThreshold+valid_gradient_range)
        if self.__auto_detectLegs: forward = not forward
        if positiveZc is not None and ((positiveZc.founded and forward) or (not positiveZc.founded and not forward)):
            elapsed_time = time.time() - self.__timestamp
            if elapsed_time > time_threshold:    # se self.__pos è True ho già trovaro un picco quindi lo Zc è valido         
                self.__timestamp = time.time()  # update time stamp
                # play sound and increment the movement counter
                if self.__sound: self._playSample()
                # set time for bpm estimator
                if self.__calculateBpm: self.__betweenStepTimes.append(self.__timestamp)
                self.__interestingPoints.append(self.__currentGlobalIndex)
                print("gradient: " + str(self.__gradientThreshold))

                # threshold update
                self._setNewGradientThreshold(newGradient=positiveZc.absGradient, alpha=0.85, min_value=min_gradient_threshold)
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
        # 2 --> Walking in place (con sensori sulle cosce)
        # 3 --> Swing
        # 4 --> Double step

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

        # SWING

        elif exType == 3:
            print("Swing Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectSwing)

        # DOUBLE STEP

        elif exType == 4: 
            self.__threshold = self.__parameters["double_step"]["step_leg"][f"sensitivity_{self.__sensitivity}"]["min_peak_threshold"]
            self.__gradientThreshold = self.__parameters["double_step"]["other_leg"][f"sensitivity_{self.__sensitivity}"]["min_gradient_threshold"]
            print("Double Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectDoubleStep)