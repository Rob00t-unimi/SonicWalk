from PyQt5.QtWidgets import QFrame
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
import numpy as np

sys.path.append("../")

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

class AnalysisPage(QFrame):

    # sets up pyqt signal to use with multithreading
    mtw_run_finished = pyqtSignal()
    
    def __init__(self, light = True):
        """
        Requires:
            - light: Boolean indicating whether the theme is light or dark.
        Modifies:
            - Initializes UI components including patient frame, exercise frame, recording frame, and plotter frame.
            - Handles theme toggling.
            - Toggles the enabled or disabled state of buttons and selects in response to user interaction with play button.
        Effects:
            - Sets up the user interface for the analysis page.
            - Manages the interaction and behavior of UI components.
        """
        super().__init__()

        # Initialize attributes
        self.light = light
        self.playButtonAbilited = False
        self.allEnabled = True

        # initialize self
        self.setup_ui()

    def setup_ui(self):
        """
            Modifies:   self
            Effects:    Sets up the user interface for the analysis page.
        """

        # set layout
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # create sub frames
        self.selection_frame = ExerciseFrame(light=self.light)
        self.actions_frame = RecordingFrame(getBpm = self.selection_frame.getBpm, getMusicModality = self.selection_frame.getMusicModality, getMusicPath = self.selection_frame.getMusicPath, getExerciseNumber = self.selection_frame.getExerciseNumber, light = self.light, changeEnabledAll = self.changeEnabledAll)
        self.patient_frame = PatientFrame(light=self.light, enablePlayButton = self.actions_frame.enablePlayButton, disablePlayButton = self.actions_frame.disablePlayButton) 
        self.actions_frame.getPatient = self.patient_frame.getPatient
        self.plotter_frame = QFrame()
        layout_plotter = QVBoxLayout(self.plotter_frame)
        layout_plotter.setContentsMargins(10, 0, 0, 0)
        plotter_canvas = self.createPlotter()
        layout_plotter.addWidget(plotter_canvas)

        # add subframes in the grid
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
        """
            Modifies:   self
            Effects:    Toggles the theme for UI components including patient frame, exercise frame, and recording frame.
        """
        self.light = not self.light
        self.patient_frame.toggleTheme()
        self.selection_frame.toggleTheme()
        self.actions_frame.toggleTheme()

    def changeEnabledAll(self):
        """
            Modifies:   Toggles the enabled state of buttons and selects.
            Effects:    Enables or disables all buttons and selects based on the current state.
        """
        self.allEnabled = not self.allEnabled
        self._disableButtonsInFrame(self)   # change enabled state of buttons
        self._disableSelectsInFrame(self)   # change enabled state of selects
        self._enableStopRecordingButton()   # enable recording button

        # change enabled state of slider
        slider = self.selection_frame.findChild(QSlider)
        if slider:
            slider.setEnabled(not slider.isEnabled())

    def _disableButtonsInFrame(self, frame):
        """
            Requires:   frame: The frame containing buttons.
            Modifies:   Disables buttons within the specified frame.
            Effects:    Disables all buttons recursively within the frame.
        """
        # Iterate over all widgets within the frame, enabling or disabling buttons
        for widget in frame.findChildren(QWidget):
            if isinstance(widget, QPushButton):
                widget.setEnabled(False if not self.allEnabled else True)
            elif isinstance(widget, QFrame):
                self._disableButtonsInFrame(widget)

    def _disableSelectsInFrame(self, frame):
        """
            Requires:   frame: The frame containing combo boxes.
            Modifies:   Disables combo boxes within the specified frame.
            Effects:    Disables all combo boxes recursively within the frame.
        """
        # Iterate over all widgets within the frame, enabling or disabling selects
        for widget in frame.findChildren(QWidget):
            if isinstance(widget, QComboBox):
                widget.setEnabled(False if not self.allEnabled else True)
            elif isinstance(widget, QFrame):
                self._disableSelectsInFrame(widget)
    
    def _enableStopRecordingButton(self):
        """
            Modifies:   Enables the stop recording button within the actions frame.
            Effects:    Enables the stop recording button when called.
        """
        # Iterate over all widgets within the frame and enable the stop recording button
        for widget in self.actions_frame.findChildren(QWidget):
            if isinstance(widget, QPushButton) and widget.toolTip() == "Stop recording":
                widget.setEnabled(True)
                break  
    
    def createPlotter(self):
        # Example of two simple signals
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Create figure and axes
        fig, ax = plt.subplots()
        ax.plot(x, y1, label='Sin(x)')
        ax.plot(x, y2, label='Cos(x)')
        ax.legend()  # Show the legend

        # Create canvas for the plot
        canvas = FigureCanvas(fig)
        canvas.setContentsMargins(0, 0, 0, 0)

        # Add canvas to the plotter layout
        layout_plotter = self.plotter_frame.layout()
        layout_plotter.addWidget(canvas)

        return canvas


