import threading
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap
import os
import sys
from datetime import datetime
import numpy as np
import simpleaudio as sa    # simpleaudio has problems with the python threading GIL 
import pygame

sys.path.append("../")

from mtw_run import MtwThread

class RecordingFrame(QWidget):

    thread_signal = pyqtSignal()
    thread_signal_start = pyqtSignal()

    def __init__(self, light = True, getMusicModality = None, getMusicPath = None, getExerciseNumber = None, getPatient = None, getBpm = None, setBpm = None, changeEnabledAll = None, shared_data = None, plotter_start = None, setSaved = None):#, mtw_run_finished = None):
        """
        This class represents the frame responsible for handling recording functionalities.

        Requires:
            - light: A boolean indicating the theme of the frame.
            - getMusicModality: A function to retrieve the selected music modality.
            - getMusicPath: A function to retrieve the path of the selected music.
            - getExerciseNumber: A function to retrieve the selected exercise number.
            - changeEnabledAll: A function to call when we would change the enabled state of external components.

        Modifies:
            - self

        Effects:
            - Manages recording functionalities such as starting, stopping, and saving recordings.
        """
        super().__init__()

        self.setObjectName("recording_frame")

        self.thread_signal.connect(self.stop_by_musicError)
        self.thread_signal_start.connect(self.setStart)

        # initialize attributes
        self.shared_data = shared_data
        self.plotter_start = plotter_start
        self.setSaved = setSaved
        self.exerciseTime = 45 #90
        self.selectedMusic = None
        self.selectedExercise = None
        self.modality = None
        self.patient_info_data = None
        self.calculateBpm = False
        self.bpm = None
        # self.mtw_run_finished = mtw_run_finished

        self.getMusicModality = getMusicModality
        self.getMusicPath = getMusicPath
        self.getExerciseNumber = getExerciseNumber
        self.changeEnabledAll = changeEnabledAll
        self.getPatient = getPatient
        self.getBpm = getBpm
        self.setBpm = setBpm

        self.light = light

        self.playAbilited = True    # state of the play button
        self.execution = False      # state of the execution
        self.startTime = None       # start execution time
        self.playingMusic = False

        # sinals for multithreading
        self.connection_msg = None
        self.signals = None
        self.Fs = None

        self.record_thread = None

        # init pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        # create a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(50)

        # set self layout
        self.layout_actions = QVBoxLayout(self)
        self.layout_actions.setContentsMargins(25, 25, 25, 25)

        # create new frame and set layout
        self.buttons_actions_frame = QWidget(self)
        self.buttons_layoutActions = QHBoxLayout(self.buttons_actions_frame)

        # Buttons

        self.buttons_layoutActions.addStretch()

        # create custom recording buttons
        self.play_button = QPushButton()
        self.play_button.setIconSize(QSize(25, 25))
        self.play_button.setFixedSize(85, 85)
        self.play_button.setProperty("icon_name", "play")
        self.play_button.setProperty("class", "rec_button")
        self.play_button.setToolTip("Start Recording")
        self.buttons_layoutActions.addWidget(self.play_button)
        self.play_button.clicked.connect(self.startExecution)

        self.buttons_layoutActions.addStretch()

        self.stop_button = QPushButton()
        self.stop_button.setProperty("icon_name", "stop")
        self.stop_button.setIconSize(QSize(25, 25))
        self.stop_button.setFixedSize(85, 85)
        self.stop_button.setProperty("class", "rec_button")
        self.stop_button.setToolTip("Stop Recording")
        self.buttons_layoutActions.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stopExecution)


        self.buttons_layoutActions.addStretch()


        # Create timer label
        self.time_label = QLabel("00:00:00")
        self.time_label.setProperty("class", "")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setContentsMargins(25, 25, 25, 25)
        self.layout_actions.addWidget(self.time_label)

        # add all to the class frame
        self.layout_actions.addWidget(self.buttons_actions_frame)
        self.layout_actions.addWidget(self.time_label)
        self.layout_actions.setContentsMargins(25, 25, 25, 25)

        self.disablePlayButton()

    def closeEvent(self, event):
        print("bye bye")
        if self.record_thread is not None and self.record_thread.is_alive():
            self.record_thread.interrupt_recording(lambda: self.setSaved(None))

    def enablePlayButton(self):
        """
            Modifies:   self.playAbilited
            Effects:    Enables the play button.
        """
        if not self.playAbilited:
            self.playAbilited = True
            self.play_button.setEnabled(True)
            self.play_button.setToolTip("Start Recording")
            opacity_effect = QGraphicsOpacityEffect(self.play_button)
            opacity_effect.setOpacity(1.0)
            self.play_button.setGraphicsEffect(opacity_effect)

    def disablePlayButton(self):
        """
            Modifies:   self.playAbilited
            Effects:    Disables the play button.
        """
        if self.playAbilited:
            self.playAbilited = False
            self.play_button.setEnabled(False)
            self.play_button.setToolTip("Please select a patient before recording.")
            opacity_effect = QGraphicsOpacityEffect(self.play_button)
            opacity_effect.setOpacity(0.6)
            self.play_button.setGraphicsEffect(opacity_effect)

    def timeUpdater(self):
        """
            Modifies:   self.time_label
                        self.startTime
            Effects:    Updates the timer label during the recording.
        """
        if self.execution:
            current_time = time.time() - self.startTime
            if self.exerciseTime >= current_time:
                minutes, seconds = divmod(current_time, 60)
                centiseconds = int((current_time - int(current_time)) * 100)
                self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
                if max(0, self.exerciseTime - current_time) <= 10:
                    self.time_label.hide()
                    self.time_label = QLabel("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
                    self.time_label.setProperty("class", "red_label")
                    self.time_label.setAlignment(Qt.AlignCenter)
                    self.time_label.setContentsMargins(25, 25, 25, 25)
                    self.layout_actions.addWidget(self.time_label)
            else:
                minutes, seconds = divmod(self.exerciseTime, 60)
                centiseconds = int((self.exerciseTime - int(self.exerciseTime)) * 100)
                self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
        else:
            self.time_label.hide()
            self.time_label = QLabel("00:00:00")
            self.time_label.setProperty("class", "")
            self.time_label.setAlignment(Qt.AlignCenter)
            self.time_label.setContentsMargins(25, 25, 25, 25)
            self.layout_actions.addWidget(self.time_label)
            self.startTime = None

    def startExecution(self):
        """
            Modifies:   self.execution
                        self.startTime
                        self.play_button
                        self.stop_button
                        self.save_button
            Effects:    Starts the recording.
        """
        # get mtwRecord params
        self.modality = self.getMusicModality()
        self.selectedMusic = self.getMusicPath()
        self.selectedExercise = self.getExerciseNumber()
        self.calculateBpm = True if self.modality == 0 else False

        # set the execution state on false
        self.execution = False

        # disable all buttons and selects except stop button
        self.changeEnabledAll()

        # Execute mtw_run in a different thread
        analyze = False if self.modality == 1 else True
        
        self.record_thread = MtwThread(Duration=self.exerciseTime, MusicSamplesPath=self.selectedMusic, Exercise=self.selectedExercise, Analyze=analyze, setStart = self.emit_startSignal, CalculateBpm=self.calculateBpm, shared_data = self.shared_data)
        self.record_thread.daemon = True
        self.record_thread.start()

        # connection message
        self.connection_msg = QMessageBox()
        self.connection_msg.setIcon(QMessageBox.Information)
        self.connection_msg.setWindowTitle("Connection...")
        self.connection_msg.setText("Please wait. We are trying to connect with the sensors...")
        self.connection_msg.setStandardButtons(QMessageBox.NoButton)
        self.connection_msg.show()

        # create execuiton timer
        self.check_mtw_run_timer = QTimer(self)
        self.check_mtw_run_timer.timeout.connect(self.check_mtw_run_status)
        self.check_mtw_run_timer.start(50)

    def check_mtw_run_status(self):
        """
            Modifies:   self.execution
                        self.startTime
                        self
            Effects:    Checks the status of the mtw_run thread.
                        if is not alive executes saveRecording
        """
        if not self.record_thread.is_alive():
            print("closed thread")

            self.playingMusic = False   # stops music
            self.execution = False
            self.startTime = None
            self.changeEnabledAll()
            self.check_mtw_run_timer.stop()

            result= self.record_thread.get_results()
            if result is not None:

                if isinstance(result, Exception):
                    # close connection msg
                    self.connection_msg.reject()
                    self.setSaved(None)
                    
                    error_msg = QMessageBox()
                    error_msg.setIcon(QMessageBox.Warning)  # Icona di avviso
                    error_msg.setWindowTitle("Error")
                    msg = (str(result)).replace("Aborting.", "") if "Aborting." in str(result) else str(result)
                    error_msg.setText(msg + " Do you want to try again?")
                    error_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    response = error_msg.exec_()

                    if response == QMessageBox.Yes:
                        self.startExecution()
                else:
                    self.signals, self.Fs, self.bpm = result
                    if self.setBpm and self.bpm != False:
                        print("bpm: " + str(self.bpm))
                        self.setBpm(self.bpm) 
                    elif self.setBpm and self.bpm == False:
                        print("Bpm Estimation Failed")

                    self.saveRecording()   
            else:
                self.setSaved(None) # clean plotter

    def emit_startSignal(self):
        self.thread_signal_start.emit()


    def setStart(self):
        """
            Modifies:   self.startTime
                        self.execution
            Effects:    Sets the start time of the recording.
                        It closes the connection message.
                        If music modality is setted on Music it starts to play the music in a different thread.
        """

        self.startTime = time.time()
        self.execution = True

        print("msg closing..")
        self.connection_msg.reject()

        self.plotter_start()
        beepPath = "../sonicwalk/audio_samples/beep.wav"
        beep = pygame.mixer.Sound(beepPath)
        beep.play()

        if self.modality == 1:

            try:
                # Load and sort music samples
                files = [os.path.join(self.selectedMusic, f) for f in os.listdir(self.selectedMusic) 
                        if os.path.isfile(os.path.join(self.selectedMusic, f))]
                files.sort()
                self.music_samples = []
                print("loading wave samples...")
                for f in files:
                    if f.lower().endswith((".wav", ".mp3")):
                        self.music_samples.append(pygame.mixer.Sound(f))

                if not self.music_samples:
                    raise Exception("No music samples")

                music_thread = threading.Thread(target=self._play_music)
                music_thread.setDaemon(True)
                music_thread.start()

            except Exception as e:
                print("An error occurred while loading music samples:", e)
                self.thread_signal.emit()

    def stop_by_musicError(self):
        self.stopExecution()
        sample_error_msg = QMessageBox()
        sample_error_msg.setIcon(QMessageBox.Critical)
        sample_error_msg.setWindowTitle("Error")
        sample_error_msg.setText("Failed to load music samples. Please ensure that the provided path is correct and that the files are in either WAV or MP3 format.")
        sample_error_msg.setStandardButtons(QMessageBox.Ok)
        sample_error_msg.exec_()

    def _play_music(self):
        bpm = self.getBpm()
        beats_per_second = bpm / 60.0
        beat_duration = 1.0 / beats_per_second

        # play
        self.playingMusic = True
        current_sample_index = 0
        while self.playingMusic:
            sample = self.music_samples[current_sample_index]
            sample.play()
            pygame.time.wait(int(beat_duration * 1000))
            current_sample_index = (current_sample_index + 1) % len(self.music_samples)

    def stopExecution(self):
        """
            Modifies:   self.execution
                        self.startTime
            Effects:    Stops the recording.
        """
        if self.execution:
            # per implementarla bisogna rivedere la logica del codice di sonicwalk
            self.check_mtw_run_timer.stop()
            self.execution = False
            self.startTime = None
            self.playingMusic = False
            self.changeEnabledAll()
            ## interruzione della registrazione (sicura), deve rimettere i sensori nella modalità corretta
            self.record_thread.interrupt_recording(lambda: self.setSaved(None))

    
    def saveRecording(self):
        """
        Modifies:   Creates and saves a numpy file with the recording data (signal and Fs) in the folder of specified patient.

        Effects:    Prompts the user to confirm before saving the recording.
                    Saves the recording data in a numpy file with a unique filename in the patient folder.
                    Displays a success message upon successful saving.
        """

        # Prompts the user to confirm before saving the recording
        confirm_msg = QMessageBox()
        confirm_msg.setIcon(QMessageBox.Question)
        confirm_msg.setWindowTitle("Confirm Save")
        confirm_msg.setText("Do you want to save the recording?")
        confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # get the response from user
        response = confirm_msg.exec_()


        # if user says yes, save the recording
        if response == QMessageBox.Yes:

            dialog = QDialog()
            dialog.setWindowTitle("Exercise Information")

            layout = QVBoxLayout()

            # SpinBox for session number
            session_label = QLabel("Session Number of today's date:")
            session_spinbox = QSpinBox()
            session_spinbox.setMinimum(1)
            session_spinbox.setValue(1)

            layout.addWidget(session_label)
            layout.addWidget(session_spinbox)

            # LineEdit for optional comment
            comment_label = QLabel("Exercise Comment (optional):")
            comment_textedit = QTextEdit()

            layout.addWidget(comment_label)
            layout.addWidget(comment_textedit)

            # Button box
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            layout.addWidget(button_box)
            dialog.setLayout(layout)

            if dialog.exec_() == QDialog.Accepted:
                session_number = session_spinbox.value()
                comment = comment_textedit.toPlainText()
                print("comment_text: ", comment)
            else: 
                self.setSaved(None)
                return

            self.patient_info_data = self.getPatient()
            try:
                if self.signals is None or self.Fs is None:
                    raise ValueError("No signals to save")

                # find current patient ID
                patient_id = self.patient_info_data[2][1]

                # verify if id is Empty
                if patient_id.strip() == "":
                    raise ValueError("Patient ID is empty")
                
                if self.selectedExercise == 0:
                    exName = "walk" 
                elif self.selectedExercise == 1:
                    exName = "marchHight"
                elif self.selectedExercise == 2:
                    exName = "marchButt"
                elif self.selectedExercise == 3:
                    exName = "swing"
                elif self.selectedExercise == 4:
                    exName = "doubleStep"

                if self.modality == 0:
                    musicMode ="noMusic"
                elif self.modality == 1:
                    musicMode ="music"
                elif self.modality == 2:
                    musicMode ="realTime"

                # Creates a unique filename for the recording
                today_date = datetime.today().strftime('%Y-%m-%d')
                parent_dir = os.path.dirname(os.path.abspath(__file__))
                directory_path = os.path.join(parent_dir.replace("frames",""), f"data/archive/{patient_id}")
                os.makedirs(directory_path, exist_ok=True)  # Crea la directory se non esiste
                session_number_str = str(session_number).zfill(2)
                session_dir = os.path.join(directory_path, f"{today_date}_session_{session_number_str}")
                os.makedirs(session_dir, exist_ok=True)
                current_time = datetime.now().strftime("%H%M%S")
                filename = os.path.join(session_dir, f"{exName}_{musicMode}_{patient_id}_session_{session_number_str}_{today_date}_{current_time}.npy")

                # save datas into the file npy
                np.save(filename, {"signals": self.signals, "Fs": self.Fs, "comment": comment})

                self.setSaved(self.signals)

                # Confirm message
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
                # Handle exceptions if unable to save the file or the patient ID is empty
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setWindowTitle("Error")
                error_msg.setText(f"An error occurred while saving the recording: {str(e)}")
                error_msg.setStandardButtons(QMessageBox.Ok)
                
                ok_button = error_msg.button(QMessageBox.Ok)
                ok_button.setMinimumWidth(100)
                ok_button.setMinimumHeight(40)
                error_msg.exec_()

        else: self.setSaved(None)





        