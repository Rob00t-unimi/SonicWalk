import threading
import time
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import os
import sys
from datetime import datetime
import numpy as np

gui_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(gui_path)

from components.recButton import RecButton
from mtw_run import mtw_run

class RecordingFrame(QFrame):
    def __init__(self, light = True, getMusicModality = None, getMusicPath = None, getExerciseNumber = None):
        super().__init__()

        self.exerciseTime = 90
        self.selectedMusic = None
        self.selectedExercise = None
        self.modality = None

        self.getMusicModality = getMusicModality
        self.getMusicPath = getMusicPath
        self.getExerciseNumber = getExerciseNumber


        self.light = light
        self.blackIcons = "icons/black"
        self.whiteIcons = "icons/white"

        self.playAbilited = True
        self.execution = False
        self.startTime = None

        self.connection_msg = None
        self.signals = None
        self.Fs = None

        # create a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(15)

        # set self layout
        self.layout_actions = QVBoxLayout(self)
        self.layout_actions.addWidget(self)
        self.layout_actions.setContentsMargins(25, 25, 25, 25)

        # create new frame and set layout
        self.buttons_actions_frame = QFrame(self)
        self.buttons_layoutActions = QHBoxLayout(self.buttons_actions_frame)

        # Buttons

        # si vuole implementare lo stop?
        # se si stoppa si vuole poter salvare o si scarta la registrazione?
        self.stop_button = RecButton(light=self.light, icons_paths=["icons/square.svg", "icons/square.svg"], tooltip="Stop recording")
        self.buttons_layoutActions.addWidget(self.stop_button)
        self.stop_button.onClick(self.stopExecution)

        # create custom recording buttons
        self.play_button = RecButton(light=self.light, icons_paths=[self.blackIcons+"/play.svg", self.whiteIcons+"/play.svg"], tooltip="Start recording")
        self.buttons_layoutActions.addWidget(self.play_button)
        self.play_button.onClick(self.startExecution)

        # si vuole implementare salva manuale o si chiede sempre automaticamente?
        self.save_button = RecButton(light=self.light, icons_paths=[self.blackIcons+"/save.svg", self.whiteIcons+"/save.svg"], tooltip="Save the recording")
        self.buttons_layoutActions.addWidget(self.save_button)
        self.save_button.setEnabled(False)


        # Create timer label
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("color: black;" if self.light else "color: white;")
        font = self.time_label.font()
        font.setPointSize(15)
        self.time_label.setFont(font)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(25, 25, 25, 25)
        self.layout_actions.addWidget(self.time_label)

        # add all to the class frame
        self.layout_actions.addWidget(self.buttons_actions_frame)
        self.layout_actions.addWidget(self.time_label)
        self.layout_actions.setContentsMargins(25, 25, 25, 25)

        self.disablePlayButton()

    def toggleTheme(self):
        self.light = not self.light
        self.time_label.setStyleSheet("color: black;" if self.light else "color: white;")
        self.play_button.toggleTheme()
        self.stop_button.toggleTheme()
        self.save_button.toggleTheme()

    def enablePlayButton(self):
        if not self.playAbilited:
            self.playAbilited = True
            self.play_button.setEnabled(True)

    def disablePlayButton(self):
        if self.playAbilited:
            self.playAbilited = False
            self.play_button.setEnabled(False)

    def timeUpdater(self):
        if self.execution:
            current_time = time.time() - self.startTime
            if self.exerciseTime >= current_time:
                minutes, seconds = divmod(current_time, 60)
                # Calcola i centesimi di secondo
                centiseconds = int((current_time - int(current_time)) * 100)
                self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
            else:
                minutes, seconds = divmod(self.exerciseTime, 60)
                centiseconds = int((self.exerciseTime - int(self.exerciseTime)) * 100)
                self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
        else:
            self.time_label.setText("00:00.00")
            self.startTime = None

    def startExecution(self):

        self.modality = self.getMusicModality()
        self.selectedMusic = self.getMusicPath()
        self.selectedExercise = self.getExerciseNumber()

        self.execution = False

        self.showConnectionMessage()

        # Execute mtw_run in a different thread
        self.thread = threading.Thread(target=self.run_mtw)
        self.thread.daemon = True
        self.thread.start()

        self.check_mtw_run_timer = QTimer(self)
        self.check_mtw_run_timer.timeout.connect(self.check_mtw_run_status)
        self.check_mtw_run_timer.start(100)

    def check_mtw_run_status(self):
        if not self.thread.is_alive():
            self.execution = False
            self.startTime = None
            self.saveRecording()
            self.check_mtw_run_timer.stop()

    def run_mtw(self):
        analyze = False if self.modality != 2 else True
        try:
            self.signals, self.Fs = mtw_run(Duration=int(self.exerciseTime), MusicSamplesPath=self.selectedMusic, Exercise=self.selectedExercise, Analyze=analyze, setStart = self.setStart)
            # gestire il dongle non inserito
            self.mtw_run_finished.emit()
        except RuntimeError as e:
            self.connection_msg.setText(str(e))
            # non restituisce l'errore

    def showConnectionMessage(self):
        if self.connection_msg is None:
            self.connection_msg = QMessageBox(QMessageBox.Information, "Waiting for Sensor Connection", "Please wait while the sensors are connecting...", QMessageBox.NoButton, self)
        self.connection_msg.setWindowModality(Qt.ApplicationModal)
        self.connection_msg.setIcon(QMessageBox.NoIcon)
        self.connection_msg.setStandardButtons(QMessageBox.NoButton)
        self.connection_msg.show()

    def setStart(self):
        self.startTime = time.time()
        self.execution = True
        #beepPath = "../sonicwalk/audio_samples/beep.wav"
        #wave_obj = sa.WaveObject.from_wave_file(beepPath)
        #wave_obj.play()
        if self.connection_msg and not self.connection_msg.isHidden():
            self.connection_msg.reject()
        if self.modality == 1:
            # suona musica... 
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



        