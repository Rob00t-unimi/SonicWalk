from multiprocessing import Value, Event, Lock
import time


class SharedCircularIndex():
    def __init__(self, maxval):
        self.index = Value('i', 0)
        self.maxval = maxval
    def increment(self):
        with self.index.get_lock():
            self.index.value = (self.index.value + 1) % self.maxval
    def value(self):
        with self.index.get_lock():
            return self.index.value
        
class LegDetected():
    """
        Shared variable for inter process comunication of the detected leg
    """
    def __init__(self):
        self.value = Value("b", False)
        #self.syncIndex0 = 0
        #self.syncIndex1 = 0

    def set(self, value):
        with self.value.get_lock():
            if self.value.value == value:
                return False    # not setted
            self.value.value = value
            print("gamba in movimento rilevata")
            return True # setted
    def get(self):
        with self.value.get_lock():
            return self.value.value
        
class ProcessWaiting():
    """
        inter process comunication to understand when both are running
        Synchronize the processes with a delay < 0.0001 seconds.
    """
    def __init__(self):
        self.secondProcessStart = Event()
        self.firstProcessStart = Event()

        self.firstLock = Lock()
        self.secondLock = Lock()

    def _second(self):
        self.secondProcessStart.set()

    def _first(self):
        self.firstProcessStart.set()
        # una volta emesso il primo segnale imposto l'attesa del secondo
        self.secondProcessStart.wait()
        # una volta emesso il secondo segnale ripulisco entrambi i segnali
        self.secondProcessStart.clear()
        self.firstProcessStart.clear()

    def start(self):    # chiamata da uno dei 2 processi
        
        # se è il secondo processo a chiamare start il primo segnale è già stato emesso quindi emetto il secondo segnale e termino
        if self.firstProcessStart.is_set():
            with self.secondLock:
                self._second()

        # se è il primo il primo processo a chiamare start il primo segnale non è stato emesso quindi lo emetto
        else:
            with self.firstLock:
                self._first()
        

        
