from PyQt5.QtWidgets import QFrame
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
import numpy as np

gui_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(gui_path)

from frames.patientFrame import PatientFrame
from frames.exerciseFrame import ExerciseFrame
from frames.recordingFrame import RecordingFrame

# quando si chiude il programma, se sta regstrando assicurarsi prima di terminare in modo sicuro la registrazione
# aggiungere funzione che permette di terminare
# aggiungere il plotter 
    # il plotter può essere aggiunto istanziandolo in mtwRecord e prendendo quell'istanza oppure
    # istanziandolo qui nella gui e recuperando i dati condivisi di mtwRecord
# il beep all'inizio della registrazione occupa la risorsa e genera errore quindi è temporaneamente commentato
# i path di suoni e musica vanno recuperati dinamicamente
# bisogna gestire e recuperare l'eccezione nel caso non sia inserito il dongle
# implementare un sistema per far suonare la musica

class AnalysisPage(QFrame):

    mtw_run_finished = pyqtSignal()
    
    def __init__(self, light = True, parent=None):
        super().__init__(parent)

        self.light = light
        self.playButtonAbilited = False

        self.setup_ui()

    def setup_ui(self):

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        self.selection_frame = ExerciseFrame(light=self.light)
        self.actions_frame = RecordingFrame(getMusicModality = self.selection_frame.getMusicModality, getMusicPath = self.selection_frame.getMusicPath, getExerciseNumber = self.selection_frame.getExerciseNumber, light = self.light )
        self.patient_frame = PatientFrame(light=self.light, enablePlayButton = self.actions_frame.enablePlayButton, disablePlayButton = self.actions_frame.disablePlayButton) 
        self.plotter_frame = QFrame()

        layout_plotter = QVBoxLayout(self.plotter_frame)

        layout_plotter.setContentsMargins(10, 0, 0, 0)

        # Ottieni il canvas del plotter
        plotter_canvas = self.createPlotter()

        # Aggiungi il canvas al layout del frame del plotter
        layout_plotter.addWidget(plotter_canvas)


        # add frames in the grid
        grid_layout.addWidget(self.patient_frame, 0, 0)
        grid_layout.addWidget(self.plotter_frame, 0, 1)
        grid_layout.addWidget(self.selection_frame, 1, 0)
        grid_layout.addWidget(self.actions_frame, 1, 1)

        # grid proportions
        grid_layout.addWidget(self.patient_frame, 0, 0, 1, 1)  # Alto a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.selection_frame, 1, 0, 2, 1)  # Basso a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.plotter_frame, 0, 1, 2, 3)  # Alto a destra, altezza 2/3, larghezza 2/3
        grid_layout.addWidget(self.actions_frame, 2, 1, 1, 3)  # Basso a destra, altezza 1/3, larghezza 2/3

        self.patient_frame.setMinimumWidth(200)
        self.plotter_frame.setMinimumWidth(200)
        self.selection_frame.setMinimumWidth(200)
        self.actions_frame.setMinimumWidth(200)

        # expansion policy
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

        # margins
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)


    def toggleTheme(self):
        self.light = not self.light
        self.patient_frame.toggleTheme()
        self.selection_frame.toggleTheme()
        self.actions_frame.toggleTheme()

    def createPlotter(self):
        # Esempio di due segnali semplici
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        fig, ax = plt.subplots()
        ax.plot(x, y1, label='Sin(x)')
        ax.plot(x, y2, label='Cos(x)')
        ax.legend()  # Mostra la legenda

        # Creazione del canvas per il plot
        canvas = FigureCanvas(fig)
        canvas.setContentsMargins(0, 0, 0, 0)

        # Aggiunta del canvas al layout del plotter
        layout_plotter = self.plotter_frame.layout()
        layout_plotter.addWidget(canvas)

        return canvas
