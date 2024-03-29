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

import simpleaudio
import time
import numpy as np
from scipy.signal import correlate
from scipy.ndimage import gaussian_filter1d

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
        self.__foundedPitch = False
        self.__pos = True
        self.__min = 0.0
        self.__minHistory = np.full(self.__history_sz, -5.0, dtype=np.float64)

        self.__previousWindow = None
        self.__window = None

    ################################ START & END =================================================================

    def __terminate(self):
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
        return 
    
    def runAnalysis(self, method = None):
        if method is not None:
            while self.__active:
                #allow other processes to run (wait 3ms)
                #one packet is produced roughly every 8.33ms
                method()
                time.sleep(0.003)
    
    ################################ UTILS ======================================================== && Rob ========
                
    def _playSample(self):
        """
            It play a sample and increment the step counter
        """
        _ = self.__samples[self.__sharedIndex.value()].play()
        self.__sharedIndex.increment()
        self.__completeMovements += 1
        return
    
    def peakFinder(self, window, previous_window, current_window, minimum=False):
        """
        Determine if there is a positive or negative peak in the window.
        
        Requires:
            window (list): The window to analyze for the presence of a peak.
            previous_window (list): The previous window.
            current_window (list): The current window.
            minimum (bool, optional): Indicates whether the research is for peak or minimum.
                                       Defaults to False (peak).
        Effects:
            Returns: bool True if a positive or negative peak is detected in the window; otherwise, False.
            Using this function allows the determination of a positive or negative peak with a single window delay.
        """

        # Questo approccio consente di identificare la presenza di un picco in una finestra al tempo di quella successiva
        # Per la rilevazione del picco si confrontano i massimi o i minimi delle finestre consentendo cosi di abbattere il rumore
        # Infatti confrontare direttamente 3 campioni anzichè le finestre potrebbe portare ad identificazioni errate 
        # per via di oscillazioni errate nei valori causate dal rumore.

        if not minimum:
            if np.max(window) >= np.max(previous_window) and np.max(window) > np.max(current_window):
                # il picco è in window
                return True
        else:
            if np.min(window) <= np.min(previous_window) and np.min(window) < np.min(current_window):
                # il minimo è in window
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
    
    def zeroCrossingDetector(self, window, positive = True):
        """
        Detect zero crossings in the window.

        Requires:
            window (list): The window to analyze for zero crossings.
            positive (bool, optional): Indicates whether the zero crossing to detect is for positive or negative zero crossings.
                                    Defaults to True (positive zero crossing).

        Effects:
            Returns: bool True if specified zero crossing is detected; False if another type of zero crossing is detected, otherwise None.
            This function detects zero crossings in the given window, considering the specified polarity.

        """
        # zero crossings count
        cross =  np.diff(np.signbit(window))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            # determine position of zero crossing
            crossPosition = np.where(cross)[0][0]
            # determine polarity of zero-crossing (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
            negativeZc = np.signbit(np.gradient(window)[crossPosition + 1])
            if positive:
                return not negativeZc
            else:
                return negativeZc
        else:
            return None
        

    ################################ STEP DETECTION =======================================================================
        
    # RIFLESSIONE: 
    #       Siccome il segnale è pulito e il rumore è basso e quando è alto è perlopiù negativo (per via del piegamento delle ginocchia)
    #       Per rimuovere la threshold dinamica si potrebbe pensare di elevare il segnale al cubo, distanziando rumore e passi, poi aumentando la traslazione si ottiene una threshold fissa                

    def __detectStep(self):

        if self.__endController() : return
        self.__nextWindow()

        
        #TEST: subtract a certain angle to trigger sound earlier in the cycle
        self.__pitch = self.__pitch - 5

        # update peak (only in swing phase : after a positive zero-crossing is encountered 
        # - until the next zero-crossing with negative gradient)
        if self.__swingPhase == True:
            self.__peak = np.max([self.__peak, np.max(self.__pitch)])

        # Zero crossing detection
        negativeZc = self.zeroCrossingDetector(positive=False, window = self.__pitch)

        if negativeZc:
            if self.__swingPhase == True:
                elapsed_time = time.time() - self.__timestamp
                if self.__peak >= self.__threshold - 3.0 and elapsed_time > self.__timeThreshold:
                    # a step is valid only if last peak is greater than adaptive threshold 
                    # minus a constant angle to allow angles less than the minimum to be re gistered

                    self.__swingPhase = False #swing phase is set to false only when step is valid
                    self.__timestamp = time.time() # reset timestamp (new step)

                    # update peak history with last peak
                    self.__peakHistory[self.__completeMovements % self.__history_sz] = self.__peak

                    # play sound and increment the movement counter
                    self._playSample()

                    # update threshold
                    newthresh = np.min(self.__peakHistory)
                    self.__threshold = newthresh if newthresh > 5.0 else 5.0 # ensure that threshold cannot go below 2.0

                self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
        elif not negativeZc: #positiveZc
            self.__swingPhase = True

    ################################ MARCH DETECTION ======================================================== && Rob ========
        
    ### Supporta:
    #           - Marcia sul posto (Ginocchia alte - High knees march) con sensori sulle caviglie
    #           - Marcia sul posto (Ginocchia alte - High knees march) con sensori sulle cosce
    #           - Macia sul posto (piedi indietro - butt kicks) sensori sulle caviglie
            
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
        self.__threshold = 12
        if (self.__exType == 1):
            self.__pitch = - self.__pitch
        self.__pitch = self.__pitch - self.__threshold

        # Zero crossing detection
        negativeZc = self.zeroCrossingDetector(positive=False, window = self.__pitch)
        if negativeZc:
            if self.__swingPhase == True:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold:

                    # in this case the displacement is sufficient to be also the threshold
                    # so, a step is valid when we found a zero crossing after a peak value > 0

                    # set swing phase to false until we find a positive zero crossing
                    self.__swingPhase = False
                    self.__timestamp = time.time() # reset timestamp (new step)
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()

                    # increment step count
                    self.__completeMovements += 1
                    #print(self.__stg)
                self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
        elif not negativeZc: 
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

        pos = np.diff(np.signbit(pitch))
        if np.sum(pos) == 1:    
            crossPosition = np.where(pos)[0][0]
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if not negativeZc:
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

        if self.__sharedLegDetected.get() == False:
            self.detectLeg(displacement=5)

        if self.__sharedLegDetected.get() == True : 
            if self.__legDetected == False:
                self.otherLeg()
            else:
                self.stepLeg()
        return 
        
    
    # RILEVAZIONE MOVIMENTO GAMBA "CHE SI MOUOVE"
    def stepLeg(self):
            

            # IDEA:
            # La gamba in movimento genera un doppio picco positivo seguito da un doppio minimo negativo, e così via.
            # Siamo interessati solo quando il piede tocca terra, quindi per ogni coppia conta solo il primo dei due picchi (o minimi).
            # Quando rilevo un picco positivo, suono, poi cerco il secondo picco. Quando l'ho trovato, cambio la ricerca in un minimo negativo, e viceversa.


            if self.__endController() : return
            self.__nextWindow()

            def _updateWindows():
                self.__previousWindow = self.__window
                self.__window = self.__pitch

            # If the first 2 windows haven't arrived yet do nothing.
            if self.__previousWindow is None or self.__window is None: 
                _updateWindows() 
                return

            # Displacement only for denoize is optional (any involuntary movements)
            # displacement = 1
            # displacement *= -1 if self.__pos else 1
            pitch = self.__pitch #+ displacement
            previous = self.__previousWindow #+ displacement
            window = self.__window #+ displacement

            # Remove values above or below zero
            pitch[pitch <= 0 if self.__pos else pitch >= 0] = 0
            previous[previous <= 0 if self.__pos else previous >= 0] = 0
            window[window <= 0 if self.__pos else window >= 0] = 0

            # Find if there are peaks or minimum values
            findedPeak = self.peakFinder(previous_window=previous, window=window, current_window=pitch, minimum = (not self.__pos))

            # If a peak or a minimum has been found, check if it is valid
            if findedPeak:
                peak = np.max(window) if self.__pos else (-1*np.min(window))
                elapsed_time = time.time() - self.__timestamp
                if peak >= self.__threshold - self.__trasholdRange and elapsed_time > self.__timeThreshold*5:   # The threshold value not to go below seems to be 0.4 s; the peaks often occur before the footfall, so this is perfectly fine
                    if not self.__foundedPitch:
                        self.__timestamp = time.time()
                        
                        # update history and threshold
                        if self.__pos: 
                            self.__peakHistory[self.__completeMovements % self.__history_sz] = peak
                            newthresh = np.min(self.__minHistory)
                        else: 
                            self.__minHistory[self.__completeMovements % self.__history_sz] = peak
                            newthresh = np.min(self.__peakHistory)
                            # ensure that threshold cannot go below 2.0
                            self.__threshold = newthresh if newthresh > 5.0 else 5.0

                        self._playSample()
                        self.__foundedPitch = True  # first valid pitch is founded

                    else:
                        self.__foundedPitch = False # second muted pitch is founded
                        self.__pos = not self.__pos # alternate searching types of pitch every 2 peaks founded
            
            # update windows
            _updateWindows() 



#   --------------------------------------------------------------- RIVEDERE DA QUI
        
    # RILEVAZIONE MOVIMENTO GAMBA "FERMA"
    def otherLeg(self):

        ## questa gamba ha un'andamenso tipo sinusoidale quindi mi interessano gli zero crossing
        # in questo caso però mi interessano entrambi gli zero crossing che si verificano uno prima e uno dopo il picco
        # quindi cerco uno zero crossing positivo, faccio suonare
        # cerco un picco valido, quando lo trovo cerco uno zero crossing negativo
        # quando trovo lo zero crossing negativo faccio suonare e cerco un minimo valido, quando lo trovo cerco uno zero crossing positivo

        # per semplificare il codice faccio il valore assoluto e traslo in modo da validare tutti come picchi invece che alternare tra picchi e minimi
        
        if self.__endController() : return
        self.__nextWindow()

        # faccio il valore assoluto ottenendo solo picchi
        # traslo per ottenere zero crossing e anticipare

        # pitch = abs(self.__pitch)

        # if self.__pos: pitch = pitch - 5  # quando il piede poggia avanti poggia direttamente il tallone ed è più veloce a raggiungere lo zero crossing
        # else: pitch = pitch -7            # quando il piede poggia indietro poggia prima la punta poi il tallone e quindi raggiunge piu lentamente lo zero crossing
        # # il piede potrebbe metterci più tempo a raggiungere lo zero crossing negativo di quello positivo
        # # si può cercare di compensare usando displacement diversi

        # # pitch = pitch - 5

        # QUESTO MODO DI RILEVARE I PICCHI È SBAGLIATISSIMO, METTE TRUE APPENA TROVA UN NUMERO MAGGIORE DI UN ALTRO NON VA BENE IN QUESTO CASO.. DOVREBBE ASPETTARE LO ZERO CROSSING COSI...!!
        # if self.__foundedPitch == False:
        #     self.__peak = np.max([self.__peak, np.max(pitch)])
        #     self.__foundedPitch = True

        # cross =  np.diff(np.signbit(pitch))
        # if np.sum(cross) == 1:
        #     crossPosition = np.where(cross)[0][0]
        #     negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
        #     if negativeZc:
        #         elapsed_time = time.time() - self.__timestamp
        #         if self.__foundedPitch and elapsed_time > self.__timeThreshold*3.0:
        #             self.__foundedPitch = False
        #             self.__pos = not self.__pos
        #             # update time stamp
        #             self.__timestamp = time.time()
        #             # play sound
        #             _ = self.__samples[self.__sharedIndex.value()].play()
        #             self.__sharedIndex.increment()
        #             # increment step count
        #             self.__completeMovements += 1
        #         # reset peak
        #         self.__peak = 0.0

        # if self.__endController() : return
        # self.__nextWindow()










        # faccio il valore assoluto ottenendo solo picchi
        # traslo per ottenere zero crossing e anticipare

        # quando il piede poggia avanti poggia direttamente il tallone ed è più veloce a raggiungere lo zero crossing
        # quando il piede poggia indietro fa un angolo più ampio, poggia prima la punta poi il tallone e quindi raggiunge piu lentamente lo zero crossing
        # traslando in modo diverso si hanno dei delay nel suono
        # non traslando o traslando in modo uguale si hanno problemi di rumore, infatti:
        # quando il piede ha angolo poitivo potrebb verificarsi un piegamento del ginocchio che provoca zero crossing che non vorremmo rilevare
        # al contrario non accade poichè il ginocchio si piega in un sono verso
        # quindi:

        # - gli angoli negativi sono più ampi
        # - gli angoli positivi possono scendere improvvisamente sotto zero se si piega il ginocchio
        
        # soluzione:
        # - trasliamo molto in alto il segnal tagliando gli zero crossing non desiderati
        # - in questo modo ritardiamo il rilevamento degli zero crossing negativi, quindi anticipiamo ulteriormente e cerchiamo i picchi positivi

        # Algoritmo:
        # cerco zero crossing positivi, poi picchi positivi e cosi via
        # non suono subito quando trovo un picco altrimenti sarei troppo in anticipo, suono dopo un tot di tempo dalla rilevazione solo se sono sotto una soglia fissa










        # for i, tmppitch in enumerate(self.__pitch):
        #     if tmppitch < 0:
        #         self.__pitch[i] = (tmppitch**3)/1000
        pitch = self.__pitch + 20

        if self.__foundedPitch == True:
            if np.min(self.__pitch ) <= 15:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold*3:
                    self.__timestamp = time.time()
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    # increment step count
                    self.__completeMovements += 1
                    self.__pos = True
                    self.__peak = 0.0
                    self.__foundedPitch = False

        if self.__pos == False:
            last = self.__peak
            current = np.max(pitch)
            # if self.__peak > self.__threshold:
            if last > current:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold*4:
                    self.__timestamp = time.time()
                    self.__foundedPitch = True
                    self.__peak = last
            else:
                self.__peak = current
 
        cross =  np.diff(np.signbit(pitch))
        if np.sum(cross) == 1:
            crossPosition = np.where(cross)[0][0]
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if not negativeZc:
                elapsed_time = time.time() - self.__timestamp
                if self.__pos and elapsed_time > self.__timeThreshold*5:
                    self.__pos = False
                    # update time stamp
                    self.__timestamp = time.time()
                    # play sound
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    # increment step count
                    self.__completeMovements += 1
    

    ################################ SWING DETECTION ======================================================== && Rob ========


    def __detectSwing(self):
        # le due gambe fanno cose diverse ma simili.
        # una gamba fa quasi solo angoli negativi e ci interessa rilevare quando si avvicina a zero (o zero crossing positivi)
        # l'altra gamba fa quasi solo angoli positivi e ci interessa rilevare quando si avvicina a zero (o zero crossing negativi)
        # sia che si inizi con la gamba andando avanti che andando indietro, la gamba avanti è la prima che fa zero crossing positivo
        # quindi uso lo stesso metodo di riconoscimento di doubleStepAnalyzer

        if self.__endController() : return
        self.__nextWindow()

        if self.__sharedLegDetected.get() == False:
            self.detectLeg(displacement=10)

        if self.__sharedLegDetected.get() == True : 
            if self.__legDetected == False:
                self.backwardLeg()
            else:
                self.forwardLeg()
    

    # potrebbe verificarsi che gli angoli negativi sono proporzionlmente più bassi rispetto ai positivi quindi si dovrebbero adottare traslazioni differenti
    # la differenza di traslazioni è data dagli angoli che fanno i piedi generalmente, gli angoli di norma variano, 
    # il piede indietro punta in fuori
    # il piede avanti punta avanti
                
    # rimane il problema della piegatura del ginocchio

    def forwardLeg(self):
        # i minimi sono sempre sopra 10
        # i massimi locali sono sempre sotto 10
        # posso traslare di -10 e cercare gli zero crossing positivi

        pitch = self.__pitch - 10
        cross =  np.diff(np.signbit(pitch))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            # determine position of zero crossing
            crossPosition = np.where(cross)[0][0]
            # determine polarity of zero-crossing (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if negativeZc:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold * 2.0:
                    self.__timestamp = time.time()
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    self.__completeMovements += 1
    
    def backwardLeg(self):
        # i picchi sono sempre sopra -10
        # i minimi sono sempre sotto -10
        # posso traslare di 15 e cercare gli zero crossing negativi
        
        pitch = self.__pitch + 10
        cross =  np.diff(np.signbit(pitch))
        if np.sum(cross) == 1: #If more than 1 zero crossing is found then it's noise
            # determine position of zero crossing
            crossPosition = np.where(cross)[0][0]
            # determine polarity of zero-crossing (use np.gradient at index of zero crossing + 1 (the value where zero is crossed))
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if not negativeZc:
                elapsed_time = time.time() - self.__timestamp
                if elapsed_time > self.__timeThreshold * 2.0:
                    self.__timestamp = time.time()
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    self.__completeMovements += 1


    ################################ OBJECT CALL ======================================================== && Rob ========

    
    def __call__(self, data, index, num, sharedIndex, samples, exType, sharedLegBool, syncProcesses):
        
        self.syncProcesses = syncProcesses

        self.syncProcesses()
        print('starting analyzer daemon.. {:d}'.format(num))
        print(("start time: ") + str(time.time()))

        self.__num = num
        self.__data = data
        self.__index = index
        self.__sharedIndex = sharedIndex
        self.__samples = samples
        self.__timestamp = time.time()
        self.__active = True
        self.__exType = exType
        self.__sharedLegDetected = sharedLegBool

        # exType= False
        # 0 --> walking
        # 1 --> Walking in place and Marching
        # 2 --> Walking in place (con sensori sulle cosce)
        # 3 --> Swing
        # 4 --> Double step
    
        if exType == 0: 
            print("Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectStep)

        elif exType == 1 or exType == 2: 
            print("Marching Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectMarch)

        elif exType == 3:
            print("Swing Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectSwing)

        elif exType == 4: 
            print("Double Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.runAnalysis(method=self.__detectDoubleStep)