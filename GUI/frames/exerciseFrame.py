import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt 
import sys

sys.path.append("../")

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
            self.musicModality = 2
            self.light = light
            self.bpm = 60
            self.firstRendering = True

            # set self layout
            self.layout_selection = QVBoxLayout(self)
            self.layout_selection.setContentsMargins(30, 30, 30, 30)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored) 

            # exercise selection
            label_selected_exercise = QLabel("Selected Exercise:")
            self.layout_selection.addWidget(label_selected_exercise)
            self.exercise_selector = QComboBox()
            self.exercise_selector.addItems(["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])
            self.exercise_selector.currentTextChanged.connect(self.selectExercise)
            self.layout_selection.addWidget(self.exercise_selector)

            # music selection
            self.label_selected_music = QLabel("Selected Music:")
            self.layout_selection.addWidget(self.label_selected_music)
            self.musicOptions = self._findMusicOptions()
            self.music_selector = QComboBox()
            self.music_selector.addItems(self.musicOptions if self.musicOptions is not None else [""])
            self.music_selector.currentTextChanged.connect(self.selectMusic)
            self.layout_selection.addWidget(self.music_selector)

            # define a frame for buttons
            self.music_buttons_frame = QWidget()
            self.music_buttons_layout = QHBoxLayout(self.music_buttons_frame)
            self.music_buttons_layout.setContentsMargins(0, 0, 0, 0)
            self.layout_selection.addWidget(self.music_buttons_frame)

            self.noMusic_button = QPushButton("No Music")
            self.noMusic_button.setCheckable(True)
            self.noMusic_button.clicked.connect(lambda: self._buttonClick(0))

            self.music_button = QPushButton("Music")
            self.music_button.setCheckable(True)
            self.music_button.clicked.connect(lambda: self._buttonClick(1))

            self.realTimeMusic_button = QPushButton("Real Time")
            self.realTimeMusic_button.setCheckable(True)
            self.realTimeMusic_button.clicked.connect(lambda: self._buttonClick(2))

            # Slider for BPM
            self.slider_label = QLabel("Velocity:")
            self.slider_frame = QWidget()
            self.bpm_slider = QSlider(Qt.Horizontal)  
            self.bpm_slider.setRange(1, 150) 
            self.bpm_slider.setValue(60)  
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
            with open('data/settings.json', 'r') as f:
                settings = json.load(f)
            music_directories = settings.get('music_directories', [])
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
        print(text)
        if text == "Walk": self.selectedExercise = 0 
        elif text == "March in place (Hight Knees)": self.selectedExercise = 1
        elif text == "March in place (Butt Kicks)": self.selectedExercise = 1
        elif text == "Swing": self.selectedExercise = 3
        elif text == "Double Step": self.selectedExercise = 4

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
    
    def getBpm(self):
        """
        EFFECTS:    
            - Rerurns selected bpm
        """
        return self.bpm
    
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