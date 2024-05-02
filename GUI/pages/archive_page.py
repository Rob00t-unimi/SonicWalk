from datetime import datetime, date
import json
import os
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot  as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

import sys
sys.path.append("../")

class ArchivePage(QWidget):
    def __init__(self, light = True, icons_manager = None, parent=None):
        super().__init__(parent)

        self.light = light
        self.icons_manager = icons_manager

        # principal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create left box   ------------------------------------------------------------------------------
        left_box = QWidget()
        left_box.setFixedWidth(400)

        # create left layout
        left_layout = QVBoxLayout()
        # left_layout.setContentsMargins(5, 0, 5, 0)
        left_box.setLayout(left_layout)
        layout.addWidget(left_box)

        # create research box
        research_box = QFrame()
        research_box.setFixedHeight(240)
        left_layout.addWidget(research_box)
        left_layout.setAlignment(Qt.AlignTop)
        research_box.setContentsMargins(0, 20, 0, 0)

        # create research box layout
        research_box_layout = QVBoxLayout()
        research_box.setLayout(research_box_layout)

        select_patient_label = QLabel("Select Patient")
        research_box_layout.addWidget(select_patient_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        select_patient_label.setStyleSheet("""font-size: 20px""")

        search_and_toggle_layout = QHBoxLayout()

        # add search box
        search_lineedit = QLineEdit()
        search_lineedit.setFixedWidth(300)
        search_lineedit.setFixedHeight(80)
        search_lineedit.setPlaceholderText("Enter name, surname, ID or CF")
        search_and_toggle_layout.addWidget(search_lineedit, alignment=Qt.AlignCenter)
        self.current_search_text = ""
        search_lineedit.textChanged.connect(lambda text: update_text(text))
        def update_text(text):
            self.current_search_text = text
            self.updatesearchresults()

        # filters
        toggle_filter_button = QPushButton()
        toggle_filter_button.setProperty("icon_name", "minus_circle")
        toggle_filter_button.setFixedHeight(35)
        toggle_filter_button.setFixedWidth(35)
        toggle_filter_button.setStyleSheet("""border: None;""")
        search_and_toggle_layout.addWidget(toggle_filter_button)

        def toggleFilterBox():
            if research_box.height() == 175:
                research_box.setFixedHeight(240)
                toggle_filter_button.setProperty("icon_name", "minus_circle")
                toggle_filter_button.setIcon(icons_manager.getIcon("minus_circle"))
                filter_box.setVisible(True)
            else:
                research_box.setFixedHeight(175)
                toggle_filter_button.setProperty("icon_name", "plus_circle")
                toggle_filter_button.setIcon(icons_manager.getIcon("plus_circle"))
                filter_box.setVisible(False)

        # Collega il pulsante alla funzione di gestione
        toggle_filter_button.clicked.connect(toggleFilterBox)

        research_box_layout.addLayout(search_and_toggle_layout)

        # read json dataset
        with open('data/dataset.json', 'r') as file:
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

        filter_box = QWidget()
        filter_box.setMinimumWidth(300)
        filter_layout = QGridLayout()
        filter_layout.addWidget(hospital_combo, 0, 1)
        filter_layout.addWidget(group_combo, 1, 1)
        filter_layout.addWidget(sex_combo, 0, 2)
        filter_layout.addWidget(age_combo, 1, 2)
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        filter_box.setLayout(filter_layout)
        research_box_layout.addWidget(filter_box, alignment=Qt.AlignLeft)

        # Leggiamo il dataset JSON
        self.patients_list = QListWidget()
        self.patients_list.setProperty("class", "archive_list")
        left_layout.addWidget(self.patients_list)
        self.load_patients_from_json()

        # create Central box ------------------------------------------------------------------------------------
        central_box = QWidget()
        central_box.setMinimumWidth(650)

        # create Central layout
        central_layout = QVBoxLayout()
        # central_layout.setContentsMargins(0, 0, 0, 0)
        central_box.setLayout(central_layout)
        layout.addWidget(central_box)

        # create Central top
        central_top_box = QWidget()
        central_top_box.setMinimumHeight(400)
        central_top_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # create Central top layout
        self.central_top_layout = QVBoxLayout()

        self.central_top_layout.setContentsMargins(0, 0, 0, 0)
        central_top_box.setLayout(self.central_top_layout)
        central_layout.addWidget(central_top_box)

        central_bottom_box = QWidget()
        central_bottom_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central_bottom_box.setMaximumHeight(250)

        # create Central bottom layout
        central_bottom_layout = QHBoxLayout()
        central_bottom_layout.setContentsMargins(0, 0, 0, 0)
        central_bottom_box.setLayout(central_bottom_layout)
        central_layout.addWidget(central_bottom_box)

        # create Matplotlib plot
        self.fig, self.ax = plt.subplots()
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        # self.fig.tight_layout()

        # create a canvas for the plot
        self.canvas = FigureCanvas(self.fig)

        # add the canvas to the layout
        self.central_top_layout.addWidget(self.canvas)


        # Creazione delle liste e dei loro modelli
        self.listView_folders = QListView()
        self.listView_files = QListView()

        # Creazione delle etichette per i titoli
        label_folders = QLabel("Folders")
        label_files = QLabel("Files")

        # Aggiunta di un padding sinistro alle etichette
        label_folders.setStyleSheet("padding-left: 5px;")
        label_files.setStyleSheet("padding-left: 5px;")

        # Creazione dei layout per ciascuna coppia di lista e titolo
        layout_folders = QVBoxLayout()
        layout_files = QVBoxLayout()

        # Aggiunta della lista e del titolo al layout
        layout_folders.addWidget(label_folders)
        layout_folders.addWidget(self.listView_folders)
        layout_files.addWidget(label_files)
        layout_files.addWidget(self.listView_files)

        # Creazione dei widget di gruppo per ciascuna coppia di lista e titolo
        group_box_folders = QWidget()
        group_box_folders.setLayout(layout_folders)
        group_box_files = QWidget()
        group_box_files.setLayout(layout_files)

        # Rimozione del padding dai QGroupBox
        layout_folders.setContentsMargins(0, 0, 0, 0)
        layout_files.setContentsMargins(0, 0, 0, 0)

        # Aggiunta dei widget di gruppo al layout principale
        central_bottom_layout.addWidget(group_box_folders)
        central_bottom_layout.addWidget(group_box_files)

        self.listView_folders.setProperty("class", "archive_list")
        self.listView_files.setProperty("class", "archive_list")
        self.listView_files.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.folder_model = QFileSystemModel() 
        self.folder_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.folder_model.directoryLoaded.connect(self.on_folder_loaded) 

        self.listView_folders.clicked.connect(self.folder_clicked)

        # Modello per i file
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(["*.npy"])

        self.listView_files.clicked.connect(self.load_selected_file)

        self.navigation_toolbar = None

        # Creazione del menu contestuale per le cartelle
        self.folder_context_menu = QMenu(self)
        delete_folder_action = self.folder_context_menu.addAction("Delete")
        delete_folder_action.triggered.connect(self.delete_selected_folder)

        # Collegamento del menu contestuale alla lista delle cartelle
        self.listView_folders.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_folders.customContextMenuRequested.connect(self.show_folder_context_menu)

        # Creazione del menu contestuale per i file
        self.file_context_menu = QMenu(self)
        delete_file_action = self.file_context_menu.addAction("Delete")
        delete_file_action.triggered.connect(self.delete_selected_file)

        # Collegamento del menu contestuale alla lista dei file
        self.listView_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_files.customContextMenuRequested.connect(self.show_file_context_menu)
        # Collegamento del menu contestuale alla lista dei file
        self.listView_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_files.customContextMenuRequested.connect(self.show_file_context_menu)

        # right box ---------------------------------------------------------------------------------------------------
        right_box = QWidget()
        right_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_box.setMaximumWidth(375)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_box.setLayout(right_layout)
        layout.addWidget(right_box)

        # create an add patient button
        add_patient_button = QPushButton("Add new patient")
        add_patient_button.setProperty("class", "fill_button_inverted")
        right_layout.addWidget(add_patient_button, alignment=Qt.AlignTop | Qt.AlignHCenter)
        add_patient_button.clicked.connect(self.add_patient_modal)

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
        
        if close_modal is not None: close_modal()

        # Update the patient list in the UI
        self.patients_list.clear()
        self.load_patients_from_json()
        self.updatesearchresults()

        QMessageBox.information(self, "Success", f"Patient {patient_data['Name']} {patient_data['Surname']} added successfully.")

    def delete_patient(self, patient_id):
        json_path = os.path.join(os.getcwd(), "data", "dataset.json")
        
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Patient database file not found.")
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error decoding patient database file.")
            return

        confirmation = QMessageBox.warning(self, "Confirm Deletion", "Are you sure you want to delete this patient?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        try:
            # Remove the patient from the data list
            for patient in data:
                if patient["ID"] == patient_id:
                    data.remove(patient)
                    break

            # Write the updated data back to the JSON file
            with open(json_path, 'w') as file:
                json.dump(data, file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the patient: {str(e)}")
            return

        for i in range(self.patients_list.count()):
            item = self.patients_list.item(i)
            if item.data(Qt.UserRole)["ID"] == patient_id:
                self.patients_list.takeItem(i)
                break

        patient_folder = os.path.join(os.getcwd(), "data", "archive", patient_id.upper())
        try:
            shutil.rmtree(patient_folder)
        except FileNotFoundError:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the patient folder: {str(e)}")


    def show_folder_context_menu(self, position):
        index = self.listView_folders.indexAt(position)
        if index.isValid():
            self.folder_context_menu.exec_(self.listView_folders.mapToGlobal(position))

    def show_file_context_menu(self, position):
        index = self.listView_files.indexAt(position)
        if index.isValid():
            self.file_context_menu.exec_(self.listView_files.mapToGlobal(position))

    def delete_selected_folder(self):
        selected_indexes = self.listView_folders.selectedIndexes()
        if selected_indexes:
            reply = QMessageBox.warning(self, 'Deleting Folder', 
                                         "Are you sure you want to delete the selected folder?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for index in selected_indexes:
                    folder_path = self.folder_model.filePath(index)
                    try:
                        shutil.rmtree(folder_path)
                    except Exception as e:
                        QMessageBox.warning(self, 'Error', 
                                            f"Error while deleting folder '{folder_path}': {e}",
                                            QMessageBox.Ok, QMessageBox.Ok)

    def delete_selected_file(self):
        selected_indexes = self.listView_files.selectedIndexes()
        if selected_indexes:
            reply = QMessageBox.warning(self, 'Deleting File', 
                                         "Are you sure you want to delete the selected file?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for index in selected_indexes:
                    file_path = self.file_model.filePath(index)
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        QMessageBox.warning(self, 'Error', 
                                            f"Error while deleting file '{file_path}': {e}",
                                            QMessageBox.Ok, QMessageBox.Ok)

                    
    def on_folder_loaded(self):
        self.listView_folders.setRootIndex(self.folder_model.index(self.folder_path))

    def folder_clicked(self, index):
        self.listView_files.setModel(self.file_model)
        folder_path = self.folder_model.fileInfo(index).absoluteFilePath()
        self.file_model.setRootPath(folder_path)
        self.listView_files.setRootIndex(self.file_model.index(folder_path))

    def load_selected_file(self, index):
        file_path = self.file_model.fileInfo(index).absoluteFilePath()
        try:
            loaded_data = np.load(file_path, allow_pickle=True)
            signals = loaded_data.item().get("signals")
            Fs = loaded_data.item().get("Fs")
            time = np.arange(len(signals[0])) / Fs
            self.ax.clear()
            colors = ["b", "c"]
            i = 0
            for signal in signals:
                self.ax.plot(time, signal, color=colors[i])  
                i += 1
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Angle (Deg)')
            self.ax.grid(True, color="#FFE6E6")

            self.canvas.draw()
            if self.navigation_toolbar is None: self.navigation_toolbar = NavigationToolbar(self.canvas, self)
            else: self.navigation_toolbar.setVisible(True)
            self.central_top_layout.addWidget(self.navigation_toolbar)

        except Exception as e:
            QMessageBox.warning(None, "Errore", f"Impossibile caricare il file: {str(e)}")

    def load_patients_from_json(self):
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        self.selected_items = [False] * len(patient_data)
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

        self.patients_list.itemClicked.connect(self.clicked_patient)


    def clicked_patient(self, item):
        index = self.patients_list.row(item)

        if not self.selected_items[index]:
            self.select_patient_folder(item)
        else:
            self.listView_folders.setModel(None)
            self.reset()
            item.setSelected(False)
        for i, _ in enumerate(self.selected_items):
            if i == index: self.selected_items[i] = not self.selected_items[i]
            else: self.selected_items[i] = False

    def updatesearchresults(self):
        search_text = self.current_search_text.lower()
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        for i in range(self.patients_list.count()):
            item = self.patients_list.item(i)
            item.setHidden(True)

        def age_in_range(date_of_birth_str, age_range):
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
                        item.setHidden(False)

    def updatefilters(self, type, text):
        if type == text: 
            self.filters[type] = None
        else:
            self.filters[type] = text
        self.updatesearchresults()

    def select_patient_folder(self, item):

        patient = item.data(Qt.UserRole)
        patient_id = (patient['ID']).upper()
        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "data", "archive", patient_id)
        if os.path.exists(self.folder_path):
            self.folder_model.setRootPath(self.folder_path) 
            self.listView_folders.setModel(self.folder_model)
            self.listView_folders.setRootIndex(self.folder_model.index(self.folder_path))
        else: self.listView_folders.setModel(None)
        self.listView_folders.clearSelection()
        self.reset()

    def reset(self):
        if self.navigation_toolbar is not None: self.navigation_toolbar.setVisible(False)
        self.ax.clear()
        self.ax.grid(True, color="#FFE6E6")
        self.canvas.draw()
        self.listView_files.setModel(None)
        self.listView_files.clearSelection()

    def show_context_menu(self, position):
        self.context_menu.exec_(self.sender().mapToGlobal(position))