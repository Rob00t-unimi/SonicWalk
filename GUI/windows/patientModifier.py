from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
import os
import json

class PatientModifier(QFrame):
    """
    Dialog window to modify the informations of the selected Patient to the dataset.JSON
    """
    def __init__(self, patient_data):
        """
        REQUIRES: 
            - patient_data must be valid map of patient datas

        MODIFIES: 
            - self

        EFFECTS:  
            - initialize the object and open the modal dialog window
        """
        super().__init__()

        folder_name = os.path.basename(os.getcwd())
        self.settings_path = 'data/settings.json' if folder_name == "GUI" else 'GUI/data/settings.json'
        self.dataset_path = 'data/dataset.json' if folder_name == "GUI" else 'GUI/data/dataset.json'

        self.patient_info_data = patient_data
        self.modify_patient_modal()
        
    def modify_patient_modal(self):
        """
        MODIFIES:   
            - self

        EFFECTS:    
            - opens the dialog window with all input fields for the selected Patient
        """
        # Create a modal window
        modal = QDialog()
        modal.setWindowTitle("Modify Patient")
        modal.setFixedWidth(650)
        layout = QVBoxLayout(modal)

        # Add hospital details section
        hospital_section = QGroupBox("Hospital Details")
        hospital_layout = QFormLayout()
        hospital_section.setLayout(hospital_layout)

        hospital_fields = [
            ("Hospital:", QLineEdit(self.patient_info_data["Hospital"])),  # ospedale
            ("Group:", QComboBox())       # ospedale
        ]
        
        # Populate comboboxes with options
        group_combobox = hospital_fields[1][1]
        group_combobox.addItems(["Parkinson", "ALS", "Healthy", "Stroke", "Other"])
        group_combobox.setCurrentText(self.patient_info_data["Group"])

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
        personal_fields = ["Name", "Surname", "Date of Birth", "CF", "Gender"]

        personal_table.horizontalHeader().setVisible(False)  # Hide default horizontal header

        for i, label in enumerate(personal_fields):
            personal_table.insertRow(i)
            personal_table.setVerticalHeaderItem(i, QTableWidgetItem(label))
            if i == 2:
                initial_date_string = self.patient_info_data["Date_of_Birth"]
                initial_date = QDate.fromString(initial_date_string, "yyyy-MM-dd")
                date_edit = QDateEdit() 
                date_edit.setDisplayFormat("yyyy-MM-dd")
                date_edit.setCalendarPopup(True)
                date_edit.setDate(initial_date)
                personal_table.setCellWidget(i, 0, date_edit)
            elif i != len(personal_fields) - 1:
                line_edit = QLineEdit()
                line_edit.setFixedHeight(21)
                line_edit.setAlignment(Qt.AlignVCenter)
                line_edit.setText(self.patient_info_data[label])
                personal_table.setCellWidget(i, 0, line_edit)
            else:
                gender_combo_box = QComboBox()
                gender_combo_box.addItems(["M", "F"])
                gender_combo_box.setCurrentText(self.patient_info_data[label])
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
        measurement_fields_original = ["Height", "Weight", "Right_Leg_Length", "Left_Leg_Length"]

        measurements_table.horizontalHeader().setVisible(False)  # Hide default horizontal header

        for i, label in enumerate(measurement_fields):
            measurements_table.insertRow(i)
            measurements_table.setVerticalHeaderItem(i, QTableWidgetItem(label))
            value = int((self.patient_info_data[measurement_fields_original[i]]).split()[0])
            spin_box = QSpinBox()
            spin_box.setMaximum(300)
            spin_box.setValue(value)
            measurements_table.setCellWidget(i, 0, spin_box)

        measurements_table.horizontalHeader().setStretchLastSection(True)
        measurements_table.verticalHeader().setMinimumWidth(200)
        measurements_layout.addWidget(measurements_table)
        layout.addWidget(measurements_section)

        # Add buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Confirm Modifies")
        add_button.clicked.connect(lambda: self.modify_patient({
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
            "ID": self.patient_info_data["ID"]
        }, modal.close))

        cancel_button = QPushButton("Close")
        cancel_button.clicked.connect(modal.close)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        modal.exec_()

    def modify_patient(self, patient_data, close_modal=None):
        """
        REQUIRES:   
            - patient_data (dictionary): must contain valid informations about the patient
            - close_modal (callable): function to close the modal (default None)

        MODIFIES:   
            - self

        EFFECTS:    
            - It sets the informations of the new Patient into the dataset.JSON 
            - it updates self.patient_info_data with some patient info and closes the modal
            - otherwise shows error in a QMessageBox
        """
        if patient_data["Name"] == "" or patient_data["Surname"] == "" or patient_data["Name"] is None or patient_data["Surname"] is None:
            QMessageBox.warning(self, "Error", "Please fill in all required fields (Name, Surname).")
            return

        json_path = os.path.join(os.getcwd(), self.dataset_path)
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error decoding patient database file.")
            return

        # Search the patient in the dataset
        for existing_patient in data:
            if existing_patient["ID"] == patient_data["ID"]:
                # Modify the patient datas
                existing_patient.update(patient_data)
                break

        try:
            with open(json_path, 'w') as file:
                json.dump(data, file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving patient data: {str(e)}")
            return
        
        self.patient_info_data = patient_data

        if close_modal is not None: 
            close_modal()

        QMessageBox.information(self, "Success", f"Patient {patient_data['Name']} {patient_data['Surname']} modified successfully.")

    def get_patient_data(self):
        """
        EFFECTS:    
            - Returns self.patient_info_data: a list containing patient information
        """
        return self.patient_info_data
