import threading
import time
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import os
import sys
from datetime import datetime
import numpy as np
import simpleaudio as sa    # simpleaudio has problems with the python threading GIL 
import pygame

sys.path.append("../")

from components.recButton import RecButton
from mtw_run import MtwThread

class RecordingFrame(QFrame):
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

        # initialize attributes
        self.shared_data = shared_data
        self.plotter_start = plotter_start
        self.setSaved = setSaved
        self.exerciseTime = 11 #90
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
        self.blackIcons = "icons/black"
        self.whiteIcons = "icons/white"

        self.playAbilited = True    # state of the play button
        self.execution = False      # state of the execution
        self.startTime = None       # start execution time
        self.playingMusic = False

        # sinals for multithreading
        self.connection_msg = None
        self.signals = None
        self.Fs = None

        # init pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        # create a timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(50)

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
        """
            Modifies:   self.light
            Effects:    Toggles the theme of the recording frame between light and dark mode.
        """
        self.light = not self.light
        self.time_label.setStyleSheet("color: black;" if self.light else "color: white;")
        self.play_button.toggleTheme()
        self.stop_button.toggleTheme()
        self.save_button.toggleTheme()

    def enablePlayButton(self):
        """
            Modifies:   self.playAbilited
            Effects:    Enables the play button.
        """
        if not self.playAbilited:
            self.playAbilited = True
            self.play_button.setEnabled(True)

    def disablePlayButton(self):
        """
            Modifies:   self.playAbilited
            Effects:    Disables the play button.
        """
        if self.playAbilited:
            self.playAbilited = False
            self.play_button.setEnabled(False)

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
            else:
                minutes, seconds = divmod(self.exerciseTime, 60)
                centiseconds = int((self.exerciseTime - int(self.exerciseTime)) * 100)
                self.time_label.setText("{:02}:{:02}.{:02}".format(int(minutes), int(seconds), centiseconds))
        else:
            self.time_label.setText("00:00.00")
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
        self.record_thread = MtwThread(Duration=self.exerciseTime, MusicSamplesPath=self.selectedMusic, Exercise=self.selectedExercise, Analyze=analyze, setStart = self.setStart, CalculateBpm=self.calculateBpm, shared_data = self.shared_data)
        self.record_thread.daemon = True
        try:
            self.record_thread.start()
        except Exception as e:
            self.setSaved(None)
            # have to return only some errors in a message

        # open connection message

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
        # print("thread alive")
        if not self.record_thread.is_alive():
            print("closed thread")

            self.playingMusic = False   # stops music
            self.execution = False
            self.startTime = None
            self.changeEnabledAll()
            self.check_mtw_run_timer.stop()

            result= self.record_thread.get_results()
            if result is not None:
                self.signals, self.Fs, self.bpm = result
                if self.setBpm and self.bpm != False:
                    print("bpm: " + str(self.bpm))
                    self.setBpm(self.bpm) 
                elif self.setBpm and self.bpm == False:
                    print("Bpm Estimation Failed")

                self.saveRecording()   
            else:
                self.setSaved(None) # clean plotter

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

        # close connection message

        if self.modality == 1:
            music_thread = threading.Thread(target=self._play_music)
            music_thread.start()

        self.plotter_start()
        print("after plotter start")
        beepPath = "../sonicwalk/audio_samples/beep.wav"
        beep = pygame.mixer.Sound(beepPath)
        beep.play()

    def _play_music(self):
        bpm = self.getBpm()
        beats_per_second = bpm / 60.0  # Convert BPM to beats per second
        beat_duration = 1.0 / beats_per_second  # Duration of each beat in seconds

        # Load and sort music samples
        files = [os.path.join(self.selectedMusic, f) for f in os.listdir(self.selectedMusic) 
                if os.path.isfile(os.path.join(self.selectedMusic, f))]
        files.sort() #sort filenames in order
        music_samples = []
        print("loading wave samples...")
        for f in files:
            if f.lower().endswith(".wav"):
                music_samples.append(pygame.mixer.Sound(f))

        # play
        self.playingMusic = True
        current_sample_index = 0
        while self.playingMusic:
            sample = music_samples[current_sample_index]
            sample.play()
            pygame.time.wait(int(beat_duration * 1000))  # Convert seconds to milliseconds
            current_sample_index = (current_sample_index + 1) % len(music_samples)

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
                current_time = datetime.now().strftime("%H%M%S")
                filename = os.path.join(directory_path, f"{today_date}_{current_time}_{patient_id}_{exName}_{musicMode}.npy")

                # save datas into the file npy
                np.save(filename, {"signals": self.signals, "Fs": self.Fs})

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



        