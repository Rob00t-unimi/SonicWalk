import threading
from PyQt5.QtWidgets import QFrame
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
import json
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QFont
from datetime import datetime, date
from pages.patient_selector import PatientSelector
from mtw_run import mtw_run
import os
import numpy as np




class AnalysisPage(QFrame):

    mtw_run_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.selectedExercise = 0
            # 0 --> walking
            # 1 --> Walking in place (High Knees, Butt Kicks)
            # 2 --> Walking in place (High Knees con sensori sulle cosce)
            # 3 --> Swing
            # 4 --> Double Step
            # 5 --> ROB's walking 
        
        self.modality = 1
        self.selectedMusic = "../sonicwalk/audio_samples/cammino_1_fase_2"

        self.execution = False
        self.startTime = None

        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        self.connection_msg = None
        self.signals = None
        self.Fs = None

        self.patient_info_data = [
            ("Name:", ""),
            ("Surname:", ""),
            ("ID:", ""),
            ("Group:", ""),
            ("Hospital:", "")
        ]

        self.setup_ui()

    def setup_ui(self):
        #time controller
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(15)

        # Page structure

        localcss =  """
            QPushButton {
                border: none;
                background-color: rgba(150, 150, 150, 10%);
                border-radius: 40px;
                
            }
            QPushButton:hover {
                background-color: rgba(108, 60, 229, 40%);
            }
            QPushButton:pressed {
                background-color: rgba(108, 60, 229, 60%);
            }
            """

        self.frame = QFrame()
        grid_layout = QGridLayout(self.frame)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        self.patient_frame = QFrame()    
        self.plotter_frame = QFrame()
        self.selection_frame = QFrame()
        self.actions_frame = QFrame()
        self.buttons_actions_frame = QFrame(self.actions_frame)

        layout_patient = QVBoxLayout(self.patient_frame)
        layout_patient.setContentsMargins(30, 30, 30, 30)
        layout_plotter = QVBoxLayout(self.plotter_frame)
        layout_selection = QVBoxLayout(self.selection_frame)
        layout_selection.setContentsMargins(30, 30, 30, 30)
        layout_actions = QVBoxLayout(self.actions_frame)
        buttons_layoutActions = QHBoxLayout(self.buttons_actions_frame)

        # patient table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setRowCount(5)
        self.table_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.table_widget.verticalHeader().hide()
        self.table_widget.horizontalHeader().hide()

        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # table style
        self.table_widget.setStyleSheet("""
            QTableWidget {
                border: 1px solid rgba(185, 153, 255, 80%);
                border-radius: 10px;
                font-family: Arial;
            }
        """)

        # table population
        for row, (label_text, data_text) in enumerate(self.patient_info_data):
            
            item_label = QTableWidgetItem("   " + label_text)
            item_data = QTableWidgetItem("   " + data_text)
            
            self.table_widget.setItem(row, 0, item_label)
            self.table_widget.setItem(row, 1, item_data)

        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_patient.addWidget(self.table_widget)

        layout_patient.setSpacing(20)

        button_seleziona_paziente = QPushButton("Select Patient")
        layout_patient.addWidget(button_seleziona_paziente, alignment=Qt.AlignHCenter)
        button_seleziona_paziente.setStyleSheet("QPushButton { border: none; text-align: center; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 50%); }")
        button_seleziona_paziente.setFixedSize(180, 40)
        button_seleziona_paziente.clicked.connect(self.selectPatient)

        # example plotter frame
        plotter_widget = self.createPlotter()
        layout_plotter.addWidget(plotter_widget)
        layout_plotter.setContentsMargins(10, 0, 0, 0)

        # select style
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

        # selection frame
        layout_selection.addWidget(QLabel("Selected Music:"))
        music_selector = QComboBox()
        music_selector.addItems(["Music 1"])
        # le musiche bisogna recuperarle da una cartella e metterle nela lista.

        music_selector.setStyleSheet(self.select_style)
        music_selector.currentTextChanged.connect(self.selectMusic)

        layout_selection.addWidget(music_selector)
        layout_selection.addWidget(QLabel("Selected Exercise:"))
        exercise_selector = QComboBox()
        exercise_selector.addItems(["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])
        exercise_selector.setStyleSheet(self.select_style)
        exercise_selector.currentTextChanged.connect(self.selectExercise)

        layout_selection.addWidget(exercise_selector)
        music_buttons_frame = QFrame()
        music_buttons_layout = QHBoxLayout(music_buttons_frame)
        music_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.noMusic_button = QPushButton("No Music")
        self.noMusic_button.clicked.connect(self.noMusicButtonClicked)
        self.music_button = QPushButton("Music")
        self.music_button.clicked.connect(self.musicButtonClicked)
        self.realTimeMusic_button = QPushButton("Real Time")
        self.realTimeMusic_button.clicked.connect(self.realTimeButtonClicked)
        music_buttons_layout.addWidget(self.noMusic_button)
        music_buttons_layout.addWidget(self.music_button)
        music_buttons_layout.addWidget(self.realTimeMusic_button)
        layout_selection.addWidget(music_buttons_frame)

        self.music_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.noMusic_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.realTimeMusic_button.setStyleSheet("QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.music_button.setFixedSize(110, 40)
        self.realTimeMusic_button.setFixedSize(110, 40)
        self.noMusic_button.setFixedSize(110, 40)

        # actions frame
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(self.blackIconPath + "play.svg"))
        self.play_button.clicked.connect(self.startExecution)
        self.play_button.setFixedSize(85, 85)
        self.play_button.setIconSize(QSize(25, 25)) 
        self.play_button.setStyleSheet(localcss)
        self.play_button.setToolTip("Start Recording")

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("icons/square.svg"))
        self.stop_button.clicked.connect(self.stopExecution)
        self.stop_button.setFixedSize(85, 85)
        self.stop_button.setIconSize(QSize(25, 25)) 
        self.stop_button.setStyleSheet(localcss)
        self.stop_button.setToolTip("Stop Recording")

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(self.blackIconPath + "save.svg"))
        self.save_button.clicked.connect(self.saveRecording)
        self.save_button.setFixedSize(85, 85)
        self.save_button.setIconSize(QSize(25, 25)) 
        self.save_button.setStyleSheet(localcss)
        self.save_button.setToolTip("Stop and Save Recording")

        buttons_layoutActions.addWidget(self.stop_button)
        buttons_layoutActions.addWidget(self.play_button)
        buttons_layoutActions.addWidget(self.save_button)
        self.time_label = QLabel("00:00:00")
        font = self.time_label.font()
        font.setPointSize(15)
        self.time_label.setFont(font)
        layout_actions.addWidget(self.buttons_actions_frame)
        layout_actions.addWidget(self.time_label)
        layout_actions.setContentsMargins(25, 25, 25, 25)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(25, 25, 25, 25)

        # add frames in the grid
        grid_layout.addWidget(self.patient_frame, 0, 0)
        grid_layout.addWidget(self.plotter_frame, 0, 1)
        grid_layout.addWidget(self.selection_frame, 1, 0)
        grid_layout.addWidget(self.actions_frame, 1, 1)

        # grid proportions
        grid_layout.addWidget(self.patient_frame, 0, 0, 1, 1)  # Alto a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.selection_frame, 1, 0, 2, 1)  # Basso a sinistra, altezza 1/3, larghezza 1/3
        grid_layout.addWidget(self.plotter_frame, 0, 1, 2, 3)  # Alto a destra, altezza 2/3, larghezza 2/3
        grid_layout.addWidget(self.actions_frame, 2, 1, 1, 3)  # Basso a destra, altezza 1/3, larghezza 2/3

        self.patient_frame.setMinimumWidth(200)
        self.plotter_frame.setMinimumWidth(200)
        self.selection_frame.setMinimumWidth(200)
        self.actions_frame.setMinimumWidth(200)

        # expansion policy
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

        # colors 
        self.selection_frame.setStyleSheet("background-color: #DCDFE4; border-top-left-radius: 15px; border-top-right-radius: 15px;")
        self.patient_frame.setStyleSheet("background-color: #DCDFE4; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;")

        # margins
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setContentsMargins(0, 0, 0, 0)

        self.realTimeButtonClicked()
        self.updatePlayButtonState()

    def selectExercise(self, text):
            print(text)
            if text == "Walk": self.selectedExercise = 0 
            elif text == "March in place (Hight Knees)": self.selectedExercise = 1
            elif text == "March in place (Butt Kicks)": self.selectedExercise = 1
            elif text == "Swing": self.selectedExercise = 3
            elif text == "Double Step": self.selectedExercise = 4
            return
    
    def selectMusic(self, text):
        print(text)
        if text == "Music 1": self.selectedMusic = "../sonicwalk/audio_samples/cammino_1_fase_2" 
        # elif text == "Music 2": self.selectedMusic = "../sonicwalk/audio_samples/..."

        return

    def timeUpdater(self):
        if self.execution:
            current_time = time.time() - self.startTime
            minutes, seconds = divmod(current_time, 60)
            # Calcola i centesimi di secondo
            centiseconds = int((current_time - int(current_time)) * 100)
            self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
        else:
            self.time_label.setText("00:00.00")
            self.startTime = None

    def selectPatient(self):
        
        patient_selector = PatientSelector()
        patient_selector.selectPatient()
        self.patient_info_data = patient_selector.getSelectedPatientInfo()
        self.updatePatientInfoTable()
        return

    def updatePatientInfoTable(self):
        for row, (label_text, data_text) in enumerate(self.patient_info_data):
            item_label = QTableWidgetItem("   " + label_text)
            item_data = QTableWidgetItem(data_text)
            
            self.table_widget.setItem(row, 0, item_label)
            self.table_widget.setItem(row, 1, item_data)

            self.updatePlayButtonState()
        return    
    
    def noMusicButtonClicked(self):
        self.modality = 0
        self.deactivate_buttons()
        self.noMusic_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); }")
        print("No Music")
    
    def musicButtonClicked(self):
        self.modality = 1
        self.deactivate_buttons()
        self.music_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); }")
        print("Music")
    
    def realTimeButtonClicked(self):
        self.modality = 2
        self.deactivate_buttons()
        self.realTimeMusic_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); }")
        print("Real time")

    def deactivate_buttons(self):
        self.noMusic_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.music_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.realTimeMusic_button.setStyleSheet("QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 7%); } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")

    def updatePlayButtonState(self):
        patient_id = self.patient_info_data[2][1]  # ID del paziente nella terza tupla
        if patient_id.strip() == "":
            self.play_button.setEnabled(False)
        else:
            self.play_button.setEnabled(True)

     
    def startExecution(self):
        self.execution = False

        self.showConnectionMessage()

        # Eseguire mtw_run in un thread separato per non bloccare la gui
        self.thread = threading.Thread(target=self.run_mtw)
        self.thread.daemon = True
        self.thread.start()

        self.check_mtw_run_timer = QTimer(self)
        self.check_mtw_run_timer.timeout.connect(self.check_mtw_run_status)
        self.check_mtw_run_timer.start(100)

    def run_mtw(self):
        analyze = False if self.modality != 2 else True
        try:
            self.signals, self.Fs = mtw_run(Duration=10, MusicSamplesPath=self.selectedMusic, Exercise=self.selectedExercise, Analyze=analyze, setStart = self.setStart)
            # gestire il dongle non inserito
            self.mtw_run_finished.emit()
        except RuntimeError as e:
            self.connection_msg.setText(str(e))
            # non restituisce l'errore
    
    def check_mtw_run_status(self):
        if not self.thread.is_alive():
            self.execution = False
            self.startTime = None
            self.saveRecording()  # Esegui il salvataggio
            self.check_mtw_run_timer.stop()
            
    def showConnectionMessage(self):
        if self.connection_msg is None:
            self.connection_msg = QMessageBox(QMessageBox.Information, "Waiting for Sensor Connection", "Please wait while the sensors are connecting...", QMessageBox.NoButton, self)
        self.connection_msg.setWindowModality(Qt.ApplicationModal)
        self.connection_msg.setIcon(QMessageBox.NoIcon)
        # impedire all'utente di chiudere il popup, con la seguente linea si riesce ma poi non si riesce a chiuderlo nemmeno dal codice
        #self.connection_msg.setStandardButtons(QMessageBox.NoButton)
        self.connection_msg.show()

    def setStart(self):
        time.sleep(1)
        self.startTime = time.time()
        self.execution = True
        if self.connection_msg and not self.connection_msg.isHidden():
            self.connection_msg.close()
        if self.modality == 1:
            # suona una canzone... 
            return
        return
    
    def stopExecution(self):
        # per implementarla bisogna rivedere la logica del codice di sonicwalk
        self.execution = False
        self.startTime = None

        ## interruzione della registrazione (sicura), deve rimettere i sensori nella modalità corretta
        return
    

    def saveRecording(self):
        # Chiedi conferma prima di salvare la registrazione
        confirm_msg = QMessageBox()
        confirm_msg.setIcon(QMessageBox.Question)
        confirm_msg.setWindowTitle("Confirm Save")
        confirm_msg.setText("Do you want to save the recording?")
        confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Ottieni il pulsante premuto
        response = confirm_msg.exec_()


        # Se l'utente ha confermato, salva la registrazione
        if response == QMessageBox.Yes:
            try:
                if self.signals is None or self.Fs is None:
                    raise ValueError("No signals to save")

                # Trova l'ID del paziente corrente
                patient_id = self.patient_info_data[2][1]  # ID del paziente nella terza tupla

                # Verifica se l'ID del paziente è vuoto
                if patient_id.strip() == "":
                    raise ValueError("Patient ID is empty")

                # Genera un nome univoco per il file
                today_date = datetime.today().strftime('%Y-%m-%d')
                parent_dir = os.path.dirname(os.path.abspath(__file__))
                directory_path = os.path.join(parent_dir.replace("pages",""), f"data/archive/{patient_id}")
                os.makedirs(directory_path, exist_ok=True)  # Crea la directory se non esiste
                filename = os.path.join(directory_path, f"{patient_id}_ex.{self.selectedExercise}_{today_date}_1.npy")

                # Verifica l'esistenza del file e genera un numero progressivo univoco se necessario
                counter = 1
                while os.path.exists(filename):
                    filename = os.path.join(directory_path, f"{patient_id}_ex.{self.selectedExercise}_{today_date}_{counter}.npy")
                    counter += 1

                # Salva i dati nel file numpy
                np.save(filename, {"signals": self.signals, "Fs": self.Fs})

                # Messaggio di conferma
                msg = QMessageBox()
                msg.setIconPixmap(QPixmap("icons/checkmark.png").scaledToWidth(50))
                msg.setWindowTitle("Recording Saved")
                msg.setText("Your recording has been saved successfully.")
                msg.setStandardButtons(QMessageBox.Ok)
        
                ok_button = msg.button(QMessageBox.Ok)
                ok_button.setMinimumWidth(100)
                ok_button.setMinimumHeight(40)
                msg.exec_()

            except Exception as e:
                # Gestione dell'eccezione nel caso in cui non sia possibile salvare il file o l'ID del paziente sia vuoto
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setWindowTitle("Error")
                error_msg.setText(f"An error occurred while saving the recording: {str(e)}")
                error_msg.setStandardButtons(QMessageBox.Ok)
                
                ok_button = error_msg.button(QMessageBox.Ok)
                ok_button.setMinimumWidth(100)
                ok_button.setMinimumHeight(40)
                error_msg.exec_()


    def createPlotter(self):
        # il plotter real time qui è ancora da implementare

        # esempio fake:
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

        canvas = FigureCanvas(fig)
        canvas.setContentsMargins(0, 0, 0, 0)

        return canvas
    
    def get_frame(self):
        return self.frame
