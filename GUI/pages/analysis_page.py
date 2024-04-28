import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

sys.path.append("../")

from frames.patientFrame import PatientFrame
from frames.exerciseFrame import ExerciseFrame
from frames.recordingFrame import RecordingFrame
sys.path.append("../")
from sonicwalk.sharedVariables import SharedData
import time
from PyQt5.QtCore import QThread



# quando si chiude il programma, se sta regstrando assicurarsi prima di terminare in modo sicuro la registrazione
# aggiungere funzione che permette di terminare
# aggiungere il plotter 
    # il plotter può essere aggiunto istanziandolo in mtwRecord e prendendo quell'istanza oppure
    # istanziandolo qui nella gui e recuperando i dati condivisi di mtwRecord
# il beep all'inizio della registrazione occupa la risorsa e genera errore quindi è temporaneamente commentato
# bisogna gestire e recuperare l'eccezione nel caso non sia inserito il dongle



class AnalysisPage(QWidget):

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
        self.shared_data = SharedData()

        # initialize self
        self.setup_ui()

    def setup_ui(self):
        """
            Modifies:   self
            Effects:    Sets up the user interface for the analysis page.
        """

        # set layout
        grid_layout = QGridLayout(self)
        # grid_layout.setContentsMargins(0, 0, 0, 0)

        # create sub frames
        self.selection_frame = ExerciseFrame(light=self.light)
        self.actions_frame = RecordingFrame(setBpm = self.selection_frame.setBpm, getBpm = self.selection_frame.getBpm, getMusicModality = self.selection_frame.getMusicModality, getMusicPath = self.selection_frame.getMusicPath, getExerciseNumber = self.selection_frame.getExerciseNumber, light = self.light, changeEnabledAll = self.changeEnabledAll, shared_data=self.shared_data, plotter_start = self.plotter_start, setSaved = self.setSaved)#, mtw_run_finished = self.mtw_run_finished)
        self.patient_frame = PatientFrame(light=self.light, enablePlayButton = self.actions_frame.enablePlayButton, disablePlayButton = self.actions_frame.disablePlayButton) 
        self.actions_frame.getPatient = self.patient_frame.getPatient
        self.plotter_frame = QWidget()
        self.layout_plotter = QVBoxLayout(self.plotter_frame)
        self.layout_plotter.setContentsMargins(0, 0, 0, 0)


        self.create_static_plotter() # initialize a void plotter
        self.layout_plotter.addWidget(self.canvas)   # add the plotter into the gui

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
        self.selection_frame.setMinimumWidth(375)
        self.actions_frame.setMinimumWidth(375)

        # expansion policy
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

        # margins
        # grid_layout.setContentsMargins(0, 0, 0, 0)
        # self.setContentsMargins(0, 0, 0, 0)

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

    def plotter_start(self):
        print("plotter starting...")
        if hasattr(self, 'plot_thread') and self.plot_thread.isRunning():
            self.plot_thread.terminate()
        self.plot_thread = PlotterThread(self.shared_data.data0, self.shared_data.data1, self.shared_data.index0, self.shared_data.index1)
        self.plot_thread.dataUpdated.connect(self.update_plot)
        self.plot_thread.termination.connect(self.reset_shared_data)
        self.plot_thread.start()

    def create_static_plotter(self):
        self.fig, self.ax = plt.subplots()
        self.ax.plot([], [], label='Data 0')
        self.ax.plot([], [], label='Data 1')
        self.ax.set_xticks([])
        # self.ax.legend()
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        # self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)
    
    def update_plot(self, data0, data1):
        # Aggiorna il plotter con i nuovi dati
        self.ax.clear()
        self.ax.plot(data0, 'b')
        self.ax.plot(data1, 'c')
        self.ax.set_xticks([])
        # self.ax.legend()
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        # self.fig.tight_layout()
        self.canvas.draw()

    def setSaved(self, data):
        if hasattr(self, 'plot_thread'):
            self.plot_thread.force_stop()
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        if data is not None:
            self.ax.plot(data[0], 'b')
            self.ax.plot(data[1], 'c')
            self.isSaved = None
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        # self.fig.tight_layout()
        self.canvas.draw()
        
    def reset_shared_data(self):
        self.shared_data.index0.value = 0
        self.shared_data.index1.value = 0
        for i in range(len(self.shared_data.data0)):
            self.shared_data.data0[i] = 0
        for i in range(len(self.shared_data.data1)):
            self.shared_data.data1[i] = 0

class PlotterThread(QThread):
    dataUpdated = pyqtSignal(np.ndarray, np.ndarray)
    termination = pyqtSignal()

    def __init__(self, data0, data1, index0, index1):
        super().__init__()
        print("init plotter...")
        self.data0 = data0
        self.data1 = data1
        self.index0 = index0
        self.index1 = index1
        self.stop = False

    def run(self):
        print("plotter running...")
        while True:
            if self.data0[self.index0.value] == 1000:
                self.termination.emit()
                print("terminate plotter process...")
                return
            data0 = np.array(self.data0)
            data1 = np.array(self.data1)

            self.dataUpdated.emit(data0, data1)
            time.sleep(0.07)

    def force_stop(self):
        if self.isRunning():
            self.data0[self.index0.value] = 1000
            self.stop = True