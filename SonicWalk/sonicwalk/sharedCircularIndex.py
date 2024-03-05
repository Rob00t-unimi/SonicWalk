from multiprocessing import Value

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