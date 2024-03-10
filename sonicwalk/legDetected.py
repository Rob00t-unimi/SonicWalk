from multiprocessing import Value
import time
class LegDetected():
    def __init__(self):
        self.value = Value("b", False)
        #self.syncIndex0 = 0
        #self.syncIndex1 = 0

    def set(self, value):
        with self.value.get_lock():
            self.value.value = value
            print("gamba in movimento rilevata")
            return
    def get(self):
        with self.value.get_lock():
            return self.value.value
        
        