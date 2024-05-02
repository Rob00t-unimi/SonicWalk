
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDir
import os
import json

import sys
sys.path.append("../")

class PatientAdder(QFrame):
    def __init__(self):
        super().__init__()

        self.patient_info_data = [
            ("Name:", ""),
            ("Surname:", ""),
            ("ID:", ""),
            ("Group:", ""),
            ("Hospital:", "")
        ]
        self.add_patient_modal()
        
    def add_patient_modal(self):

        # Create a modal window
        modal = QDialog()
        modal.setWindowTitle("Add New Patient")
        modal.setFixedWidth(650)
        layout = QVBoxLayout(modal)

        # Add hospital details section
        hospital_section = QGroupBox("Hospital Details")
        hospital_layout = QFormLayout()
        hospital_section.setLayout(hospital_layout)

        hospital_fields = [
            ("Hospital:", QLineEdit()),  # ospedale
            ("Group:", QComboBox())       # ospedale
        ]

        # Populate comboboxes with options
        group_combobox = hospital_fields[1][1]
        group_combobox.addItems(["Parkinson", "ALS", "Healthy", "Stroke", "Other"])

        for label, widget in hospital_fields:
            row = QHBoxLayout()
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Allineamento verticale per la label
            row.addWidget(label_widget)
            row.addWidget(widget)
            hospital_layout.addRow(row)

        layout.addWidget(hospital_section)

        # Add patient information section
        personal_section = QGroupBox("Patient Information")
        personal_section.setFixedHeight(265)
        personal_layout = QVBoxLayout()
        personal_section.setLayout(personal_layout)

        personal_table = QTableWidget()
        personal_table.setColumnCount(1)
        personal_fields = ["Name:", "Surname:", "Date of Birth:", "CF:", "Gender:"]

        personal_table.horizontalHeader().setVisible(False)  # Hide default horizontal header

        for i, label in enumerate(personal_fields):
            personal_table.insertRow(i)
            personal_table.setVerticalHeaderItem(i, QTableWidgetItem(label))
            if i == 2:
                date_edit = QDateEdit() 
                date_edit.setDisplayFormat("yyyy-MM-dd")
                date_edit.setCalendarPopup(True)
                personal_table.setCellWidget(i, 0, date_edit)
            elif i != len(personal_fields) - 1:
                line_edit = QLineEdit()
                line_edit.setFixedHeight(21)
                line_edit.setAlignment(Qt.AlignVCenter)
                personal_table.setCellWidget(i, 0, line_edit)
            else:
                gender_combo_box = QComboBox()
                gender_combo_box.addItems(["M", "F"])
                personal_table.setCellWidget(i, 0, gender_combo_box)
        
        personal_table.horizontalHeader().setStretchLastSection(True)
        personal_table.verticalHeader().setMinimumWidth(150)
        personal_layout.addWidget(personal_table)
        layout.addWidget(personal_section)

        # Add measurements section
        measurements_section = QGroupBox("Measurements")
        measurements_section.setFixedHeight(230)
        measurements_layout = QVBoxLayout()
        measurements_section.setLayout(measurements_layout)

        measurements_table = QTableWidget()
        measurements_table.setColumnCount(1)
        measurement_fields = ["Height (cm):", "Weight (kg):", "Right Leg Length (cm):", "Left Leg Length (cm):"]

        measurements_table.horizontalHeader().setVisible(False)  # Hide default horizontal header

        for i, label in enumerate(measurement_fields):
            measurements_table.insertRow(i)
            measurements_table.setVerticalHeaderItem(i, QTableWidgetItem(label))
            measurements_table.setCellWidget(i, 0, QSpinBox())  
            measurements_table.cellWidget(i,0).setMaximum(300)

        measurements_table.horizontalHeader().setStretchLastSection(True)
        measurements_table.verticalHeader().setMinimumWidth(200)
        measurements_layout.addWidget(measurements_table)
        layout.addWidget(measurements_section)

        # Add buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Patient")
        add_button.clicked.connect(lambda: self.add_patient({
            "Name": personal_table.cellWidget(0, 0).text(),
            "Surname": personal_table.cellWidget(1, 0).text(),
            "Date_of_Birth": personal_table.cellWidget(2, 0).date().toString("yyyy-MM-dd"),
            "CF": personal_table.cellWidget(3, 0).text(),
            "Gender": personal_table.cellWidget(4, 0).currentText(),
            "Hospital": hospital_fields[0][1].text(),
            "Group": hospital_fields[1][1].currentText(),
            "Height": str(measurements_table.cellWidget(0, 0).value()) + " cm",
            "Weight": str(measurements_table.cellWidget(1, 0).value()) + " kg",
            "Right_Leg_Length": str(measurements_table.cellWidget(2, 0).value()) + " cm",
            "Left_Leg_Length": str(measurements_table.cellWidget(3, 0).value()) + " cm",
        }, modal.close))

        cancel_button = QPushButton("Close")
        cancel_button.clicked.connect(modal.close)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        modal.exec_()

    def add_patient(self, patient_data, close_modal = None):

        if patient_data["Name"]=="" or patient_data["Surname"]=="" or patient_data["Name"] is None or patient_data["Surname"] is None:
            QMessageBox.warning(self, "Error", "Please fill in all required fields (Name, Surname).")
            return

        # Generate ID for the new patient
        json_path = os.path.join(os.getcwd(), "data", "dataset.json")
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error decoding patient database file.")
            return

        existing_ids = set(patient["ID"] for patient in data)
        new_id = 1
        while str(new_id).zfill(5) in existing_ids:
            new_id += 1
        new_id_str = str(new_id).zfill(5)

        patient_data["ID"] = new_id_str

        # Add the new patient to the existing JSON data
        data.append(patient_data)

        try:
            with open(json_path, 'w') as file:
                json.dump(data, file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving patient data: {str(e)}")
            return
        
        self.loadPatientData(patient_data)
        if close_modal is not None: close_modal()

        QMessageBox.information(self, "Success", f"Patient {patient_data['Name']} {patient_data['Surname']} added successfully.")

    def loadPatientData(self, patient):
        self.patient_info_data = [
            ("Name:", patient["Name"]),
            ("Surname:", patient["Surname"]),
            ("ID:", patient["ID"]),
            ("Group:", patient["Group"]),
            ("Hospital:", patient["Hospital"])
        ]

    def getSelectedPatientInfo(self):
        """
        Effects:    Returns self.patient_info_data: a list containing patient information
        """
        return self.patient_info_data