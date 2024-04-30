from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

sys.path.append("../")

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
        self.data = None

        # layout
        layout_patient = QVBoxLayout(self)
        layout_patient.setContentsMargins(30, 30, 30, 30)

        # table
        self.table = PatientTable(reducedTable=True)
        layout_patient.addWidget(self.table)

        # spacer
        layout_patient.setSpacing(20)

        # button
        self.selectPatientButton = QPushButton("Select Patient")
        self.selectPatientButton.setProperty("class", "fill_button_inverted")
        layout_patient.addWidget(self.selectPatientButton, alignment=Qt.AlignHCenter)
        self.selectPatientButton.clicked.connect(self.selectPatient)

    def selectPatient(self):
        """
        Modifies:   self.table
        Effects:    Opens the modal window for patient selection.
                    Populates the patient table when a patient is selected.
                    It is called enablePlayButton
        """
        # every time it creates a new patient selector instance, we can improve it creating the instance one time 
        # and call them whenever we need
        patient_selector = PatientSelector()
        patient_selector.selectPatient()
        self.data = patient_selector.getSelectedPatientInfo()

        # update table
        self.table.setTableData(self.data)

        # enable play button
        self.enablePlayButton()

        # if data is empty, disable play button
        dataEmpty = True
        for _, dat in self.data:
            if dat.strip():
                dataEmpty = False
                break
        if dataEmpty: self.disablePlayButton()

    def getPatient(self):
        """
            Effects:    Rerurns selected patient Data
        """
        return self.data