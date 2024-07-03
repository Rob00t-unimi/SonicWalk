from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
from datetime import datetime, date
import os

class PatientSelector(QFrame):
    """
    Dialog window to select a Patient from dataset.JSON
    """
    def __init__(self):
        """
        Modifies: 
            - self

        Effects:  
            - initialize the object and open the modal dialog window
        """
        super().__init__()
        self.settings_path = 'GUI/data/settings.json'
        self.dataset_path = 'GUI/data/dataset.json'

        self.patient_info_data = [
            ("Name:", ""),
            ("Surname:", ""),
            ("ID:", ""),
            ("Group:", ""),
            ("Hospital:", "")
        ]

    def selectPatient(self):
        """
        MODIFIES:   
            - self

        EFFECTS:    
            - Opens a dialog window to select a patient.
            - Filters patients based on hospital, group, sex, and age.
            - Updates search results based on keyword search.
            - Reloads and updates patient list when filters are changed.
        """
        # open dialog window
        self.dialog = QDialog()
        self.dialog.setFixedSize(600, 494)
        self.dialog.setWindowTitle("Select Patient")
        self.dialog.setWindowIcon(QIcon('GUI/icons/SonicWalk_logo.png'))

        self.no_results_label = QLabel("No results found", self.dialog)
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setMinimumSize(200, 40)
        self.no_results_label.move(200, 250)

        # read json dataset
        with open(self.dataset_path, 'r') as file:
            patient_data = json.load(file)

        # filters widgets
        hospitals = set(patient['Hospital'] for patient in patient_data)
        groups = set(patient['Group'] for patient in patient_data)
        sexes = {'M', 'F'}
        age_ranges = {'0-20', '21-40', '41-60', '61-80', '81+'}

        self.filters = {
            "Hospitals": None,
            "Groups": None,
            "Genders": None,
            "Ages": None
        }

        # initialize selects for filters
        hospital_combo = QComboBox()
        hospital_combo.addItems(["Hospitals"] + sorted(hospitals))

        group_combo = QComboBox()
        group_combo.addItems(["Groups"] + sorted(groups))

        sex_combo = QComboBox()
        sex_combo.addItems(["Genders"] + sorted(sexes))

        age_combo = QComboBox()
        age_combo.addItems(["Ages"] + sorted(age_ranges))

        hospital_combo.currentIndexChanged.connect(lambda index: self.updatefilters("Hospitals", hospital_combo.currentText()))
        group_combo.currentIndexChanged.connect(lambda index: self.updatefilters("Groups", group_combo.currentText()))
        sex_combo.currentIndexChanged.connect(lambda index: self.updatefilters("Genders", sex_combo.currentText()))
        age_combo.currentIndexChanged.connect(lambda index: self.updatefilters("Ages", age_combo.currentText()))

        # search box
        search_lineedit = QLineEdit()
        search_lineedit.setPlaceholderText("Enter name, surname, ID or CF")
        self.current_search_text = ""
        search_lineedit.textChanged.connect(lambda text: update_text(text))
        def update_text(text):
            self.current_search_text = text
            self.updatesearchresults()

        # filters layout
        filter_layout = QHBoxLayout()
        # filter_layout.addWidget(QLabel("Hospital:"))
        filter_layout.addWidget(hospital_combo)
        # filter_layout.addWidget(QLabel("Group:"))
        filter_layout.addWidget(group_combo)
        # filter_layout.addWidget(QLabel("Sex:"))
        filter_layout.addWidget(sex_combo)
        # filter_layout.addWidget(QLabel("Age:"))
        filter_layout.addWidget(age_combo)

        # search box layout
        search_layout = QVBoxLayout()
        search_layout.addWidget(search_lineedit)
        search_layout.addLayout(filter_layout)

        # patient frame
        patient_frame = QFrame()
        patient_frame_layout = QVBoxLayout()
        patient_frame_layout.setAlignment(Qt.AlignTop)
        patient_frame.setLayout(patient_frame_layout)

        # patients list
        self.patients_list = QListWidget()
        self.patients_list.setProperty("class", "archive_list")
        patient_frame_layout.addWidget(self.patients_list)
        self.load_patients_from_json()

        # dialog window layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.patients_list)
        self.dialog.setLayout(main_layout)

        self.dialog.exec_()

    def load_patients_from_json(self):
        """
        MODIFIES: 
            - self

        EFFECTS:  
            - loads the patients from dataset.JSON and sets up the list of patients
        """
        with open(self.dataset_path, 'r') as file:
            patient_data = json.load(file)

        # if there are no patients show the label "no results found"
        if not patient_data:
            self.no_results_label.raise_()  # on top
            self.no_results_label.show()
            return
        self.no_results_label.hide()

        patient_data = sorted(patient_data, key=lambda x: (x['Name'], x['Surname']))    # sort data in alphabetic order by name and surname
        self.selected_items = [False] * len(patient_data)
        # sets up the list
        for patient in patient_data:

            patientview = QWidget()
            patientview.setContentsMargins(0,0,0,0)
            patientview.setStyleSheet("background-color: transparent;")
            patientview_layout = QHBoxLayout()
            patientview_label_1 = QLabel(f"<span style='text-align: center;'>{patient['Name']} {patient['Surname']}</span>")
            patientview_label_1.setContentsMargins(0,0,0,0)
            patientview_label_2 = QLabel(f"<span style='color: gray; text-align: center;'>ID: ({patient['ID']})</span>")
            patientview_label_2.setContentsMargins(0,0,0,0)
            patientview_label_1.setStyleSheet("background-color: transparent;")
            patientview_label_2.setStyleSheet("background-color: transparent;")
            patientview_layout.addWidget(patientview_label_1)
            patientview_layout.addWidget(patientview_label_2)
            patientview.setLayout(patientview_layout)
            patientview.setMinimumHeight(40)
            
            item = QListWidgetItem()
            item.setData(Qt.UserRole, patient)
            item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            patientview.setDisabled(True)

            self.patients_list.addItem(item)
            self.patients_list.setItemWidget(item, patientview)

        self.patients_list.itemClicked.connect(self.handle_patient_click)

    def handle_patient_click(self, item):
        """
        REQUIRES: 
            - item (QListWidgetItem): must be a valid item of the patients list

        MOFIFIES: 
            - self

        EFFECTS:  
            - extract the data of the patient from the item and calls self.loadPatientData
        """
        patient = item.data(Qt.UserRole)
        self.loadPatientData(patient, self.dialog)

    def loadPatientData(self, patient, dialog):
        """
        REQUIRES:   
            - patient: a dictionary containing patient information
            - dialog:  the dialog window object

        MODIFIES:   
            - self.patient_info_data

        EFFETCS:    
            - Updates self.patient_info_data with some patient information
            - Loads selected patient data and closes the dialog window
            - Closes the dialog window
        """
        # Load selected patient data
        self.patient_info_data = [
            ("Name:", patient["Name"]),
            ("Surname:", patient["Surname"]),
            ("ID:", patient["ID"]),
            ("Group:", patient["Group"]),
            ("Hospital:", patient["Hospital"])
        ]
        dialog.accept()

    def getSelectedPatientInfo(self):
        """
        EFFECTS:    
            - Returns self.patient_info_data: a list containing patient information
        """
        return self.patient_info_data

    def updatesearchresults(self):
        """
        MODIFIES: 
            - self

        EFFECTS:  
            - Updates the list of patients based on the entered search text and selected filters.
        """
        search_text = self.current_search_text.lower()
        # load json
        with open(self.dataset_path, 'r') as file:
            patient_data = json.load(file)

        # hide all items
        for i in range(self.patients_list.count()):
            item = self.patients_list.item(i)
            item.setHidden(True)

        # sets up the age ranges
        def age_in_range(date_of_birth_str, age_range):
            """
            calculates ages of patients and returns patients in the selected age range
            """
            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age_range == "0-20":
                return 0 <= age <= 20
            elif age_range == "21-40":
                return 21 <= age <= 40
            elif age_range == "41-60":
                return 41 <= age <= 60
            elif age_range == "61-80":
                return 61 <= age <= 80
            elif age_range == "81+":
                return age >= 81
            else:
                return False

        # filtering
        no_results = True
        for patient in patient_data:
            if (
                (not self.filters["Hospitals"] or patient['Hospital'] == self.filters["Hospitals"]) and
                (not self.filters["Groups"] or patient['Group'] == self.filters["Groups"]) and
                (not self.filters["Genders"] or patient['Gender'] == self.filters["Genders"]) and
                (not self.filters["Ages"] or age_in_range(patient['Date_of_Birth'], self.filters["Ages"]))
            ):
                for i in range(self.patients_list.count()):
                    item = self.patients_list.item(i)
                    data = item.data(Qt.UserRole)
                    if patient['ID'] == data["ID"] and (search_text == "" or search_text.lower() in data["ID"].lower() or search_text.lower() in data["CF"].lower() or search_text.lower() in data["Name"].lower() or search_text.lower() in data["Surname"].lower()):
                        item.setHidden(False)   # show the item
                        no_results = False

        # if there are no patients show the label "no results found"
        if no_results:
            self.no_results_label.raise_()  # on top
            self.no_results_label.show()
        else:
            self.no_results_label.hide()

    def updatefilters(self, type, text):
        """
        MODIFIES: 
            - self

        EFFETCS:  
            - updates the selected filters and updates the search results by calling self.updatesearchresults
        """
        if type == text: 
            self.filters[type] = None
        else:
            self.filters[type] = text
        self.updatesearchresults()