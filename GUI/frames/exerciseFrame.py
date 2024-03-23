from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt 
import sys

sys.path.append("../")

from components.customSelect import CustomSelect
from components.customButton import CustomButton

class ExerciseFrame(QFrame):
    def __init__(self, light = True):
            super().__init__()
            """
            Requires:
                - light: a boolean indicating light or dark theme
            Modifies:
                - Initializes self attributes, customSelect, customButtons and labels
            Effects:
                - Initializes a custom frame for exercise selection.
            """

            # initialize attributes
            self.selectedMusic = "../sonicwalk/audio_samples/cammino_1_fase_2" 
            self.selectedExercise = 0
                # 0 --> walking
                # 1 --> Walking in place (High Knees, Butt Kicks)
                # 2 --> Walking in place (High Knees con sensori sulle cosce)
                # 3 --> Swing
                # 4 --> Double Step
            self.musicModality = 2
            self.light = light
            self.bpm = 75

            # theme style
            self.lightTheme = "background-color: #B6C2CF; border-top-left-radius: 15px; border-top-right-radius: 15px; color: black;"
            self.darkTheme = "background-color: #282E33; border-top-left-radius: 15px; border-top-right-radius: 15px; color: white;"

            # set self layout
            self.layout_selection = QVBoxLayout(self)
            self.layout_selection.setContentsMargins(30, 30, 30, 30)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored) 

            # exercise custom selection
            label_selected_exercise = QLabel("Selected Exercise:")
            label_selected_exercise.setFont(QFont("sans-serif", 11))
            self.layout_selection.addWidget(label_selected_exercise)
            self.exercise_selector = CustomSelect(light=self.light, options=["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])
            self.exercise_selector.currentTextChanged.connect(self.selectExercise)
            self.layout_selection.addWidget(self.exercise_selector)

            # music custom selection
            self.label_selected_music = QLabel("Selected Music:")
            self.label_selected_music.setFont(QFont("sans-serif", 11))
            self.layout_selection.addWidget(self.label_selected_music)
            self.musicOptions = self._findMusicOptions()
            self.music_selector = CustomSelect(light=self.light, options=self.musicOptions if self.musicOptions is not None else [""])
            self.music_selector.currentTextChanged.connect(self.selectMusic)
            self.layout_selection.addWidget(self.music_selector)

            # define a frame for buttons
            self.music_buttons_frame = QFrame()
            self.music_buttons_layout = QHBoxLayout(self.music_buttons_frame)
            self.music_buttons_layout.setContentsMargins(0, 0, 0, 0)
            self.layout_selection.addWidget(self.music_buttons_frame)

            # define custom buttons
            self.noMusic_button = CustomButton(light=self.light, text="No Music", stayActive = True, onClickDeactivate = False)
            self.noMusic_button.onClick(lambda: self._buttonClick(0))
            self.music_button = CustomButton(light=self.light, text="Music", stayActive = True, onClickDeactivate = False)
            self.music_button.onClick(lambda: self._buttonClick(1))
            self.realTimeMusic_button = CustomButton(light=self.light, text="Real Time", stayActive = True, onClickDeactivate = False)
            self.realTimeMusic_button.onClick(lambda: self._buttonClick(2))

            # Slider for BPM
            self.slider_label = QLabel("Velocity:")
            self.slider_label.setFont(QFont("sans-serif", 11))
            
            self.slider_frame = QFrame()
            self.bpm_slider = QSlider(Qt.Horizontal)  
            self.bpm_slider.setRange(0, 150) 
            self.bpm_slider.setValue(75)  
            self.bpm_slider.setTickInterval(5)  
            self.bpm_slider.setStyleSheet(
                "QSlider::groove:horizontal { height: 10px; background-color: gray; border-radius: 5px; }"
                "QSlider::handle:horizontal { background-color: white; border: 1px solid #4A708B; width: 18px; margin: -2px 0; border-radius: 8px; }"
                "QSlider::add-page:horizontal { background-color: lightgray; border-radius: 5px; }"
                "QSlider::sub-page:horizontal { background-color: #B99AFF; border-radius: 5px; }"
            )
            self.bpm_slider.valueChanged.connect(self.setBpm)
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

            # set style
            self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

            # call default button
            self.music_button.clickCall()


    def setBpm(self):
        """
            Modifies:   self.bpm
            Effects:    updates bpm value and label
        """
        # update bpm value
        self.bpm = self.bpm_slider.value()
        self.bpm_value_label.setText("  "+str(self.bpm)+" bpm")

    def _findMusicOptions(self):
        # da definire
          
          return ["Music 1"]
    
    def selectMusic(self, text):
        """
            Requires:   text: a string representing the selected music option
            Effects:    Sets the selected music path based on the chosen option.
        """
        print(text)
        if text == "Music 1": self.selectedMusic = "../sonicwalk/audio_samples/cammino_1_fase_2" 
        # elif text == "Music 2": self.selectedMusic = "../sonicwalk/audio_samples/..."
        # da definire in base a come e dove si trova la musica

    def selectExercise(self, text):
        """
            Requires:   text: a string representing the selected exercise option from (Walk, March in place (Hight Knees), March in place (Butt Kicks), Swing, Double Step)
            Effects:    Sets the selected exercise number based on the chosen option.
        """
        print(text)
        if text == "Walk": self.selectedExercise = 0 
        elif text == "March in place (Hight Knees)": self.selectedExercise = 1
        elif text == "March in place (Butt Kicks)": self.selectedExercise = 1
        elif text == "Swing": self.selectedExercise = 3
        elif text == "Double Step": self.selectedExercise = 4

    def _buttonClick(self, number):
        """"
            Requires:   number must be a number from 0 to 2 that represents the modality selected
                        button must be valid button
        """
        self.noMusic_button.deselectButton()
        self.music_button.deselectButton()
        self.realTimeMusic_button.deselectButton()

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

    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
                        all custom elements
            Effects:    Switches between light and dark themes.
        """
        self.light = not self.light
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        
        self.music_selector.toggleTheme()
        self.exercise_selector.toggleTheme()
        self.realTimeMusic_button.toggleTheme()
        self.noMusic_button.toggleTheme()
        self.music_button.toggleTheme()

    def getMusicModality(self):
        """
            Effects:    Rerurns selected music modality
        """
        return self.musicModality
    
    def getMusicPath(self):
        """
            Effects:    Rerurns selected music path
        """
        return self.selectedMusic
    
    def getExerciseNumber(self):
        """
            Effects:    Rerurns selected exercise number
        """
        return self.selectedExercise
    
    def getBpm(self):
        """
            Effects:    Rerurns selected bpm
        """
        return self.bpm
