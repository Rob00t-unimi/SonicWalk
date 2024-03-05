import simpleaudio
import time
import numpy as np

class Analyzer():
    def __init__(self) -> None:
        self.__winsize = 15 #window duration is 8.33ms * 15 ~ 125 ms
        self.__peak = 0.0
        self.__history_sz = 10 #last three steps
        self.__threshold = 2.5
        self.__peakHistory = np.full(self.__history_sz, 5.0, dtype=np.float64) #start with threshold value low to filter noise
        self.__timeThreshold = 0.1 #seconds (100 ms)
        self.__swingPhase = False
        self.__active = False
        self.__completeMovements = 0    # ex. steps
        self.__traslationFactor = 1
        self.__trasholdRange = 1.5

    def __terminate(self):
        print("analyzer daemon {:d} terminated...".format(self.__num))
        print("analyzer {:d} number of completed movements: {:d}".format(self.__num, self.__completeMovements))
        #write total number of complete movements to shared memory
        #data is written at index - 1 (termination flag at index should not be overwritten for the correct behaviour)
        self.__data[self.__index.value - 1] = self.__completeMovements

    def stepDetector(self):
        self.__threshold = 5.0
        while self.__active:
            self.__detectStep()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

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
        # questo segnale ha solo picchi negativi molto alti e lontani dal rumore, quindi non mi serve una threshold

        # Approccio 1
        # inizialmente ho pensato di ribaltare il segnale e cercare i picchi con una threshold adattiva, quando validavo un picco
        # cercavo il primo campione in un range vicino a zero per far suonare, quando lo trovavo ripartivo nel cercare un picco valido

        # Approccio 2
        # Il segnale come dicevo ha picchi molto alti negativi, quindi ribalto il segnale e lo traslo in toto in modo da negativizzare quasi tutto il rumore
        # con una traslazione di 20 siamo sicuri che non ci sarà rumore
        # con una traslazione di 10 siamo quasi sicuri che non ci sarà rumore
        # con una traslazione di 5 siamo un po' meno sicuri e e meno in anticipo ma rileviamo la marcia con passi molto piccoli
        # poi riutilizzo il codice per la step detection in cerca degli zero crossing opposti e il picco centrale

        ## MARCIA (High knees march) sulle CAVUGLIE è molto simile alla precedente e la gestisco nello stesso modo
        ## MARCIA (High knees march) sulle COSCE è anch'essa simile alle precedenti ma positiva quindi non viene ribaltata

        if self.__data[self.__index.value] == 1000:
            self.__active = False
            self.__terminate()
            return
        #Take last winsize samples from shared memory buffer
        if self.__index.value > self.__winsize:
            self.__pitch = np.array(self.__data[self.__index.value-self.__winsize:self.__index.value])
        else:
            self.__pitch = np.concatenate((np.array(self.__data[-(self.__winsize - self.__index.value):]), np.array(self.__data[:self.__index.value])))
        
        self.__threshold = 10
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
                    if self.__peak >= self.__threshold - self.__trasholdRange and elapsed_time > self.__timeThreshold:
                        # a step is valid only if last peak is greater than adaptive threshold 
                        # minus a constant angle to allow angles less than the minimum to be re gistered
                        self.__swingPhase = False #swing phase is set to false only when step is valid
                        self.__timestamp = time.time() # reset timestamp (new step)
                        _ = self.__samples[self.__sharedIndex.value()].play()
                        self.__sharedIndex.increment()

                        # update peak history with last peak
                        self.__peakHistory[self.__completeMovements % self.__history_sz] = self.__peak

                        # increment step count
                        self.__completeMovements += 1
                        #print(self.__stg)
                    self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
            else: #positiveZc
                self.__swingPhase = True


    def stepDetector_Rob(self):
        self.__threshold = 2.5
        while self.__active:
            self.__detectStep_Rob()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

    def __detectStep_Rob(self):
        # la step detection originale è molto robusta ma ha problemi a rilevare passi molto molto piccoli
        # persone con difficoltà motorie gravi spesso non sono in grado di fare dei veri e propri passi


        # siccome per gli altri segnali il metodo adottato funziona bene anche senza una threshold dinamica dato che c'è una 
        # suddivisione del segnale ben definita tra rumore e passi
        # si potrebbe pensare qui di semplificare la threshold dinamica con i percentili della finestra invece che con il picco minimo
        # oppure rimuoverla
        # si potrebbe elevare al quadrato i campioni, in modo da riuscire meglio a distinguere il rumore dai picchi


        # in alternativa, come già sperimentato (vedi sotto) si può tentare di dinamizzare anche l'anticipazione angolare e il range della threshold
        # in modo proporzionae alla grandezza della threshold

        return
            

    # Swing
                
    # 
    
    ###
    
    def __call__(self, data, index, num, sharedIndex, samples, exType):
        print('starting analyzer daemon.. {:d}'.format(num))

    #    if num == 0:
    #        self.__stg = "********************************STEP**********ZERO*********************************************"
    #    else:
    #        self.__stg = "********************************STEP***********ONE*********************************************"

        self.__num = num
        self.__data = data
        self.__index = index
        self.__sharedIndex = sharedIndex
        self.__samples = samples
        self.__timestamp = time.time()
        self.__active = True
        self.__exType = exType

        # exType
        # 0 --> walking
        # 1 --> Walking in place and Marching
        # 2 --> Walking in place (con sensori sulle cosce)
        # 3 --> Swing
        # 4 --> ??? step swing ???
        # 5 --> ROB's walking 
    
        if exType == 0: 
            print("Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.stepDetector()

        elif exType == 1 or exType == 2: 
            print("Marching Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.marchDetector()

        #elif exType == 3:
        #elif exType == 4: 
            
        elif exType == 5: 
            print("Rob's Step Analyzer")
            print('...analyzer daemon {:d} started'.format(num))
            self.stepDetector_Rob()






















































    #######################################à FAIL ############################################
            
    def stepDetector_Rob0(self):
        self.__threshold = 2.5
        while self.__active:
            self.__detectStep_Rob0()
            #allow other processes to run (wait 3ms)
            #one packet is produced roughly every 8.33ms
            time.sleep(0.003)

    def __detectStep_Rob0(self):
        if self.__data[self.__index.value] == 1000:
            self.__active = False
            self.__terminate()
            return
        
        #Take last winsize samples from shared memory buffer
        if self.__index.value > self.__winsize:
            self.__pitch = np.array(self.__data[self.__index.value-self.__winsize:self.__index.value])
        else:
            self.__pitch = np.concatenate((np.array(self.__data[-(self.__winsize - self.__index.value):]), np.array(self.__data[:self.__index.value])))
        
        # la treshold dinamica cambia dinamicamente la traslazione della finestra e il range di sensibilità
        if self.__threshold >= 1.0 : self.__traslationFactor = 0    # sotto l'1 non mi interessa andare, il minimo picco rilevato con passi minuscoli è attorno a 1.5
        if self.__threshold >= 2.5 : self.__traslationFactor = 1
        if self.__threshold >= 5 : self.__traslationFactor = 5  
        self.__trasholdRange = 3.0 * self.__threshold / 5.0     # 60 % della threshold

        #TEST: subtract a certain angle to trigger sound earlier in the cycle
        self.__pitch = self.__pitch - self.__traslationFactor

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
                    if self.__peak >= self.__threshold - self.__trasholdRange and elapsed_time > self.__timeThreshold:
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
                        #self.__threshold = newthresh if newthresh > 1.0 else 1.0

                        if newthresh <= 1.0:
                            if newthresh >= 0: 
                                self.__threshold = 1.0      # non mi interessa che vada sotto 1.0
                            else:
                                self.__threshold = 2.5      # se va su valori negativi la resetto
                        else:
                            self.__threshold = newthresh

                        print("threshold: " + str(self.__threshold))

                        # increment step count
                        self.__completeMovements += 1
                        #print(self.__stg)
                    self.__peak = 0.0 #reset peak whenever a zero crossing is encountered (negative gradient)
            else: #positiveZc
                self.__swingPhase = True
            
    def __detectMarchFail(self):
        if self.__data[self.__index.value] == 1000:
            self.__active = False
            self.__terminate()
            return
        
        #Take last winsize samples from shared memory buffer
        if self.__index.value > self.__winsize:
            self.__pitch = np.array(self.__data[self.__index.value-self.__winsize:self.__index.value])
        else:
            self.__pitch = np.concatenate((np.array(self.__data[-(self.__winsize - self.__index.value):]), np.array(self.__data[:self.__index.value])))
        
        # adattiamo l'intono del range in modo proporzionale alla threshold!
            
        # usiamo una threshold massima di 90 gradi -- eliminato
        # quando abbiamo picchi di 80 gradi l'intorno di 0 lo stimo circa da -5 a 10 -- eliminato
        # quindi facciamo che se threshold = 90, intorno di 0 da -6.5 a 12 -- eliminato
        # diminuendo la threshold diminuiamo l'intorno, la threshold minima è 20 quindi.... 
            
        sensitivity_range = 15
        self.__threshold = 20

        self.__pitch = - self.__pitch

        #self.__pitch = self.__pitch - rangeStatic      -- eliminato
        #self.__pitch[self.__pitch == (0 - rangeStatic)] = -2000 -- eliminato
        #self.__pitch[np.logical_and(-2000 < self.__pitch, self.__pitch <= 0)] = 0 -- eliminato

        
        # in questo caso non cerco gli zero crossing ma cerco solo il primo campione che rientra nell'intorno di zero definito
        # appena lo rilevo suono solo se precedentente ho rilevato un picco che supera la threshold
            
        # in pratica un picco valido è seguito da li a breve da un campione intorno a zero
        # i campioni intorno a zero successivi al primo non mi interessano più (faccio suonare solo il primo) finchè non trovo di nuovo un picco valido


        # Troviamo il picco (valore massimo) nei campioni
        if self.__swingPhase == True:
            self.__peak = np.max(self.__pitch)

        elapsed_time = time.time() - self.__timestamp

        # Controlliamo se il picco supera la soglia minima
        if self.__peak >= self.__threshold and elapsed_time > self.__timeThreshold:
            self.__timestamp = time.time()
            if self.__swingPhase == True: 
                # Ricerca del primo campione nell'intervallo intorno allo zero
                pick_index = np.argmax(self.__pitch)    # RIVEDERE, se siamo al giro successivo non ho piu l'indice
            else: 
                pick_index = 0
            for i in range(len(self.__pitch)):
                if i >= pick_index and abs(self.__pitch[i]) <= sensitivity_range:
                    # Passo valido trovato, suona e aggiorna la soglia
                    _ = self.__samples[self.__sharedIndex.value()].play()
                    self.__sharedIndex.increment()
                    
                    # Aggiorna la threshold
                    self.__peakHistory[self.__completeMovements % self.__history_sz] = self.__peak
                    new_thresh = np.min(self.__peakHistory)
                    self.__threshold = new_thresh
                    self.__threshold = new_thresh if new_thresh >= 20 else 20

                    self.__completeMovements += 1
                    print(str(self.__threshold) + " --- passo: " + str(self.__completeMovements)) 

                    self.__swingPhase = True
                    break
                else:
                    self.__swingPhase = False


    ###