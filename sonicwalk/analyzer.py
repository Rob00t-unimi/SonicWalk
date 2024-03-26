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
    
    def stepDetector(self):
        while self.__active:
            self.__detectStep()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

    def __detectStep(self):

        if self.__endController() : return
        self.__nextWindow()

        
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
                        self.__peakHistory[self.__completeMovements % self.__history_sz] = self.__peak

                        # update threshold
                        newthresh = np.min(self.__peakHistory)
                        # ensure that threshold cannot go below 2.0
                        self.__threshold = newthresh if newthresh > 5.0 else 5.0
                        #print("threshold: " + str(self.__threshold))
                        # increment step count
                        self.__completeMovements += 1
                        #print(self.__stg)
                    self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
            else: #positiveZc
                self.__swingPhase = True

        
    ### ALTRI METODI DI DETECTION
                
    ### Macia sul posto (piedi indietro - butt kicks) sensori sulle caviglie
    ### Questo metodo va bene anche per la Marcia sul posto (Ginocchia alte - High knees march) se si montano i sensori sulle caviglie
    ### Inoltre è stato adattato per andare bene anche con la camminata sul posto (Ginocchia alte - High knees march) con sensori sulle cosce
                
    def marchDetector(self):
        while self.__active:
            self.__detectMarch()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

    def __detectMarch(self):

        ## MARCIA (butt kicks)
        # questo segnale ha solo picchi positivi molto alti e lontani dal rumore, quindi non mi serve una threshold

        # Approccio 1
        # inizialmente ho pensato di ribaltare il segnale e cercare i picchi con una threshold adattiva, quando validavo un picco
        # cercavo il primo campione in un range vicino a zero per far suonare, quando lo trovavo ripartivo nel cercare un picco valido

        # Approccio 2
        # Il segnale come dicevo ha picchi molto alti, quindi traslo in toto in modo da negativizzare quasi tutto il rumore
        # con una traslazione di 20 siamo sicuri che non ci sarà rumore
        # con una traslazione di 10 siamo quasi sicuri che non ci sarà rumore
        # con una traslazione di 5 siamo un po' meno sicuri e e meno in anticipo ma rileviamo la marcia con passi molto piccoli
        # poi riutilizzo il codice per la step detection in cerca degli zero crossing opposti e il picco centrale

        ## MARCIA (High knees march) sulle CAVIGLIE è molto simile alla precedente e la gestisco nello stesso modo
        ## MARCIA (High knees march) sulle COSCE è anch'essa simile alle precedenti ma negativa quindi viene ribaltata

        if self.__endController() : return
        self.__nextWindow()


        self.__threshold = 12
        if (self.__exType == 1):
            self.__pitch = - self.__pitch
        self.__pitch = self.__pitch - self.__threshold

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
                    if elapsed_time > self.__timeThreshold:
                        # a step is valid only if last peak is greater than adaptive threshold 
                        # minus a constant angle to allow angles less than the minimum to be re gistered
                        self.__swingPhase = False #swing phase is set to false only when step is valid
                        self.__timestamp = time.time() # reset timestamp (new step)
                        _ = self.__samples[self.__sharedIndex.value()].play()
                        self.__sharedIndex.increment()

                        # increment step count
                        self.__completeMovements += 1
                        #print(self.__stg)
                    self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
            else: #positiveZc
                self.__swingPhase = True

    ### double Step exercise

    def doubleStepDetector(self):
        while self.__active:
            self.__detectDoubleStep()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)


    def __detectDoubleStep(self):

        ### Le due gambe hanno segnali differenti che quindi devono essere distinti e analizzati in modo diverso

        
        if self.__endController() : return
        self.__nextWindow()

        if self.__sharedLegDetected.get() == False:
            self.detectLeg()

        if self.__sharedLegDetected.get() == True : 
            if self.__legDetected == False:
                self.otherLeg()
            else:
                self.stepLeg()
        return
    

    # DISTINGUERE AUTOMATICAMENTE LE GAMBE
    def detectLeg(self, displacement = None):

        # normalmente un'esercizio parte con il passo in avanti non con quello indietro quindi il primo segnale che avrà uno zero crossing positivo
        # identificherà a gamba che fa il passo avanti e indietro, l'altro segnale identificherà la gamba "ferma"

        ## In questa versione semplicemente cerco il segnale che per primo fa lo zero crossing positivo e comunico ad una variabile condivisa ai 2 processi
        # applico lo scostamento per 2 motivi
        # 1: taglio possibili zerogrossing dati dal rumore
        # 2: scosto di molto poichè i processi non iniziano insieme, 
        # ipotizziamo che il segnale 1 inizi al tempo 0 ma è il segnale per cui non ci interessa lo zero crossing
        # segnale 2 inizia al tempo 1 ma ci interessa il suo zero crossing
        # potrebbe verificarsi che rilevo prima lo zero crossing del segnale 1 rispetto a quello del segnale 1
        # traslando in basso di cosi tanto (11) invece, siccome il segnale 1 è più ampio ovvero varia più lentamente
        # sto ritardando la rilevazione di entrambi i segnali, ma la rilevazione del segnale 1 risulta più ritardata rispetto a quella del segnale 2
        # in questo modo sono sempre sicuro (eccetto movimenti sotto i 10 gradi) che il segnale 2 viene sempre rilevato prima del segnale 1

        # proseguendo l'esempio ...
        # quando rilevo lo zero crossing positivo nel processo 2 setto una variabile condivisa ai 2 processi su true cosi da comunicare al processo 1 che 
        # il segnale 2 è quello che stavamo cercando e si trova nel processo 2, di conseguenza il processo 1 capisce di avere il segnale 1

        pitch = self.__pitch - 7           # aumentando il valore sottratto si aumenta la precisione nella rilevazione tuttavia aumenta l'ampiezza del passo richiesto
                                            # diminuendo si perde una corretta rilevazione
        
        if displacement is not None:
            pitch =  self.__pitch - displacement

        pos = np.diff(np.signbit(pitch))
        if np.sum(pos) == 1:    
            crossPosition = np.where(pos)[0][0]
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if not negativeZc:
                setted = self.__sharedLegDetected.set(True)
                if setted: self.__legDetected = True
        return    
        
    
    # RILEVAZIONE MOVIMENTO GAMBA "CHE SI MOUOVE"
    def stepLeg(self):
            
            ## la gamba che si muove fa un doppio picco positivo poi doppio negativo etc..
            # a noi interessa solo quando poggia terra ovvero per ogni coppia solo il primo dei 2 picchi
            # quando rilevo un picco positivo quindi imposto la ricerca sul negativo e viceversa
            # quando rilevo un picco valido suono

            if self.__endController() : return
            self.__nextWindow()

            # traslo per togliere rumore
            pos = self.__pitch - 7
            neg = self.__pitch + 7
            
            # divido i campioni >= 0 da quelli <= 0
            for index, s in enumerate(self.__pitch):
                if s <= 0:
                    pos[index] = 0
                if s >= 0:
                    neg[index] = 0

            if self.__pos:
                # analizzo i positivi cercando i picchi
                last = self.__peak
                self.__peak = np.max(pos)
                current = self.__peak
            else: 
                # analizzo i negativi cercando i minimi
                # lo faccio ribaltando e cercando comunque i massimi
                last = self.__min
                neg = - neg
                self.__min = np.max(neg)
                current = self.__min

            if last > current:

                    elapsed_time = time.time() - self.__timestamp
                    if last >= self.__threshold - self.__trasholdRange and elapsed_time > self.__timeThreshold*5:

                        # a step is valid only if last peak is greater than adaptive threshold 
                        # minus a constant angle to allow angles less than the minimum to be re gistered
                        self.__timestamp = time.time() # reset timestamp (new step)
                        _ = self.__samples[self.__sharedIndex.value()].play()
                        self.__sharedIndex.increment()

                        # update history and threshold
                        if self.__pos: 
                           self.__peakHistory[self.__completeMovements % self.__history_sz] = last 
                           newthresh = np.min(self.__minHistory)
                        else: 
                           self.__minHistory[self.__completeMovements % self.__history_sz] = last
                           newthresh = np.min(self.__peakHistory)
                        # ensure that threshold cannot go below 2.0
                        self.__threshold = newthresh if newthresh > 5.0 else 5.0

                        self.__completeMovements += 1
                        self.__pos = not self.__pos

        
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

        pitch = abs(self.__pitch)

        if self.__foundedPitch == False:
            self.__peak = np.max([self.__peak, np.max(pitch)])
            self.__foundedPitch = True

        if self.__pos: pitch = pitch - 5  # quando il piede poggia avanti poggia direttamente il tallone ed è più veloce a raggiungere lo zero crossing
        else: pitch = pitch -7            # quando il piede poggia indietro poggia prima la punta poi il tallone e quindi raggiunge piu lentamente lo zero crossing
        # il piede potrebbe metterci più tempo a raggiungere lo zero crossing negativo di quello positivo
        # si può cercare di compensare usando displacement diversi

        cross =  np.diff(np.signbit(pitch))
        if np.sum(cross) == 1:
            crossPosition = np.where(cross)[0][0]
            negativeZc = np.signbit(np.gradient(pitch)[crossPosition + 1])
            if negativeZc:
                elapsed_time = time.time() - self.__timestamp
                if self.__foundedPitch and elapsed_time > self.__timeThreshold*4:
                    self.__foundedPitch = False
                    self.__pos = not self.__pos
                    # update time stamp
                    self.__timestamp = time.time()
                    # play sound
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    # increment step count
                    self.__completeMovements += 1
                # reset peak
                self.__peak = 0.0



    
    ## SWING

    def swingDetector(self):
        while self.__active:
            self.__detectSwing()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

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
    

    # la differenza di traslazioni è data dagli angoli che fanno i piedi generalmente, gli angoli di norma variano, 
    # il piede indietro punta in fuori
    # il piede avanti punta avanti

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
                if elapsed_time > self.__timeThreshold * 2:
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
                if elapsed_time > self.__timeThreshold * 2:
                    self.__timestamp = time.time()
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    self.__completeMovements += 1
    
    def __call__(self, data, index, num, sharedIndex, samples, exType, sharedLegBool, first):
        print('starting analyzer daemon.. {:d}'.format(num))

        if first: time.sleep(0.003)
        print(("primo: " if first else "secondo") +str(time.time()))

        self.__num = num
        self.__data = data
        self.__index = index
        self.__sharedIndex = sharedIndex
        self.__samples = samples
        self.__timestamp = time.time()
        self.__active = True
        self.__exType = exType
        self.__sharedLegDetected = sharedLegBool
        self.isFirstProcess = first

        # exType= False
        # 0 --> walking
        # 1 --> Walking in place and Marching
        # 2 --> Walking in place (con sensori sulle cosce)
        # 3 --> Swing
        # 4 --> Double step
    
        if exType == 0: 
            print("Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.stepDetector()

        elif exType == 1 or exType == 2: 
            print("Marching Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.marchDetector()

        elif exType == 3:
            print("Swing Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.swingDetector()

        elif exType == 4: 
            print("Double Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.doubleStepDetector()