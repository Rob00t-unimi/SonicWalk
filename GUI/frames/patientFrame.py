from PyQt5.QtWidgets import *
from GUI.components.patientTable import PatientTable
from GUI.windows.patientSelector import PatientSelector
from GUI.windows.patientAdder import PatientAdder

class PatientFrame(QFrame):
    """
    Custom frame for patient visualization, selection and adding.
    """
    def __init__(self, light = True, enablePlayButton = None, disablePlayButton = None, setPatientId = None):
        """
        REQUIRES:
            - light (bool): a boolean indicating light or dark theme
            - enablePlayButton (callable): a callback function that will be called to enable play button
            - disablePlayButton (callable): a callback function that will be called to disable play button

        MODIFIES:
            - self

        EFFECTS:
            - Initializes a custom frame for patient.
        """
        super().__init__()

        self.reload_archive_patient_list = None

        # initialize attributes
        self.enablePlayButton = enablePlayButton
        self.disablePlayButton = disablePlayButton
        self.light = light
        self.data = None
        self.setPatientId = setPatientId

        # layout
        layout_patient = QVBoxLayout(self)
        layout_patient.setContentsMargins(30, 30, 30, 30)

        # table
        self.table = PatientTable(reducedTable=True)
        layout_patient.addWidget(self.table)

        # spacer
        layout_patient.setSpacing(20)

        # buttons box
        button_box = QWidget()
        button_box_layout = QHBoxLayout(button_box)
        layout_patient.addWidget(button_box)

        # button
        self.selectPatientButton = QPushButton("Select Patient")
        self.selectPatientButton.setProperty("class", "fill_button_inverted")
        button_box_layout.addWidget(self.selectPatientButton)
        self.selectPatientButton.clicked.connect(self.selectPatient)

        self.addPatientButton = QPushButton("Add New Patient")
        self.addPatientButton.setProperty("class", "fill_button_inverted")
        button_box_layout.addWidget(self.addPatientButton)
        self.addPatientButton.clicked.connect(self.addPatient)

    def addPatient(self):
        """
        MODIFIES:   
            - self.table

        EFFECTS:    
            - Opens the modal window for adding new patient.
            - Populates the patient table when a patient is selected.
            - It is enabled the play button (for recording)
        """
        patient_adder = PatientAdder()
        self.data = patient_adder.getSelectedPatientInfo()
        if self.data[2][1] != "" and self.data[2][1] is not None:   # id not void -- > patient added
            if self.reload_archive_patient_list is not None: self.reload_archive_patient_list()
        self.updateInfo()

    def selectPatient(self):
        """
        MODIFIES:   
            - self.table

        EFFECTS:    
            - Opens the modal window for patient selection.
            - Populates the patient table when a patient is selected.
            - It is enabled the play button (for recording)
        """
        # every time it creates a new patient selector instance, we can improve it creating the instance one time 
        # and call them whenever we need
        patient_selector = PatientSelector()
        patient_selector.selectPatient()
        self.data = patient_selector.getSelectedPatientInfo()

        self.updateInfo()

    def updateInfo(self):
        """
        MODIFIES:
            - self

        EFFECTS:
            - Populates the patient table
            - It is enabled the play button (for recording)
        """
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
        if dataEmpty: 
            self.disablePlayButton()
            self.setPatientId(None)
        else: self.setPatientId(self.data[2][1]) # set patient id in exercise frame        

    def getPatient(self):
        """
        EFFECTS:    
            - Rerurns selected patient Data
        """
        return self.data