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

from multiprocessing import Value, Event, Lock, RawArray, RawValue
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

class SharedData:
    def __init__(self):
        self.index0 = RawValue('i', 0)
        self.index1 = RawValue('i', 0)
        self.data0 = RawArray('d', 1000)
        self.data1 = RawArray('d', 1000)
    

        

        
