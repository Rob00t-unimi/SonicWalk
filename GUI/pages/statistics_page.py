from PyQt5.QtWidgets import QFrame

class StatisticsPage(QFrame):
    def __init__(self):
        super().__init__()
        # Altri codici per l'inizializzazione dell'oggetto...
        self.frame =  QFrame()
    def get_frame(self):
        return self.frame