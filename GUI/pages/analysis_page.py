from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from GUI.frames.patientFrame import PatientFrame
from GUI.frames.exerciseFrame import ExerciseFrame
from GUI.frames.recordingFrame import RecordingFrame
import sys
import os
sys.path.append("../")
sys.path.append(os.getcwd())
from sonicwalk.sharedVariables import SharedData
import time
from PyQt5.QtCore import QThread

# bisogna gestire e recuperare l'eccezione nel caso non sia inserito il dongle

class AnalysisPage(QWidget):
    """
    Page for registering, managing, and analyzing rehabilitative exercises for patients.
    """
    def __init__(self, light = True):
        """
        REQUIRES:
            - light: Boolean indicating whether the theme is light or dark.

        MODIFIES:
            - self

        EFFECTS:
            - Sets up the user interface for the analysis page. Including patient frame, exercise frame, recording frame, and plotter frame.
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
        MODIFIES:   
            - self
        EFFECTS:    
            - Sets up the user interface for the analysis page. Including patient frame, exercise frame, recording frame, and plotter frame.
        """

        # set layout
        grid_layout = QGridLayout(self)

        # create sub frames
        self.selection_frame = ExerciseFrame(light=self.light)
        self.actions_frame = RecordingFrame(setBpm = self.selection_frame.setBpm, getBpm = self.selection_frame.getBpm, getMusicModality = self.selection_frame.getMusicModality, getMusicPath = self.selection_frame.getMusicPath, getExerciseNumber = self.selection_frame.getExerciseNumber, getSelectedLeg=self.selection_frame.getSelectedLeg, light = self.light, changeEnabledAll = self.changeEnabledAll, shared_data=self.shared_data, plotter_start = self.plotter_start, setSaved = self.setSaved)#, mtw_run_finished = self.mtw_run_finished)
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
        grid_layout.addWidget(self.patient_frame, 0, 0, 1, 1)  # Top left, height 1/3, width 1/3
        grid_layout.addWidget(self.selection_frame, 1, 0, 2, 1)  # Bottom left, height 1/3, width 1/3
        grid_layout.addWidget(self.plotter_frame, 0, 1, 2, 3)  # Top right, height 2/3, width 2/3
        grid_layout.addWidget(self.actions_frame, 2, 1, 1, 3)  # Bottom right, height 1/3, width 2/3

        self.patient_frame.setMinimumWidth(200)
        self.plotter_frame.setMinimumWidth(200)
        self.selection_frame.setMinimumWidth(375)
        self.actions_frame.setMinimumWidth(375)

        # expansion policy
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

    def set_update_patient_list(self, func):
        """
        REQUIRES: 
            - func (callable): function to reload the archive patient list
            
        MOFIFIES: 
            - self

        EFFECTS:
            - pass the function to the patient frame object
        """
        self.patient_frame.reload_archive_patient_list = func

    def changeEnabledAll(self):
        """
        MOFIFIES:   
            - Toggles the enabled state of buttons and selects.

        EFFECTS:    
            - Enables or disables all buttons (except for stop button), selects and slider based on the current state.
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
        REQUIRES:   
            - frame (QWidget): The frame containing buttons.

        EFFECTS:    
            - Disables all buttons recursively within the frame.
        """
        # Iterate over all widgets within the frame, enabling or disabling buttons
        for widget in frame.findChildren(QWidget):
            if isinstance(widget, QPushButton):
                widget.setEnabled(False if not self.allEnabled else True)
            elif isinstance(widget, QFrame):
                self._disableButtonsInFrame(widget)

    def _disableSelectsInFrame(self, frame):
        """
        REQUIRES:   
            - frame (QWidget): The frame containing combo boxes.

        EFFECTS:    
            - Disables all combo boxes recursively within the frame.
        """
        # Iterate over all widgets within the frame, enabling or disabling selects
        for widget in frame.findChildren(QWidget):
            if isinstance(widget, QComboBox):
                widget.setEnabled(False if not self.allEnabled else True)
            elif isinstance(widget, QFrame):
                self._disableSelectsInFrame(widget)
    
    def _enableStopRecordingButton(self):
        """
        EFFECTS:    
            - Enables the stop recording button within the actions frame.
        """
        # Iterate over all widgets within the frame and enable the stop recording button
        for widget in self.actions_frame.findChildren(QWidget):
            if isinstance(widget, QPushButton) and widget.property("icon_name") == "stop":
                widget.setEnabled(True)
                break  

    def plotter_start(self):
        """
        MODIFIES: 
            - self

        EFFECTS:    
            - Initializes, Shows and Starts the plotter thread class for dynamic plotter.
        """
        print("plotter starting...")
        if hasattr(self, 'plot_thread') and self.plot_thread.isRunning():
            self.plot_thread.terminate()
        self.plot_thread = PlotterThread(self.shared_data.data0, self.shared_data.data1, self.shared_data.index0, self.shared_data.index1)
        self.plot_thread.dataUpdated.connect(self.update_plot)
        self.plot_thread.termination.connect(self.reset_shared_data)
        self.plot_thread.start()

    def create_static_plotter(self):
        """
        MODIFIES: 
            - self

        EFFECTS:    
            - Initializes and shows the static plotter.
        """
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
        """
        REQUIRES: 
            - data0 (np.ndarray): Array containing data of signal 0.
            - data1 (np.ndarray): Array containing data of signal 1.

        EFFECTS:    
            - Updates the dynamic plotter with new data.
        """
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
        """
        REQUIRES: 
            - data (tuple or None): Tuple containing data for plots or None.

        EFFECTS:    
            - Sets the data in the plotter and updates it.
        """
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
        """
        MODIFIES: 
            - self SharedData object

        EFFECTS:    
            - Resets shared data (all 0).
        """
        self.shared_data.index0.value = 0
        self.shared_data.index1.value = 0
        for i in range(len(self.shared_data.data0)):
            self.shared_data.data0[i] = 0
        for i in range(len(self.shared_data.data1)):
            self.shared_data.data1[i] = 0

class PlotterThread(QThread):

    """
    Dynamic plotter thread object.
    """
    
    dataUpdated = pyqtSignal(np.ndarray, np.ndarray)
    termination = pyqtSignal()

    def __init__(self, data0, data1, index0, index1):
        """
        REQUIRES: 
            - data0 (list): List containing data for plot 0.
            - data1 (list): List containing data for plot 1.
            - index0 (int): Index for data0.
            - index1 (int): Index for data1.

        MODIFIES:
            - self

        EFFECTS:
            - Initializes the PlotterThread.
        """
        super().__init__()
        print("init plotter...")
        self.data0 = data0
        self.data1 = data1
        self.index0 = index0
        self.index1 = index1
        self.stop = False

    def run(self):
        """
        EFFECTS:    
            - Runs the PlotterThread.
            - terminates when find 1000 in data0
        """
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
        """
        MODIFIES:
            self
            
        EFFECTS:    
            - Forces the PlotterThread to stop.
        """
        if self.isRunning():
            self.data0[self.index0.value] = 1000
            self.stop = True