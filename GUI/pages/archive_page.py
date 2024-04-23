import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QFont
import matplotlib.pyplot  as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

import sys
sys.path.append("../")
from components.customButton import CustomButton
from components.customSelect import CustomSelect

class ArchivePage(QFrame):
    def __init__(self, light = True, parent=None):
        super().__init__(parent)

        # theme style
        self.lightTheme = "background-color: #B6C2CF;"
        self.darkTheme ="background-color: #282E33;"

        # principal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create left box
        left_box = QWidget()
        left_box.setStyleSheet(self.lightTheme if light else self.darkTheme)
        left_box.setFixedWidth(375)

        # create left layout
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5, 0, 5, 0)
        left_box.setLayout(left_layout)
        layout.addWidget(left_box)

        # create research box
        research_box = QWidget()
        research_box.setFixedHeight(175)
        left_layout.addWidget(research_box)
        left_layout.setAlignment(Qt.AlignTop)
        research_box.setContentsMargins(0, 20, 0, 0)

        # create research box layout
        research_box_layout = QVBoxLayout()
        research_box.setLayout(research_box_layout)

        # create an add patient button
        add_patient_button = CustomButton(text="Add new patient", light=light, dimensions=[160, 40])
        research_box_layout.addWidget(add_patient_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

        search_and_toggle_layout = QHBoxLayout()

        # add search box
        search_lineedit = QLineEdit()
        search_lineedit.setFixedWidth(300)
        search_lineedit.setFixedHeight(80)
        search_lineedit.setPlaceholderText("Enter name, surname, ID or CF")
        search_lineedit.setStyleSheet("""
            background-color: #F5F5F5;
            border: 1px solid #DCDFE4;
            border-radius: 15px;
            padding: 5px;
            margin-top: 20px;
            margin-bottom: 20px;
            font-size: 15px;
        """)
        search_and_toggle_layout.addWidget(search_lineedit, alignment=Qt.AlignCenter)

        # filters

        # Aggiungi un pulsante per abilitare/disabilitare i filtri
        toggle_filter_button = CustomButton(text="+", dimensions = [35, 35], stayActive = True, light=light)
        search_and_toggle_layout.addWidget(toggle_filter_button)

        # Funzione per gestire il cambiamento di altezza della casella dei filtri
        def toggleFilterBox():
            if research_box.height() == 175:
                research_box.setFixedHeight(240)
                toggle_filter_button.setText("-")
                # research_box_layout.addWidget(filter_box, alignment=Qt.AlignCenter)
                filter_box.setVisible(True)
            else:
                research_box.setFixedHeight(175)
                toggle_filter_button.setText("+")
                # research_box_layout.removeWidget(filter_box)
                filter_box.setVisible(False)

        # Collega il pulsante alla funzione di gestione
        toggle_filter_button.onClick(toggleFilterBox)

        research_box_layout.addLayout(search_and_toggle_layout)

        # read json dataset
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        # filters widgets
        hospitals = set(patient['Hospital'] for patient in patient_data)
        groups = set(patient['Group'] for patient in patient_data)
        sexes = {'M', 'F'}
        age_ranges = {'0-20', '21-40', '41-60', '61-80', '81+'}

        # initialize normal selects for filters
        combo_style = """
            QComboBox {
                border: 1px solid #9B90DB; 
                border-radius: 5px;
                padding: 3px; 
                background-color: #f5f5f5; 
                font-size: 12px;
                color: #4C4C4C;
            }
            QComboBox::drop-down {
                width: 15px;
                border-left-width: 0px;
                border-left-color: transparent;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #9B90DB; 
            }
            QComboBox QAbstractItemView {
                border: 1px solid #9B90DB;
                background-color: #f5f5f5; /* Coerente con lo sfondo del ComboBox */
                selection-background-color: #9B90DB; /* Colore di sfondo per l'elemento selezionato */
                color: #4C4C4C;
            }
            QScrollBar:vertical {
                width: 10px; /* Larghezza della scrollbar */
                background-color: #f5f5f5; /* Coerente con lo sfondo del ComboBox */
            }
            QScrollBar::handle:vertical {
                background-color: #9B90DB; /* Colore della maniglia della scrollbar */
                border-radius: 5px; /* Bordi arrotondati */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background-color: transparent; /* Rimuove le linee aggiuntive sopra e sotto */
            }
        """

        hospital_combo = QComboBox()
        hospital_combo.addItems(["Hospitals"] + sorted(hospitals))
        hospital_combo.setStyleSheet(combo_style)

        group_combo = QComboBox()
        group_combo.addItems(["Groups"] + sorted(groups))
        group_combo.setStyleSheet(combo_style)

        sex_combo = QComboBox()
        sex_combo.addItems(["Genders"] + sorted(sexes))
        sex_combo.setStyleSheet(combo_style)

        age_combo = QComboBox()
        age_combo.addItems(["Age"] + sorted(age_ranges))
        age_combo.setStyleSheet(combo_style)


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
        filter_box.setVisible(False)

        # Patient Box
        patients_box = QScrollArea()
        patients_box.setStyleSheet("""
            QScrollArea {
                border: none;                                   
            }
            QScrollBar:vertical {
                width: 10px; 
                background-color: transparent;
            }
            QScrollBar::handle:vertical {
                background-color: #9B90DB; 
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background-color: transparent; 
            }
        """)
        patients_box.setWidgetResizable(True)  # Abilita la possibilità di scorrere all'interno dell'area

        # Creazione del widget contenitore per i pazienti
        patients_container = QWidget()
        patients_container_layout = QVBoxLayout()
        patients_container.setLayout(patients_container_layout)

        # Leggiamo il dataset JSON
        self.patients_list = QListWidget()  # Crea l'oggetto QListWidget per la lista dei pazienti
        self.patients_list.setStyleSheet("""
            QListWidget {
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 17px;
                font-family: sans-serif;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:hover {
                background-color: #DADFE5;
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background-color: #9B90DB;
                color: white;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: #EAEAEA;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #9B90DB;
                border-radius: 5px;
            }
        """)


        left_layout.addWidget(self.patients_list)
        self.load_patients_from_json()

        # create Central box
        central_box = QWidget()
        central_box.setMinimumWidth(650)

        # create Central layout
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
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
        central_bottom_box.setMaximumHeight(350)

        # create Central bottom layout
        central_bottom_layout = QHBoxLayout()
        central_bottom_layout.setContentsMargins(0, 0, 0, 0)
        central_bottom_box.setLayout(central_bottom_layout)
        central_layout.addWidget(central_bottom_box)


        # right box
        right_box = QWidget()
        right_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_box.setStyleSheet("""
            background-color: #ABB7C3;
        """
        )
        right_box.setMaximumWidth(375)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_box.setLayout(right_layout)
        layout.addWidget(right_box)


        # create Matplotlib plot
        self.fig, self.ax = plt.subplots()
        self.ax.plot([], [])
        self.ax.grid(True, color="#FFE6E6")
        self.fig.patch.set_facecolor('none')
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.1, hspace=0)

        # create a canvas for the plot
        self.canvas = FigureCanvas(self.fig)

        # add the canvas to the layout
        self.central_top_layout.addWidget(self.canvas)


        self.listView_folders = QListView()
        central_bottom_layout.addWidget(self.listView_folders)

        self.listView_files = QListView()
        central_bottom_layout.addWidget(self.listView_files)

        list_style = """
            QListView {
                background-color: #EAEAEA;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QListView::item {
                padding: 10px;
            }
            QListView::item:hover {
                background-color: #C1C8D3;
                border-radius: 10px;
            }
            QListView::item:selected {
                background-color: #9B90DB;
                color: white;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: #EAEAEA;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #9B90DB;
                border-radius: 5px;
            }
        """

        self.listView_folders.setStyleSheet(list_style)
        self.listView_files.setStyleSheet(list_style)
        self.listView_files.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.folder_model = QFileSystemModel()
        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "data", "archive")
        self.folder_model.setRootPath(self.folder_path)  
        self.folder_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.listView_folders.setModel(self.folder_model)
        self.listView_folders.clicked.connect(self.folder_clicked)
        self.folder_model.directoryLoaded.connect(self.on_folder_loaded)  # Aggiunto

        # Modello per i file
        self.file_model = QFileSystemModel()
        self.listView_files.setModel(self.file_model)
        self.file_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(["*.npy"])

        self.listView_files.clicked.connect(self.load_selected_file)

        self.navigation_toolbar = None


    def on_folder_loaded(self):
        self.listView_folders.setRootIndex(self.folder_model.index(self.folder_path))

    def folder_clicked(self, index):
        folder_path = self.folder_model.fileInfo(index).absoluteFilePath()
        self.file_model.setRootPath(folder_path)
        self.listView_files.setRootIndex(self.file_model.index(folder_path))

    def load_selected_file(self, index):
        file_path = self.file_model.fileInfo(index).absoluteFilePath()
        try:
            # Carica il file numpy
            loaded_data = np.load(file_path, allow_pickle=True)

            # Estrai i dati dal dizionario
            signals = loaded_data.item().get("signals")
            Fs = loaded_data.item().get("Fs")

            # Calcola il tempo per ogni campione
            time = np.arange(len(signals[0])) / Fs

            # Cancella i plot precedenti
            self.ax.clear()

            # Fai qualcosa con i dati (esempio: plottali)
            colors = ["b", "c"]
            i = 0
            for signal in signals:
                self.ax.plot(time, signal, color=colors[i])  # Stampa i segnali rispetto al tempo
                i += 1
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Angle (Deg)')
            self.ax.grid(True, color="#FFE6E6")

            # Aggiorna il canvas per visualizzare il nuovo plot
            self.canvas.draw()
            if self.navigation_toolbar is None: self.navigation_toolbar = NavigationToolbar(self.canvas, self)
            self.central_top_layout.addWidget(self.navigation_toolbar)

        except Exception as e:
            QMessageBox.warning(None, "Errore", f"Impossibile caricare il file: {str(e)}")

    def load_patients_from_json(self):
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        # Aggiungi ogni paziente alla lista
        for patient in patient_data:
            # Crea il testo del paziente con nome, cognome e ID
            patient_text = f"{patient['Name']} {patient['Surname']} (ID: {patient['ID']})"
            
            # Crea un elemento della lista per il paziente
            item = QListWidgetItem(patient_text)
            item.setData(Qt.UserRole, patient)  # Salva i dati del paziente nell'elemento della lista

            # Applica lo stile all'elemento della lista
            item.setTextAlignment(Qt.AlignLeft)
            # item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            # Aggiungi l'elemento alla lista
            self.patients_list.addItem(item)
