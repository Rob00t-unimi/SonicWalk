from PyQt5.QtWidgets import QFrame
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QTimer
import json
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QFont
from datetime import datetime, date

class PatientSelector(QFrame):
    
    def __init__(self):
        super().__init__()

        self.select_style = """
            QComboBox {
                border: 1px solid #B99AFF; /* Purple border */
                border-radius: 15px;
                padding: 10px;
                background-color: #FFFFFF;
                selection-background-color: #B99AFF;
                font-size: 15px;
                color: #4C4C4C;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-left-color: transparent;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                background-color: #B99AFF;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #B99AFF;
                selection-background-color: #9C6BE5;
                background-color: #FFFFFF;
                font-size: 14px;
                color: #4C4C4C;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 10px;
                margin: 20px 0 20px 0;
            }
            QScrollBar::handle:vertical {
                background: #DCDFE4;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                background: none;
            }
            QScrollBar::sub-line:vertical {
                background: none;
            }
        """

        self.patient_info_data = [
            ("Name:", ""),
            ("Surname:", ""),
            ("ID:", ""),
            ("Group:", ""),
            ("Hospital:", "")
        ]

    def selectPatient(self):
        # open dialog window
        dialog = QDialog()
        dialog.setWindowTitle("Select Patient")

        dialog.setStyleSheet("""
            background-color: #FFFFFF;
            color: #333333;
            font-size: 12pt;
        """)

        # read json dataset
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        # filters widgets
        hospitals = set(patient['Hospital'] for patient in patient_data)
        groups = set(patient['Group'] for patient in patient_data)
        sexes = {'M', 'F'}
        age_ranges = {'0-20', '21-40', '41-60', '61-80', '81+'}

        # filters options
        hospital_combo = QComboBox()
        hospital_combo.addItem("All hospitals")
        hospital_combo.addItems(sorted(hospitals))
        hospital_combo.setStyleSheet(self.select_style)

        group_combo = QComboBox()
        group_combo.addItem("All groups")
        group_combo.addItems(sorted(groups))
        group_combo.setStyleSheet(self.select_style)

        sex_combo = QComboBox()
        sex_combo.addItem("All")
        sex_combo.addItems(sorted(sexes))
        sex_combo.setStyleSheet(self.select_style)

        age_combo = QComboBox()
        age_combo.addItem("All Age")
        age_combo.addItems(sorted(age_ranges))
        age_combo.setStyleSheet(self.select_style)

        # search box
        search_lineedit = QLineEdit()
        search_lineedit.setPlaceholderText("Enter name, surname, ID or CF")
        search_lineedit.setStyleSheet("""
            background-color: #F5F5F5;
            border: 1px solid #DCDFE4;
            border-radius: 15px;
            padding: 5px;
            margin-top: 20px;
            margin-bottom: 20px;
        """)

        # filters layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Hospital:"))
        filter_layout.addWidget(hospital_combo)
        filter_layout.addWidget(QLabel("Group:"))
        filter_layout.addWidget(group_combo)
        filter_layout.addWidget(QLabel("Sex:"))
        filter_layout.addWidget(sex_combo)
        filter_layout.addWidget(QLabel("Age:"))
        filter_layout.addWidget(age_combo)

        # search box layout
        search_layout = QVBoxLayout()
        search_layout.addWidget(search_lineedit)
        search_layout.addLayout(filter_layout)

        # patient frame
        patient_frame = QFrame()
        patient_frame_layout = QVBoxLayout()
        patient_frame.setLayout(patient_frame_layout)

        # scrollable area with patient frame
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(patient_frame)

        scroll_bar_stylesheet = """
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 10px;
                margin: 20px 0 20px 0;
            }

            QScrollBar::handle:vertical {
                background: #DCDFE4;
                min-height: 30px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical {
                background: none;
            }

            QScrollBar::sub-line:vertical {
                background: none;
            }
        """
        scroll_area.setStyleSheet(scroll_bar_stylesheet)

        # calculate age
        def calculate_age(birth_date):
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age      

        # ages partitioning
        def age_in_range(age, age_range):
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
            return False  
        
        # patient list filtered
        def filter_patients():
            filtered_patients = []
            for patient in patient_data:
                sex = "M" if patient['Gender'] == "M" else "F"
                if (
                    hospital_combo.currentText() == "All hospitals"
                    or patient['Hospital'] == hospital_combo.currentText()
                ) and (
                    group_combo.currentText() == "All groups"
                    or patient['Group'] == group_combo.currentText()
                ) and (
                    sex_combo.currentText() == "All" or sex == sex_combo.currentText()
                ):
                    # Calcolo dell'età dal campo "Data di nascita"
                    birth_date = datetime.strptime(patient['Date_of_Birth'], "%Y-%m-%d")
                    age = calculate_age(birth_date)
                    if (
                        age_combo.currentText() == "All Age"
                        or age_in_range(age, age_combo.currentText())
                    ):
                        filtered_patients.append(patient)
            return filtered_patients
        
        # update search results by keyword search
        def update_search_results():
            search_text = search_lineedit.text().lower()
            noFound = True
            for button in buttons:
                button_text = button.layout().itemAt(0).widget().text() + button.layout().itemAt(1).widget().text()
                button_text = button_text.replace("ID:", "")
                button_text = button_text.replace("CF:", "")
                button_text = button_text.replace("(", "")
                button_text = button_text.replace(")", "")
                button_text = button_text.replace(",", "")
                button.setVisible(search_text in button_text.lower())
                if search_text in button_text.lower():
                    noFound = False

            # Rimuovi la label "No results found." se è già presente nel layout
            for i in reversed(range(patient_frame_layout.count())):
                widget = patient_frame_layout.itemAt(i).widget()
                if widget is not None and widget.text() == "No results found.":
                    widget.deleteLater()

            # Aggiungi la label "No results found." solo se non sono stati trovati risultati
            if noFound:
                no_results_label = QLabel("No results found.")
                patient_frame_layout.addWidget(no_results_label)

        # reload patient list
        def reload_buttons():
            nonlocal buttons
            filtered_patients = filter_patients()

            # delete previous buttons
            for button in buttons:
                button.deleteLater()
            for i in reversed(range(patient_frame_layout.count())):
                widget = patient_frame_layout.itemAt(i).widget()
                if widget is not None and widget.text() == "No results found.":
                    widget.deleteLater()

            buttons = []
            # create a button
            def create_patient_button(patient, dialog):
                button_layout = QHBoxLayout()

                button_label_1 = QLabel(f"<span style='color: black; text-align: center;'>{patient['Name']} {patient['Surname']}</span>")
                button_label_2 = QLabel(f"<span style='color: gray; text-align: center;'>ID: ({patient['ID']}),  CF: {patient['CF']}</span>")
                button_label_1.setStyleSheet("background-color: transparent;")
                button_label_2.setStyleSheet("background-color: transparent;")

                button_layout.addWidget(button_label_1)
                button_layout.addWidget(button_label_2)

                button = QPushButton()
                button.setLayout(button_layout)

                button.setStyleSheet("""
                    QPushButton {
                        border: none;
                        padding-left: 10px;
                        border-radius: 10px;
                        height: 60px;
                        background-color: rgba(108, 60, 229, 7%);
                    }
                    QPushButton:hover {
                        background-color: rgba(108, 60, 229, 30%);
                    }
                    QPushButton:checked {
                        background-color: rgba(108, 60, 229, 100%);
                    }                 
                """)
                button.clicked.connect(lambda _, patient=patient, dialog=dialog: self.loadPatientData(patient, dialog))

                def label_click_event(event):
                    button.click()

                button_label_1.mousePressEvent = label_click_event
                button_label_2.mousePressEvent = label_click_event

                patient_frame_layout.addWidget(button)
                buttons.append(button)

            for patient in filtered_patients:
                create_patient_button(patient, dialog)

            if len(filtered_patients) == 0:
                for i in reversed(range(patient_frame_layout.count())):
                    widget = patient_frame_layout.itemAt(i).widget()
                no_results_label = QLabel("No results found.")
                patient_frame_layout.addWidget(no_results_label)

        # when change a filter  reload and update
        def on_filter_changed():
            reload_buttons()
            update_search_results()

        # filter change actions
        hospital_combo.currentIndexChanged.connect(on_filter_changed)
        group_combo.currentIndexChanged.connect(on_filter_changed)
        sex_combo.currentIndexChanged.connect(on_filter_changed)
        age_combo.currentIndexChanged.connect(on_filter_changed)
        search_lineedit.textChanged.connect(update_search_results)

        # initial buttons
        buttons = []
        on_filter_changed()

        # dialog window layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(search_layout)
        main_layout.addWidget(scroll_area)
        dialog.setLayout(main_layout)

        dialog.exec_()


    def loadPatientData(self, patient, dialog):
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
            return self.patient_info_data

