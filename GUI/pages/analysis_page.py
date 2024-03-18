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



class AnalysisPage(QFrame):
    def __init__(self):
        super().__init__()
        # codice...

        self.selectedExercise = 1
        self.modality = 1
        self.selectedMusic = 1

        self.execution = False
        self.startTime = None

        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        self.patient_info_data = [
            ("Nome:", ""),
            ("Cognome:", ""),
            ("ID:", ""),
            ("Gruppo:", ""),
            ("Ospedale:", "")
        ]

        self.setup_ui()

    def setup_ui(self):
        # set a time controller
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(1000)  # Aggiorna ogni secondo

        # Struttura pagina:

        localcss =  """
            QPushButton {
                border: none;
                background-color: rgba(150, 150, 150, 10%);
                border-radius: 40px;
                
            }
            QPushButton:hover {
                background-color: rgba(108, 60, 229, 40%);
            }
            """

        self.frame = QFrame()

        # Crea un layout a griglia per il frame principale
        grid_layout = QGridLayout(self.frame)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # Crea i frame interni
        self.patient_frame = QFrame()    
        self.plotter_frame = QFrame()
        self.selection_frame = QFrame()
        self.actions_frame = QFrame()
        self.buttons_actions_frame = QFrame(self.actions_frame)

        # Crea i layout per i frame interni
        layout_patient = QVBoxLayout(self.patient_frame)
        layout_patient.setContentsMargins(30, 30, 30, 30)
        layout_plotter = QVBoxLayout(self.plotter_frame)
        layout_selection = QVBoxLayout(self.selection_frame)
        layout_selection.setContentsMargins(30, 30, 30, 30)
        layout_actions = QVBoxLayout(self.actions_frame)
        buttons_layoutActions = QHBoxLayout(self.buttons_actions_frame)


        # Creazione della tabella
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setRowCount(5)
        self.table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        # Nascondi l'header della tabella
        self.table_widget.verticalHeader().hide()
        self.table_widget.horizontalHeader().hide()

        # Disabilita la selezione della tabella
        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)

        # Personalizza lo stile della tabella
        self.table_widget.setStyleSheet("""
            QTableWidget {
                border: 1px solid rgba(185, 153, 255, 80%);
                border-radius: 10px;
                font-family: Arial;
            }
        """)

        # Itera attraverso i dati e aggiungi ciascun elemento alla tabella
        for row, (label_text, data_text) in enumerate(self.patient_info_data):
            
            item_label = QTableWidgetItem("   " + label_text)
            item_data = QTableWidgetItem("   " + data_text)
            
            self.table_widget.setItem(row, 0, item_label)  # Aggiungi l'item della colonna delle etichette
            self.table_widget.setItem(row, 1, item_data)   # Aggiungi l'item della colonna dei valori

        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Aggiungi la tabella al layout del frame del paziente
        layout_patient.addWidget(self.table_widget)


        layout_patient.setSpacing(20)

        button_seleziona_paziente = QPushButton("Select Patient")
        layout_patient.addWidget(button_seleziona_paziente, alignment=Qt.AlignHCenter)
        button_seleziona_paziente.setStyleSheet("QPushButton { border: none; text-align: center; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        button_seleziona_paziente.setFixedSize(180, 40)
        button_seleziona_paziente.clicked.connect(self.selectPatient)

        # Codice per il frame del plotter
        plotter_widget = self.createPlotter()
        layout_plotter.addWidget(plotter_widget)
        layout_plotter.setContentsMargins(10, 0, 0, 0)

        # Definisci lo stile comune per entrambe le select
        self.select_style = """
            QComboBox {
                border: 1px solid #B99AFF; /* Bordi viola meno intenso */
                border-radius: 15px; /* Bordo arrotondato */
                padding: 10px; /* Aumenta il padding */
                background-color: #FFFFFF; /* Sfondo bianco */
                selection-background-color: #B99AFF; /* Colore di selezione */
                font-size: 15px; /* Ingrandisci il testo */
                color: #4C4C4C; /* Colore del testo */
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px; /* Aumenta la larghezza della freccia */
                border-left-width: 0px;
                border-left-color: transparent;
                border-top-right-radius: 15px; /* Bordo arrotondato */
                border-bottom-right-radius: 15px; /* Bordo arrotondato */
                background-color: #B99AFF; /* Colore di sfondo della freccia */
            }
            QComboBox QAbstractItemView {
                border: 1px solid #B99AFF; /* Bordi viola meno intenso */
                selection-background-color: #9C6BE5; /* Colore di selezione */
                background-color: #FFFFFF; /* Sfondo bianco */
                font-size: 14px; /* Ingrandisci il testo */
                color: #4C4C4C; /* Colore del testo */
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

        # Codice per il frame della selezione
        layout_selection.addWidget(QLabel("Selected Music:"))
        music_selector = QComboBox()
        music_selector.addItems(["Music 1", "Music 2"])

        # Applica lo stile alla select delle musiche
        music_selector.setStyleSheet(self.select_style)

        layout_selection.addWidget(music_selector)
        layout_selection.addWidget(QLabel("Selected Exercise:"))
        exercise_selector = QComboBox()
        exercise_selector.addItems(["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])

        # Applica lo stile alla select degli esercizi
        exercise_selector.setStyleSheet(self.select_style)

        layout_selection.addWidget(exercise_selector)
        music_buttons_frame = QFrame()
        music_buttons_layout = QHBoxLayout(music_buttons_frame)
        music_buttons_layout.setContentsMargins(0, 0, 0, 0)
        noMusic_button = QPushButton("No Music")
        music_button = QPushButton("Music")
        realTimeMusic_button = QPushButton("Real Time")
        music_buttons_layout.addWidget(noMusic_button)
        music_buttons_layout.addWidget(music_button)
        music_buttons_layout.addWidget(realTimeMusic_button)
        layout_selection.addWidget(music_buttons_frame)

        music_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        noMusic_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        realTimeMusic_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        music_button.setFixedSize(110, 40)
        realTimeMusic_button.setFixedSize(110, 40)
        noMusic_button.setFixedSize(110, 40)

        

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(self.blackIconPath + "play.svg"))
        self.play_button.clicked.connect(self.startExecution)
        self.play_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.play_button.setIconSize(QSize(25, 25)) 
        self.play_button.setStyleSheet(localcss)
        self.play_button.setToolTip("Start Recording")

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("icons/square.svg"))
        self.stop_button.clicked.connect(self.stopExecution)
        self.stop_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.stop_button.setIconSize(QSize(25, 25)) 
        self.stop_button.setStyleSheet(localcss)
        self.stop_button.setToolTip("Stop Recording")

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(self.blackIconPath + "save.svg"))
        self.save_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.save_button.setIconSize(QSize(25, 25)) 
        self.save_button.setStyleSheet(localcss)
        self.save_button.setToolTip("Stop and Save Recording")

        # Codice per il frame delle azioni
        buttons_layoutActions.addWidget(self.stop_button)
        buttons_layoutActions.addWidget(self.play_button)
        buttons_layoutActions.addWidget(self.save_button)
        self.time_label = QLabel("00:00:00")
        font = self.time_label.font()
        font.setPointSize(15)  # Imposta la dimensione del font a 20
        self.time_label.setFont(font)
        layout_actions.addWidget(self.buttons_actions_frame)
        layout_actions.addWidget(self.time_label)
        layout_actions.setContentsMargins(25, 25, 25, 25)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(25, 25, 25, 25)


        # Aggiungi i frame alla griglia
        grid_layout.addWidget(self.patient_frame, 0, 0)
        grid_layout.addWidget(self.plotter_frame, 0, 1)
        grid_layout.addWidget(self.selection_frame, 1, 0)
        grid_layout.addWidget(self.actions_frame, 1, 1)

        # Imposta le proporzioni dei box nella griglia
        grid_layout.addWidget(self.patient_frame, 0, 0, 1, 1)  # Alto a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.selection_frame, 1, 0, 2, 1)  # Basso a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.plotter_frame, 0, 1, 2, 3)  # Alto a destra, altezza 2/3, larghezza 2/3
        grid_layout.addWidget(self.actions_frame, 2, 1, 1, 3)  # Basso a destra, altezza 1/3, larghezza 2/3

        # Imposta le dimensioni minime dei frame
        self.patient_frame.setMinimumWidth(200)
        self.plotter_frame.setMinimumWidth(200)
        self.selection_frame.setMinimumWidth(200)
        self.actions_frame.setMinimumWidth(200)

        # Imposta la policy di espansione
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

        self.selection_frame.setStyleSheet("background-color: #DCDFE4; border-top-left-radius: 15px; border-top-right-radius: 15px;")
        self.patient_frame.setStyleSheet("background-color: #DCDFE4; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;")

        # Imposta i margini della griglia e del frame principale a zero
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setContentsMargins(0, 0, 0, 0)


    def selectExercise(self, text):
            print(text)
            if text == "Walk": self.selectedExercise = 1 
            elif text == "March in place (Hight Knees)": self.selectedExercise = 2
            elif text == "March in place (Butt Kicks)": self.selectedExercise = 2
            elif text == "Swing": self.selectedExercise = 3
            elif text == "Unknown": self.selectedExercise = 4

            return
    
    def selectMusic(self, text):
        print(text)
        if text == "Music 1": self.selectedMusic = 1 
        elif text == "Music 2": self.selectedMusic = 2

        return

    def timeUpdater(self):
        if self.execution:
            current_time = time.time() - self.startTime
            hours, remainder = divmod(current_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label.setText("{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds)))
        else:
            self.time_label.setText("00:00:00")
            self.startTime = None


        
    def startExecution(self):
        self.execution = True
        self.startTime = time.time()
        ## ...
        return
    
    def stopExecution(self):
        self.execution = False
        self.startTime = None
        ## ...
        return
    

    def selectPatient(self):
        # Apri una finestra di dialogo per la selezione del paziente
        dialog = QDialog()
        dialog.setWindowTitle("Seleziona Paziente")
        
        # Applica uno stile personalizzato alla finestra di dialogo
        dialog.setStyleSheet("""
            background-color: #FFFFFF;
            color: #333333;
            font-size: 12pt;
        """)
        
        # Leggi il file JSON e ottieni i dati dei pazienti
        with open('data/dataset.json', 'r') as file:
            patient_data = json.load(file)

        # Creazione dei widget per i filtri
        hospitals = set(patient['Ospedale'] for patient in patient_data)
        groups = set(patient['Gruppo'] for patient in patient_data)
        sexes = {'Maschio', 'Femmina'}
        age_ranges = {'0-20', '21-40', '41-60', '61-80', '81+'}

        # Creazione delle opzioni per i filtri
        hospital_combo = QComboBox()
        hospital_combo.addItem("Tutti gli ospedali")
        hospital_combo.addItems(sorted(hospitals))
        hospital_combo.setStyleSheet(self.select_style)

        group_combo = QComboBox()
        group_combo.addItem("Tutti i gruppi")
        group_combo.addItems(sorted(groups))
        group_combo.setStyleSheet(self.select_style)

        sex_combo = QComboBox()
        sex_combo.addItem("Qualsiasi sesso")
        sex_combo.addItems(sorted(sexes))
        sex_combo.setStyleSheet(self.select_style)

        age_combo = QComboBox()
        age_combo.addItem("Qualsiasi età")
        age_combo.addItems(sorted(age_ranges))
        age_combo.setStyleSheet(self.select_style)

        # Creazione della casella di ricerca
        search_lineedit = QLineEdit()
        # search_lineedit.setAlignment(Qt.AlignCenter)
        search_lineedit.setPlaceholderText("Inserisci nome, cognome, ID o CF")
        search_lineedit.setStyleSheet("""
            background-color: #F5F5F5;
            border: 1px solid #DCDFE4;
            border-radius: 15px;
            padding: 5px;
            margin-top: 20px;
            margin-bottom: 20px;
        """)
        
        # Creazione del layout per i filtri
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Ospedale:"))
        filter_layout.addWidget(hospital_combo)
        filter_layout.addWidget(QLabel("Gruppo:"))
        filter_layout.addWidget(group_combo)
        filter_layout.addWidget(QLabel("Sesso:"))
        filter_layout.addWidget(sex_combo)
        filter_layout.addWidget(QLabel("Età:"))
        filter_layout.addWidget(age_combo)

        # Creazione del layout per la barra di ricerca
        search_layout = QVBoxLayout()
        search_layout.addWidget(search_lineedit)
        search_layout.addLayout(filter_layout)

        # Creazione del frame per i pazienti
        patient_frame = QFrame()
        patient_frame_layout = QVBoxLayout()
        patient_frame.setLayout(patient_frame_layout)

        # Inserimento del frame dei pazienti all'interno di uno scroll area
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

        # Funzione per calcolare l'età data una data di nascita
        def calculate_age(birth_date):
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age

        # Funzione per verificare se un'età è inclusa in un certo intervallo
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

        # Funzione per filtrare i pazienti in base ai filtri selezionati
        def filter_patients():
            filtered_patients = []
            for patient in patient_data:
                sex = "Maschio" if patient['Sesso'] == "M" else "Femmina"
                if (
                    hospital_combo.currentText() == "Tutti gli ospedali"
                    or patient['Ospedale'] == hospital_combo.currentText()
                ) and (
                    group_combo.currentText() == "Tutti i gruppi"
                    or patient['Gruppo'] == group_combo.currentText()
                ) and (
                    sex_combo.currentText() == "Qualsiasi sesso" or sex == sex_combo.currentText()
                ):
                    # Calcolo dell'età dal campo "Data di nascita"
                    birth_date = datetime.strptime(patient['Data_Nascita'], "%Y-%m-%d")
                    age = calculate_age(birth_date)
                    if (
                        age_combo.currentText() == "Qualsiasi età"
                        or age_in_range(age, age_combo.currentText())
                    ):
                        filtered_patients.append(patient)

            return filtered_patients

        # Funzione per aggiornare i risultati della ricerca in base alla stringa di ricerca inserita
        def update_search_results():
            search_text = search_lineedit.text().lower()
            for button in buttons:
                button.setVisible(search_text in button.text().lower())

        # Funzione per ricaricare i pulsanti dei pazienti filtrati
        def reload_buttons():
            nonlocal buttons
            filtered_patients = filter_patients()
    
            # Rimuovi i pulsanti precedenti e l'etichetta "Nessun risultato trovato" se presente
            for button in buttons:
                button.deleteLater()
            for i in reversed(range(patient_frame_layout.count())):
                widget = patient_frame_layout.itemAt(i).widget()
                if widget is not None and widget.text() == "Nessun risultato trovato.":
                    widget.deleteLater()

            buttons = []
            def create_patient_button(patient, dialog):
                button_layout = QHBoxLayout()

                button_label_1 = QLabel(f"<span style='color: black; text-align: center;'>{patient['Nome']} {patient['Cognome']}</span>")
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

                # Definiamo una nuova funzione per il clic della QLabel che non usa l'evento
                def label_click_event(event):
                    button.click()

                # Collegamento del clic sulla QLabel al clic del QPushButton
                button_label_1.mousePressEvent = label_click_event
                button_label_2.mousePressEvent = label_click_event

                patient_frame_layout.addWidget(button)
                buttons.append(button)

            # Utilizziamo la funzione create_patient_button nel ciclo
            for patient in filtered_patients:
                create_patient_button(patient, dialog)

            
            if len(filtered_patients) == 0:
                for i in reversed(range(patient_frame_layout.count())):
                    widget = patient_frame_layout.itemAt(i).widget()
                no_results_label = QLabel("Nessun risultato trovato.")
                patient_frame_layout.addWidget(no_results_label)

        def on_filter_changed():
            reload_buttons()
            update_search_results()

        # Connessioni per l'aggiornamento dei risultati quando i filtri cambiano
        hospital_combo.currentIndexChanged.connect(on_filter_changed)
        group_combo.currentIndexChanged.connect(on_filter_changed)
        sex_combo.currentIndexChanged.connect(on_filter_changed)
        age_combo.currentIndexChanged.connect(on_filter_changed)
        search_lineedit.textChanged.connect(update_search_results)

        # Carica i pulsanti iniziali
        buttons = []
        reload_buttons()
        update_search_results()

        # Creazione del layout per la finestra di dialogo
        main_layout = QVBoxLayout()
        main_layout.addLayout(search_layout)
        main_layout.addWidget(scroll_area)  # Aggiungo lo scroll area invece del frame dei pazienti


        # Aggiunta del layout principale alla finestra di dialogo
        dialog.setLayout(main_layout)

        dialog.exec_()


    def loadPatientData(self, patient, dialog):
        # Carica i dati del paziente selezionato
        self.patient_info_data = [
            ("Nome:", patient["Nome"]),
            ("Cognome:", patient["Cognome"]),
            ("ID:", patient["ID"]),
            ("Gruppo:", patient["Gruppo"]),
            ("Ospedale:", patient["Ospedale"])
        ]

        # Aggiorna la tabella con i nuovi dati del paziente
        self.updatePatientInfoTable(dialog.accept)

    def updatePatientInfoTable(self, accept_function):
        # Itera attraverso i dati del paziente e aggiorna la tabella
        for row, (label_text, data_text) in enumerate(self.patient_info_data):
            item_label = QTableWidgetItem("   " + label_text)
            item_data = QTableWidgetItem(data_text)
            
            self.table_widget.setItem(row, 0, item_label)  # Aggiorna l'item della colonna delle etichette
            self.table_widget.setItem(row, 1, item_data)   # Aggiorna l'item della colonna dei valori

        accept_function()


    def createPlotter(self):
        # Crea una figura di esempio
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

        # Crea un canvas per il plotter e collega la figura ad esso
        canvas = FigureCanvas(fig)
        canvas.setContentsMargins(0, 0, 0, 0)

        return canvas
    
    def get_frame(self):
        return self.frame
