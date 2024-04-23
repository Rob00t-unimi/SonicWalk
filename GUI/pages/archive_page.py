import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        # Aggiungiamo un pulsante per ogni paziente
        for patient in patient_data:
            # Crea il testo del pulsante con nome, cognome e ID
            patient_text = f"{patient['Name']} {patient['Surname']} (ID: {patient['ID']})"

            patient_button = QPushButton(patient_text)  # Crea il pulsante con il testo del paziente
            font = QFont("Sans Serif", 10)
            patient_button.setFont(font)
            patient_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 10px;
                    text-align: left;
                    background-color: #C1C8D3;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(108, 60, 229, 30%); 
                    border-radius: 15px;
                }
            """)

            patients_container_layout.addWidget(patient_button)  # Aggiungi il pulsante al layout verticale

        # Imposta il widget contenitore all'interno dell'area di scorrimento
        patients_box.setWidget(patients_container)

        left_layout.addWidget(patients_box)  # Aggiungi la QScrollArea al layout sinistro


        # create Right box
        right_box = QWidget()

        # create Right layout
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_box.setLayout(right_layout)
        layout.addWidget(right_box)

        # create Right top
        right_top_box = QWidget()
        right_top_box.setStyleSheet("""
            background-color: #A4AFBC;
        """
        )

        # create Right top layout
        right_top_layout = QVBoxLayout()
        right_top_layout.setContentsMargins(0, 0, 0, 0)
        right_top_box.setLayout(right_top_layout)
        right_layout.addWidget(right_top_box)

        # create Right bottom
        right_bottom_box = QWidget()
        right_bottom_box.setFixedHeight(300)
        right_bottom_box.setStyleSheet("""
            background-color: #ABB7C3;
        """
        )
        right_bottom_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # create Right bottom layout
        right_bottom_layout = QVBoxLayout()
        right_bottom_layout.setContentsMargins(0, 0, 0, 0)
        right_bottom_box.setLayout(right_bottom_layout)
        right_layout.addWidget(right_bottom_box)
