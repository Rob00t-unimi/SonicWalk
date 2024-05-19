import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt 
import sys
import os

class ExerciseFrame(QFrame):
    """
    Custom frame for the exercise selection
    """
    def __init__(self, light = True):
            """
            REQUIRES:
                - light: a boolean indicating light or dark theme
                
            MODIFIES:
                - self

            EFFECTS:
                - Initializes a custom frame for exercise selection.
            """
            super().__init__()

            folder_name = os.path.basename(os.getcwd())
            self.settings_path = 'data/settings.json' if folder_name == "GUI" else 'GUI/data/settings.json'
            self.dataset_path = 'data/dataset.json' if folder_name == "GUI" else 'GUI/data/dataset.json'

            # for py installer only:
            # self.settings_path = '_internal/data/settings.json'
            # self.dataset_path = '_internal/data/dataset.json'

            # initialize attributes
            self.selectedMusic = None 
            self.MusicPaths = None
            self.MusicNames = None
            self.selectedExercise = 0
                # 0 --> walking
                # 1 --> Walking in place (High Knees, Butt Kicks)
                # 2 --> Walking in place (High Knees con sensori sulle cosce)
                # 3 --> Swing
                # 4 --> Double Step
            self.selected_front_leg = True # True if right leg, False if left leg
            self.musicModality = 0
            self.light = light
            self.bpm = 60
            self.sensibility = 3
            self.firstRendering = True
            self.patient_info = None

            # Main layout
            self.layout = QVBoxLayout(self)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored) 

            # Scroll area
            self.scroll_area = QScrollArea()
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)     # Enable vertical scrolling as needed
            self.scroll_area.setWidgetResizable(True)

            # Container widget for the scroll area
            self.scroll_content = QWidget()
            self.scroll_area.setWidget(self.scroll_content)

            # Layout for the content inside the scroll area
            self.layout_selection = QVBoxLayout(self.scroll_content)

            # Add scroll area to the main layout
            self.layout.addWidget(self.scroll_area)

            # exercise selection
            label_selected_exercise = QLabel("Selected Exercise:")
            self.layout_selection.addWidget(label_selected_exercise)
            self.exercise_selector = QComboBox()
            self.exercise_selector.addItems(["Walk", "March in place", "Swing - Right leg front", "Swing - Left leg front", "Double Step - Right leg front", "Double Step - Left leg front"])
            self.exercise_selector.currentTextChanged.connect(self.selectExercise)
            self.layout_selection.addWidget(self.exercise_selector)

            # Slider for Sensibility
            self.slider2_label = QLabel("Sensibility:")
            self.slider2_frame = QWidget()
            self.sensibility_slider = QSlider(Qt.Horizontal)  
            self.sensibility_slider.setRange(1, 5) 
            self.sensibility_slider.setValue(self.sensibility)  
            self.sensibility_slider.setTickInterval(1)  
            self.sensibility_slider.valueChanged.connect(self._setSensibility)
            self.sensibility_value_label = QLabel("  " + str(self.sensibility_slider.value()))

            frame2_layout = QHBoxLayout()
            frame2_layout.addWidget(self.sensibility_slider)
            frame2_layout.addWidget(self.sensibility_value_label)
            self.slider2_frame.setLayout(frame2_layout) 

            self.layout_selection.addWidget(self.slider2_label)
            self.layout_selection.addWidget(self.slider2_frame)

            # define a frame for buttons
            self.music_buttons_frame = QWidget()
            self.music_buttons_layout = QHBoxLayout(self.music_buttons_frame)
            self.music_buttons_layout.setContentsMargins(0, 0, 0, 0)
            self.layout_selection.addWidget(self.music_buttons_frame)

            self.noMusic_button = QPushButton("No Music")
            self.noMusic_button.setCheckable(True)
            self.noMusic_button.clicked.connect(lambda: self._buttonClick(0))

            self.music_button = QPushButton("Pre-Recorded")
            self.music_button.setCheckable(True)
            self.music_button.clicked.connect(lambda: self._buttonClick(1))

            self.realTimeMusic_button = QPushButton("Real Time")
            self.realTimeMusic_button.setCheckable(True)
            self.realTimeMusic_button.clicked.connect(lambda: self._buttonClick(2))

            # music selection
            self.label_selected_music = QLabel("Selected Music:")
            self.layout_selection.addWidget(self.label_selected_music)
            self.musicOptions = self._findMusicOptions()
            self.music_selector = QComboBox()
            self.music_selector.addItems(self.musicOptions if self.musicOptions is not None else [""])
            self.music_selector.currentTextChanged.connect(self.selectMusic)
            self.layout_selection.addWidget(self.music_selector)

            # Slider for BPM
            self.slider_label = QLabel("Velocity:")
            self.slider_frame = QWidget()
            self.bpm_slider = QSlider(Qt.Horizontal)  
            self.bpm_slider.setRange(1, 150) 
            self.bpm_slider.setValue(self.bpm)  
            self.bpm_slider.setTickInterval(5)  
            self.bpm_slider.valueChanged.connect(self._setBpm)
            self.bpm_value_label = QLabel("  "+str(self.bpm_slider.value())+" bpm")

            frame_layout = QHBoxLayout()
            frame_layout.addWidget(self.bpm_slider)
            frame_layout.addWidget(self.bpm_value_label)
            self.slider_frame.setLayout(frame_layout) 

            # Add the frame to the main layout
            self.music_buttons_layout.addWidget(self.noMusic_button)
            self.music_buttons_layout.addWidget(self.music_button)
            self.music_buttons_layout.addWidget(self.realTimeMusic_button)
            self.layout_selection.addWidget(self.slider_label)
            self.layout_selection.addWidget(self.slider_frame)

            # call default button
            self.noMusic_button.setChecked(True)
            if len(self.MusicNames)>0:
                self.selectMusic(self.MusicNames[0])

            self.noMusic_button.click()

    def setPatientId(self, patientId):
        """
            MODIFIES:   
                - self.patient_info

            EFFECTS:    
                - updates patient_info
        """
        if patientId is None: 
            self.patient_info = None
            self.sensibility = 3
            # self.bpm = 60
            self.sensibility_slider.setValue(self.sensibility) 
        else:
            self.patient_id = patientId
            try:
                with open(self.dataset_path, 'r') as file:
                    data = json.load(file)

                for patient in data:
                    if patient["ID"] == patientId:
                        self.patient_info = patient
                        self.load_sensibility()
                        # self.bpm = patient[exercise + "_bpm"]
                        break
            except:
                print("Error: impossible to load patient data")

        # self.bpm_slider.setValue(self.bpm)

    def load_sensibility(self):
        if self.selectedExercise == 0: exercise = "walk" 
        elif self.selectedExercise == 1: exercise = "march"
        elif self.selectedExercise == 3: exercise = "swing"
        elif self.selectedExercise == 4: exercise = "double_step"

        self.sensibility = self.patient_info[exercise + "_sensibility"]
        self.sensibility_slider.setValue(self.sensibility) 

    def update_patient_sensibility(self):
        if self.patient_info is not None:
            if self.selectedExercise == 0: exercise = "walk" 
            elif self.selectedExercise == 1: exercise = "march"
            elif self.selectedExercise == 3: exercise = "swing"
            elif self.selectedExercise == 4: exercise = "double_step"
            self.patient_info[exercise + "_sensibility"] = self.sensibility

            try:
                with open(self.dataset_path, 'r') as file:
                    data = json.load(file)
                for existing_patient in data:
                    if existing_patient["ID"] == self.patient_info["ID"]:
                        existing_patient.update(self.patient_info)
                        # print(self.patient_info)
                        break
            except:
                print("Error: impossible to load patient data")
            try:
                with open(self.dataset_path, 'w') as file:
                    json.dump(data, file)
            except Exception as e:
                print("Error: impossible to save the sensibility")


    def _setSensibility(self):
        """
            MODIFIES:   
                - self.sensibility

            EFFECTS:    
                - updates sensibility value and label
        """
        self.sensibility = self.sensibility_slider.value()
        self.sensibility_value_label.setText("  "+str(self.sensibility))
        self.update_patient_sensibility()

    def _setBpm(self):
        """
            MODIFIES:   
                - self.bpm

            EFFECTS:    
                - updates bpm value and label
        """
        # update bpm value
        self.bpm = self.bpm_slider.value()
        self.bpm_value_label.setText("  "+str(self.bpm)+" bpm")

    def setBpm(self, bpm):
        """
            MODIFIES:   
                - self.bpm

            EFFECTS:    
                - sets selected bpm
        """
        if bpm == False: return
        self.bpm = bpm
        self.bpm_value_label.setText("  "+str(self.bpm)+" bpm")
        self.bpm_slider.setValue(self.bpm)
        return

    def _findMusicOptions(self):
        """
            MODIFIES:   
                - self.MusicPaths
                - self.MusicNames

            EFFECTS:    
                - load music paths and names from settings.json
        """
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
            music_directories = settings.get('music_directories', [])
            for i, path in enumerate(music_directories):
                if not os.path.isabs(path):
                    self.this_path = os.getcwd()
                    if os.path.basename(os.getcwd()) != "GUI":
                        music_directories[i] = os.path.join(os.getcwd(), path)
                    else:
                        music_directories[i] = os.path.join(os.path.dirname(os.getcwd()), path)
            music_names = settings.get('music_names', [])
            self.MusicPaths=music_directories
            self.MusicNames=music_names
            return music_names
        except FileNotFoundError:
            print("Error: settings.json file not found.")
            return None

    def selectMusic(self, text):
        """
            REQUIRES:   
                - text (str): the selected music option

            MODIFIES:   
                - self.selectedMusic

            EFFECTS:    
                - Sets the selected music path based on the chosen option.
        """
        number = None
        for i in range(len(self.MusicNames)):
            if self.MusicNames[i] == text:
                number = i
                break
        
        if number is not None:
            self.selectedMusic = self.MusicPaths[number]
            print(text + ": " + self.selectedMusic)
        else:
            print("Error: Music option not found.")

    def selectExercise(self, text):
        """
            REQUIRES:   
                - text (str): the selected exercise option from (Walk, March in place (Hight Knees), March in place (Butt Kicks), Swing, Double Step)
           
            EFFECTS:    
                - Sets the selected exercise number based on the chosen option.
        """
        if text == "Walk": self.selectedExercise = 0 
        elif "March" in text: self.selectedExercise = 1
        elif "Swing" in text: self.selectedExercise = 3
        elif "Double Step" in text: self.selectedExercise = 4
        print(f"Selected Exercise: {text}, Exercise Number: {self.selectedExercise}")
        if "Left" in text: self.selected_front_leg=False
        elif "Right" in text: self.selected_front_leg=True
        if "leg" in text: print(f"Front Leg: {'Left' if not self.selected_front_leg else 'Right'}")

        self.load_sensibility()

    def _buttonClick(self, number):
        """"
            REQUIRES:   
                - number (int): a number from 0 to 2 that represents the modality selected
                - button (QPushButton)

            MODIFIES:
                - self

            EFFECTS:
                - Updates the selected music modality based on the provided number.
                - Updates the button states and visibility of related UI elements accordingly.
        """
        self.noMusic_button.setChecked(False)
        self.music_button.setChecked(False)
        self.realTimeMusic_button.setChecked(False)

        if number == 0: self.noMusic_button.setChecked(True)
        elif number == 1: self.music_button.setChecked(True)
        else: self.realTimeMusic_button.setChecked(True)

        self.musicModality = number
        print(str(number))

        if self.musicModality != 1:
            self.slider_label.hide()
            self.slider_frame.hide()
        else:
            self.slider_label.show()
            self.slider_frame.show()

        if self.musicModality == 0:
            self.label_selected_music.hide()
            self.music_selector.hide()
        else:
            self.label_selected_music.show()
            self.music_selector.show()

    def getMusicModality(self):
        """
        EFFECTS:    
            - Rerurns selected music modality
        """
        return self.musicModality
    
    def getMusicPath(self):
        """
        EFFECTS:    
            - Rerurns selected music path
        """
        return self.selectedMusic
    
    def getExerciseNumber(self):
        """
        EFFECTS:    
            - Rerurns selected exercise number
        """
        return self.selectedExercise
    
    def getSelectedLeg(self):
        """
        EFFECTS:    
            - Rerurns True if forward leg is the right leg, else False
        """
        return self.selected_front_leg
    
    def getBpm(self):
        """
        EFFECTS:    
            - Rerurns selected bpm
        """
        return self.bpm
    
    def getSensibility(self):
        """
        EFFECTS:    
            - Rerurns sensibility value
        """
        return self.sensibility
    
    def paintEvent(self, event):
        # when the ExerciseFrame is rendered it is executed paintEvent
        # inherit the paintEvent of the parent class
        # if is the first rendering of the ExerciseFrame executes the paintEvent of the parent class and set self.firstRendering to False
        # if is a re-rendering of the ExerciseFrame executes the paintEvent of the parent class and if the options is changed 
        # it sostitutes the music_selector 
        """
        MODIFIES:   
            - self.musicOptions
            - self.music_selector

        EFFECTS:    
            - If there's a change in music options, replaces the existing music selector widget with an updated one.
            - Executes the paintEvent of the parent class.
        """
        if not self.firstRendering:
            tmp = self.musicOptions
            self.musicOptions = self._findMusicOptions()
            if tmp != self.musicOptions:
                self.music_selector.clear()
                self.music_selector.addItems(self.musicOptions if self.musicOptions is not None else [""])
            super().paintEvent(event)

        else:
            super().paintEvent(event)
            self.firstRendering = False