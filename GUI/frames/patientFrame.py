from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import os
import sys

gui_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(gui_path)

from components.customButton import CustomButton
from components.patientTable import PatientTable
from frames.patientSelector import PatientSelector

class PatientFrame(QFrame):
    def __init__(self, light = True, enablePlayButton = None, disablePlayButton = None):
        """
        Requires:
            - light: a boolean indicating light or dark theme
            - enablePlayButton: a callback function that will be called to enable play button
            - disablePlayButton: a callback function that will be called to disable play button
        Modifies:
            - Initializes self attributes, table, and select patient button
        Effects:
            - Initializes a custom frame for patient selection.
        """
        super().__init__()

        # initialize attributes
        self.enablePlayButton = enablePlayButton
        self.disablePlayButton = disablePlayButton
        self.light = light

        # theme style
        self.lightTheme = "background-color: #B6C2CF; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;"
        self.darkTheme ="background-color: #282E33; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;"

        # layout
        layout_patient = QVBoxLayout(self)
        layout_patient.setContentsMargins(30, 30, 30, 30)
        self.setStyleSheet(self.lightTheme if light else self.darkTheme)

        # table
        self.table = PatientTable(reducedTable=True, light=light)
        layout_patient.addWidget(self.table)

        # spacer
        layout_patient.setSpacing(20)

        # button
        self.selectPatientButton = CustomButton(dimensions=[180, 40], text = "Select Patient", light = light)
        layout_patient.addWidget(self.selectPatientButton, alignment=Qt.AlignHCenter)
        self.selectPatientButton.onClick(self.selectPatient)

    def selectPatient(self):
        """
        Modifies:   self.table
        Effects:    Opens the modal window for patient selection.
                    Populates the patient table when a patient is selected.
                    It is called enablePlayButton
        """
        # every time it creates a new patient selector instance, we can improve it creating the instance one time 
        # and call them whenever we need
        patient_selector = PatientSelector(light = self.light)
        patient_selector.selectPatient()
        data = patient_selector.getSelectedPatientInfo()

        # update table
        self.table.setTableData(data)

        # enable play button
        self.enablePlayButton()

        # if data is empty, disable play button
        dataEmpty = True
        for _, dat in data:
            if dat.strip():
                dataEmpty = False
                break
        if dataEmpty: self.disablePlayButton()

    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
                        all custom elements
            Effects:    Switches between light and dark themes.
        """
        self.light = not self.light
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        self.table.toggleTheme()
        self.selectPatientButton.toggleTheme()
