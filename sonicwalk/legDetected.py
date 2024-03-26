from multiprocessing import Value
import time
class LegDetected():
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
        
        