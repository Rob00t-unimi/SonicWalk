from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
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

class AnalysisPage(QWidget):

    stopPlotterSignal = pyqtSignal()

    def __init__(self, light=True):
        super().__init__()
        self.light = light
        self.playButtonAbilited = False
        self.allEnabled = True
        self.shared_data = SharedData()
        self.setup_ui()

        self.stopPlotterSignal.connect(self.stop_plotter)

    def setup_ui(self):
        grid_layout = QGridLayout(self)
        self.selection_frame = ExerciseFrame(light=self.light)
        self.actions_frame = RecordingFrame(setBpm=self.selection_frame.setBpm, getBpm=self.selection_frame.getBpm,
                                            getMusicModality=self.selection_frame.getMusicModality, 
                                            getMusicPath=self.selection_frame.getMusicPath, 
                                            getExerciseNumber=self.selection_frame.getExerciseNumber, 
                                            getsensitivity=self.selection_frame.getsensitivity, 
                                            getSelectedLeg=self.selection_frame.getSelectedLeg, 
                                            light=self.light, 
                                            changeEnabledAll=self.changeEnabledAll, 
                                            shared_data=self.shared_data, 
                                            plotter_start=self.plotter_start, 
                                            setSaved=self.setSaved)
        self.patient_frame = PatientFrame(light=self.light, enablePlayButton=self.actions_frame.enablePlayButton, 
                                          disablePlayButton=self.actions_frame.disablePlayButton, 
                                          setPatientId=self.selection_frame.setPatientId)
        self.actions_frame.getPatient = self.patient_frame.getPatient
        self.plotter_frame = QWidget()
        self.layout_plotter = QVBoxLayout(self.plotter_frame)
        self.layout_plotter.setContentsMargins(0, 0, 0, 0)

        self.create_static_plotter()
        self.layout_plotter.addWidget(self.canvas)

        grid_layout.addWidget(self.patient_frame, 0, 0)
        grid_layout.addWidget(self.plotter_frame, 0, 1)
        grid_layout.addWidget(self.selection_frame, 1, 0)
        grid_layout.addWidget(self.actions_frame, 1, 1)

        grid_layout.addWidget(self.patient_frame, 0, 0, 1, 1)
        grid_layout.addWidget(self.selection_frame, 1, 0, 2, 1)
        grid_layout.addWidget(self.plotter_frame, 0, 1, 2, 3)
        grid_layout.addWidget(self.actions_frame, 2, 1, 1, 3)

        self.patient_frame.setMinimumWidth(200)
        self.plotter_frame.setMinimumWidth(200)
        self.selection_frame.setMinimumWidth(375)
        self.actions_frame.setMinimumWidth(375)

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
        if hasattr(self, 'timer'):
            self.timer.stop()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(40)    # 1000 / 40 = 25 fps

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
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        self.canvas = FigureCanvas(self.fig)
    
    def update_plot(self):
        """
        REQUIRES: 
            - data0 (np.ndarray): Array containing data of signal 0.
            - data1 (np.ndarray): Array containing data of signal 1.

        EFFECTS:    
            - Updates the dynamic plotter with new data.
        """
        data0 = np.array(self.shared_data.data0)
        data1 = np.array(self.shared_data.data1)

        # if 1000 in data0 or 1000 in data1: 
        #     self.setSaved(None)
        #     return

        self.ax.clear()
        self.ax.plot(data0, 'b', label = "Right Leg")
        self.ax.plot(data1, 'c', label = "Left Leg")
        self.ax.set_xticks([])
        self.ax.grid(True, color="#FFE6E6")
        self.ax.legend(loc='lower right')
        self.fig.patch.set_facecolor('none')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        self.canvas.draw()

    def setSaved(self, data):
        """
        REQUIRES: 
            - data (tuple or None): Tuple containing data for plots or None.

        EFFECTS:    
            - Sets the data in the plotter and updates it.
        """
        self.stopPlotterSignal.emit()
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        if data is not None:
            self.ax.plot(data[0], 'b', label = "Right Leg")
            self.ax.plot(data[1], 'c', label = "Left Leg")
            self.ax.legend(loc='lower right')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)
        self.canvas.draw()
        self.reset_shared_data()

    def stop_plotter(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        
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