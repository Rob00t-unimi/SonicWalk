from datetime import datetime, date
import json
import os
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDir
import matplotlib.pyplot  as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from windows.patientModifier import PatientModifier

class ArchivePage(QWidget):
    """
    Page for managing the archive. It Allows to visualize, modify, and delete patients informations and recorded signals.
    """
    def __init__(self, light = True, icons_manager = None):
        """
        REQUIRES: 
            - light (bool): indicating whether the theme is light or dark.
            - icons_manager (IconsManager): icons manager instance

        MODIFIES: 
            - self
        
        EFFECTS: 
            Initializes and show the Archive page interface
        """
        super().__init__()

        self.folder_name = os.path.basename(os.getcwd())
        self.settings_path = 'data/settings.json' if self.folder_name == "GUI" else 'GUI/data/settings.json'
        self.dataset_path = 'data/dataset.json' if self.folder_name == "GUI" else 'GUI/data/dataset.json'

        self.light = light
        self.icons_manager = icons_manager

        # principal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.no_results_label = QLabel("No results found", self)
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setMinimumSize(200, 40)
        self.no_results_label.move(95, 350)

        # create left box   ------------------------------------------------------------------------------
        left_box = QWidget()
        left_box.setFixedWidth(400)

        # create left layout
        self.left_layout = QVBoxLayout()
        left_box.setLayout(self.left_layout)
        layout.addWidget(left_box)

        # create research box
        research_box = QFrame()
        research_box.setFixedHeight(240)
        self.left_layout.addWidget(research_box)
        self.left_layout.setAlignment(Qt.AlignTop)
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
            """
            switch minus circle and plus circle, switch box dimensions, switch visibility of elements
            """
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

        toggle_filter_button.clicked.connect(toggleFilterBox)

        research_box_layout.addLayout(search_and_toggle_layout)

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

        # Read dataset.JSON
        self.patients_list = QListWidget()
        self.patients_list.setProperty("class", "archive_list")
        self.left_layout.addWidget(self.patients_list)
        self.load_patients_from_json()

        # create Central box ------------------------------------------------------------------------------------
        central_box = QWidget()
        central_box.setMinimumWidth(650)

        # create Central layout
        central_layout = QVBoxLayout()
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

        # Create lists
        self.listView_folders = QListView()
        self.listView_files = QListView()

        # labels
        label_folders = QLabel("Folders")
        label_files = QLabel("Files")

        label_folders.setStyleSheet("padding-left: 5px;")
        label_files.setStyleSheet("padding-left: 5px;")

        layout_folders = QVBoxLayout()
        layout_files = QVBoxLayout()

        layout_folders.addWidget(label_folders)
        layout_folders.addWidget(self.listView_folders)
        layout_files.addWidget(label_files)
        layout_files.addWidget(self.listView_files)

        group_box_folders = QWidget()
        group_box_folders.setLayout(layout_folders)
        group_box_files = QWidget()
        group_box_files.setLayout(layout_files)

        layout_folders.setContentsMargins(0, 0, 0, 0)
        layout_files.setContentsMargins(0, 0, 0, 0)

        central_bottom_layout.addWidget(group_box_folders)
        central_bottom_layout.addWidget(group_box_files)

        self.listView_folders.setProperty("class", "archive_list")
        self.listView_files.setProperty("class", "archive_list")
        self.listView_files.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.folder_model = QFileSystemModel() 
        self.folder_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.folder_model.directoryLoaded.connect(self.on_folder_loaded) 

        self.listView_folders.clicked.connect(self.folder_clicked)

        # File model
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(["*.npy"])

        self.listView_files.clicked.connect(self.load_selected_file)

        self.navigation_toolbar = None

        # Folders context menu
        self.folder_context_menu = QMenu(self)
        delete_folder_action = self.folder_context_menu.addAction("Delete")
        delete_folder_action.triggered.connect(self.delete_selected_folder)

        # connect context menu to the folders list
        self.listView_folders.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_folders.customContextMenuRequested.connect(self.show_folder_context_menu)

        # Files context menu
        self.file_context_menu = QMenu(self)
        delete_file_action = self.file_context_menu.addAction("Delete")
        delete_file_action.triggered.connect(self.delete_selected_file)

        # connect context menu to the files list
        self.listView_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_files.customContextMenuRequested.connect(self.show_file_context_menu)
        
        # right box ---------------------------------------------------------------------------------------------------
        self.right_box = QWidget()
        self.right_box.setMaximumWidth(400)
        self.right_box.setMinimumWidth(0)
        right_layout = QVBoxLayout()
        self.right_box.setLayout(right_layout)
        layout.addWidget(self.right_box)

        patient_box = QFrame()
        patient_layout = QVBoxLayout()
        patient_box.setLayout(patient_layout)
        right_layout.addWidget(patient_box)

        patient_box_title = QLabel("Patient Informations")
        patient_box_title.setContentsMargins(0, 20, 0, 20)
        patient_layout.addWidget(patient_box_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        patient_box_title.setStyleSheet("""font-size: 20px""")  

        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidgetResizable(True)  
        scroll_area_widget = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_widget)

        # table 1
        self.table1 = QTableWidget()
        self.table1.setRowCount(5)
        self.table1.setColumnCount(1)
        self.table1.verticalHeader().setMinimumWidth(150)
        self.table1.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        vertical_headers_table1 = ["Name", "Surname", "Date of Birth", "CF", "Gender"]
        self.table1.setVerticalHeaderLabels(vertical_headers_table1)
        self.table1.horizontalHeader().setVisible(False)
        self.table1.setFixedHeight(self.table1.rowCount() * self.table1.rowHeight(0) + 2)
        self.table1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        scroll_area_layout.addWidget(self.table1)

        # spacer
        spacer1 = QLabel("Medical Informations")
        spacer1.setContentsMargins(0, 20, 0, 20)
        scroll_area_layout.addWidget(spacer1)

        # table 2
        self.table2 = QTableWidget()
        self.table2.setRowCount(2)
        self.table2.setColumnCount(1)
        self.table2.verticalHeader().setMinimumWidth(150)
        self.table2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        vertical_headers_table2 = ["Group", "Hospital"]
        self.table2.setVerticalHeaderLabels(vertical_headers_table2)
        self.table2.horizontalHeader().setVisible(False)
        self.table2.setFixedHeight(self.table2.rowCount() * self.table2.rowHeight(0) + 2)
        self.table2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        scroll_area_layout.addWidget(self.table2)

        # spacer
        spacer2 = QLabel("Biometric Measurements")
        spacer2.setContentsMargins(0, 20, 0, 20)
        scroll_area_layout.addWidget(spacer2)

        # table 3
        self.table3 = QTableWidget()
        self.table3.setRowCount(4)
        self.table3.setColumnCount(1)
        self.table3.verticalHeader().setMinimumWidth(195)
        self.table3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        vertical_headers_table3 = ["Height (cm)", "Weight (kg)", "Right Leg Length (cm)", "Left Leg Length (cm)"]
        self.table3.setVerticalHeaderLabels(vertical_headers_table3)
        self.table3.horizontalHeader().setVisible(False)
        self.table3.setFixedHeight(self.table3.rowCount() * self.table3.rowHeight(0) + 2)
        self.table3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        scroll_area_layout.addWidget(self.table3)

        scroll_area.setWidget(scroll_area_widget)
        patient_layout.addWidget(scroll_area)

        patient_actions_box = QWidget()
        patient_actions_layout = QHBoxLayout() 
        patient_actions_box.setLayout(patient_actions_layout)
        patient_layout.addWidget(patient_actions_box)

        modify_patient_btn = QPushButton("Modify patient info")
        modify_patient_btn.setProperty("class", "fill_button_inverted")
        modify_patient_btn.clicked.connect(self.modify_patient)
        delete_patient_btn = QPushButton("Delete patient")
        delete_patient_btn.setProperty("class", "danger")
        delete_patient_btn.clicked.connect(self.delete_patient)
        patient_actions_layout.addWidget(modify_patient_btn)
        patient_actions_layout.addWidget(delete_patient_btn)

        comment_box = QFrame()
        comment_box.setContentsMargins(10, 10, 0, 10)
        comment_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        comment_box.setMaximumHeight(250)
        comment_layout = QVBoxLayout()
        comment_box.setLayout(comment_layout)
        comment_layout.setAlignment(Qt.AlignTop)
        comment_title = QLabel("Exercise Comment:")
        comment_layout.addWidget(comment_title)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        comment_layout.addWidget(line)

        # QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.comment_text_label = QLabel("")
        self.comment_text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.comment_text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.comment_text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.comment_text_label.setWordWrap(True)
        scroll_area.setWidget(self.comment_text_label)

        comment_layout.addWidget(scroll_area)
        right_layout.addWidget(comment_box)
                
        self.resizeEvent = self.resize_event
        self.right_box.hide()

        self.current_patient_id = None
        self.current_patient = None



# METHODS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def modify_patient(self):
        """
        MODIFIES: 
            - self
            - dataset.json
        
        EFFECTS: 
            - if a patient is selected open a modal to modify patients informations
            - updates patient informations into dataset.json
            - updates tables, list and search results into the GUI
        """
        if self.current_patient is None:
            QMessageBox.warning(self, "Error", "No patient selected.")
            return
        patient_modifier = PatientModifier(self.current_patient)
        self.current_patient = patient_modifier.get_patient_data()
        self.set_patient_tables(self.current_patient)
        self.reload_patient_list()
        self.updatesearchresults()

    def set_patient_tables(self, patient_data):
        """
        REQUIRES: 
            - patient_data (dictionary): valid patient data dictionary
        
        MODIFIES:
            - self

        EFFECTS: 
            - fills the tables with patient iformations
        """
        info = ["Name", "Surname", "Date_of_Birth", "CF", "Gender"]
        for i in range(5):
            item = QTableWidgetItem(patient_data[info[i]])
            self.table1.setItem(i, 0, item) 
        info = ["Group", "Hospital"]
        for i in range(2):
            item = QTableWidgetItem(patient_data[info[i]])
            self.table2.setItem(i, 0, item) 
        info = ["Height", "Weight", "Right_Leg_Length", "Left_Leg_Length"]
        for i in range(4):
            item = QTableWidgetItem(patient_data[info[i]])
            self.table3.setItem(i, 0, item) 

    def reset_patient_tables(self):
        """
        MODIFIES:
            - self

        EFFECTS: 
            - fills the tables with void str
        """
        for i in range(5):
            self.table1.setItem(i, 0, QTableWidgetItem(""))
        for i in range(2):
            self.table2.setItem(i, 0, QTableWidgetItem(""))
        for i in range(4):
            self.table3.setItem(i, 0, QTableWidgetItem(""))

    def toggle_right_box_visibility(self):
        """
        MODIFIES: 
            - self

        EFFECTS:
            - Toggles the visibility of the right box in the archive page based on the window width.
            - If the window width exceeds a specific threshold, the right box is shown; otherwise, it is hidden.
        """
        # 1057 standard width
        # 420 width needed for the right_box
        if (self.width() - 1057) >= 420: self.right_box.show()
        else: self.right_box.hide()

    def resize_event(self, event):
        """
        MODIFIES:
            - self
        
        EFFECTS: 
            - Adjusts the visibility of UI elements in response to a window resize event.
        """
        self.toggle_right_box_visibility()

    def delete_patient(self):
        """
        MODIFIES: 
            - self
        
        EFFECTS: 
            - Deletes the selected patient and their data from the database and archive folder.
            - Otherwise show the errors in a QMessageBox
        """
        patient_id = self.current_patient_id

        if patient_id is None: 
            QMessageBox.warning(self, "Error", "No patient selected.")
            return

        json_path = os.path.join(os.getcwd(), self.dataset_path)
        
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Patient database file not found.")
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error decoding patient database file.")
            return

        confirmation = QMessageBox.warning(self, "Confirm Deletion", "Are you sure you want to delete this patient and all patient's data?", QMessageBox.Yes | QMessageBox.No)
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

        patient_folder = os.path.join(os.getcwd(), "data", "archive", patient_id.upper()) if self.folder_name == "GUI" else os.path.join(os.getcwd(), "GUI", "data", "archive", patient_id.upper())
        try:
            shutil.rmtree(patient_folder)
            self.reset_patient_tables()
            self.reset()
            self.current_patient_id = None
            self.current_patient = None
            self.listView_folders.setModel(None)
            self.listView_folders.clearSelection()
            QMessageBox.information(self, "Deleting success", "Patient deleted successfully.")
        except FileNotFoundError:
            pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the patient folder: {str(e)}")

    def show_folder_context_menu(self, position):
        """
        MODIFIES: 
            - self
        
        EFFECTS: 
            - It shows the context menu for deleting a folder
        """
        index = self.listView_folders.indexAt(position)
        if index.isValid():
            self.folder_context_menu.exec_(self.listView_folders.mapToGlobal(position))

    def show_file_context_menu(self, position):
        """
        MODIFIES: 
            - self
        
        EFFECTS: 
            - It shows the context menu for deleting a file
        """
        index = self.listView_files.indexAt(position)
        if index.isValid():
            self.file_context_menu.exec_(self.listView_files.mapToGlobal(position))

    def show_context_menu(self, position):
        """
        REQUIRES:
            - position (QPoint): valid position in the window

        MODIFIES: 
            - self
        
        EFFECTS: 
            - It shows a context menu at specified position
        """
        self.context_menu.exec_(self.sender().mapToGlobal(position))

    def delete_selected_folder(self):
        """
        MODIFIES: 
            - self
            - archive folder
        
        EFFECTS: 
            - Deletes the selected folder and its contents from the archive folder.
            - Updates the folders and files models
            - Reset the plot
            - Reset the exercise comment
        """
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
                        
                if folder_path in self.file_model.filePath(index):
                    self.reset()

    def delete_selected_file(self):
        """
        MODIFIES: 
            - self
            - archive folder
        
        EFFECTS: 
            - Deletes the selected file npy
            - Updates the file model
            - Reset the plot
            - Reset the exercise comment
        """
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
                self.reset()    
       
    def on_folder_loaded(self):
        """
        MODIFIES: 
            - self

        EFFECTS:
            - sets the folder model into the listview
        """
        self.listView_folders.setRootIndex(self.folder_model.index(self.folder_path))

    def folder_clicked(self, index):
        """
        MODIFIES: 
            - self

        EFFECTS:
            - sets the selected files model into the listview
        """
        self.listView_files.setModel(self.file_model)
        folder_path = self.folder_model.fileInfo(index).absoluteFilePath()
        self.file_model.setRootPath(folder_path)
        self.listView_files.setRootIndex(self.file_model.index(folder_path))

    def load_selected_file(self, index):
        """
        REQUIRES: 
            - index (int): valid index of a files listview

        MODIFIES: 
            - self 

        EFFECTS:
            - loads the selected file
            - processes and plots the signals of the loaded file 
            - shows the matplotlib navigation toolbar
        """
        file_path = self.file_model.fileInfo(index).absoluteFilePath()
        try:
            loaded_data = np.load(file_path, allow_pickle=True)
            signals = loaded_data.item().get("signals")
            Fs = loaded_data.item().get("Fs")
            if loaded_data.item().get("comment") is not None:
                comment = loaded_data.item().get("comment") 
                self.comment_text_label.setText(comment)
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

        self.patients_list.itemClicked.connect(self.clicked_patient)

    def reload_patient_list(self):
        """
        MODIFIES:
            - self
        
        EFFECTS: 
            - replace the patient list with a new updated list
            - delete the old list
        """
        # self.patients_list.clear()
        tmp = self.patients_list
        tmp.deleteLater()
        self.patients_list = QListWidget()
        self.patients_list.setProperty("class", "archive_list")
        self.left_layout.addWidget(self.patients_list)
        self.load_patients_from_json()

    def clicked_patient(self, item):
        """
        REQUIRES: 
            - item (QListWidgetItem): valid item from patient list

        MODIFIES:
            - self

        EFFECTS:
            - If the clicked patient item is not already selected, selects it, updates the patient's data and the folders model.
            - else the clicked patient item is already selected, deselects it and resets the patient's data.
        """
        index = self.patients_list.row(item)

        if not self.selected_items[index]:
            self.select_patient_folder(item)
            patient_data = item.data(Qt.UserRole)
            self.current_patient = patient_data
            self.set_patient_tables(patient_data)
        else:
            self.current_patient_id = None
            self.current_patient = None
            self.reset_patient_tables()
            self.listView_folders.setModel(None)
            self.reset()
            item.setSelected(False)
        for i, _ in enumerate(self.selected_items):
            if i == index: self.selected_items[i] = not self.selected_items[i]
            else: self.selected_items[i] = False

    def select_patient_folder(self, item):
        """
        REQUIRES: 
            - item (QListWidgetItem): valid item from patient list

        MODIFIES:
            - self

        EFFECTS:
            - if avaiable updates the selectes folders model.
            - else reset the folders model
            - reset the folders listview
            - reset the files listview
            - reset the plotter
            - reset the comment
        """
        patient = item.data(Qt.UserRole)
        patient_id = (patient['ID']).upper()
        self.current_patient_id = patient_id
        self.folder_path = os.path.join(os.getcwd(), "data", "archive", patient_id) if self.folder_name == "GUI" else os.path.join(os.getcwd(), "GUI", "data", "archive", patient_id)
        if os.path.exists(self.folder_path):
            self.folder_model.setRootPath(self.folder_path) 
            self.listView_folders.setModel(self.folder_model)
            self.listView_folders.setRootIndex(self.folder_model.index(self.folder_path))
        else: self.listView_folders.setModel(None)
        self.listView_folders.clearSelection()
        self.reset()

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
                        item.setHidden(False)
                        no_results = False

        # if there are no patients show the label "no results found"
        if no_results:
            self.no_results_label.raise_()   # on top
            self.no_results_label.show()
        else:
            self.no_results_label.hide()

    def updatefilters(self, type, text):
        """
        REQUIRES:
            - type (str or None): must be a string from Hospitals, Groups, Genders, Ages or None

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

    def reset(self):
        """
        MODIFIES:
            - self

        EFFECTS:
            - reset the files listview
            - reset the plotter
            - reset the comment
        """
        if self.navigation_toolbar is not None: self.navigation_toolbar.setVisible(False)
        self.ax.clear()
        self.ax.grid(True, color="#FFE6E6")
        self.canvas.draw()
        self.listView_files.setModel(None)
        self.listView_files.clearSelection()
        self.comment_text_label.setText("")

    def clean_all(self):
        """
        MODIFIES: 
            - self
        
        EFFECTS:
            - updates more graphic elements.
            - reset patient list
            - reset tables
            - reset files listview
            - reset folders listview
            - reset plotter
            - reset comment
            - reset current patient and current patient id
        """
        self.patients_list.clear()
        self.load_patients_from_json()
        self.reset_patient_tables()
        self.listView_folders.setModel(None)
        self.listView_folders.clearSelection()
        self.reset()
        self.current_patient_id = None
        self.current_patient = None