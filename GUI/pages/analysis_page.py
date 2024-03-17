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
from theme_manager import ThemeManager

class AnalysisPage(QFrame):
    def __init__(self):
        super().__init__()
        # codice...

        self.selectedExercise = 1
        self.modality = 1
        self.selectedMusic = 1

        self.execution = False
        self.startTime = None

        self.theme_manager = ThemeManager()

        self.setup_ui()

    def setup_ui(self):

        self.currentThemeCss, self.icon_path = self.theme_manager.getTheme()

        # set a time controller
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(1000)  # Aggiorna ogni secondo

        # Struttura pagina:

        self.frame = QFrame()
        self.frame1 = QFrame()
        self.frame2 = QFrame()
        self.patient_frame = QFrame()        
        self.frame_a = QFrame()
        self.frame_b = QFrame()
        self.frameRecording = QFrame()

        self.layout = QVBoxLayout(self.frame)
        self.layout1 = QHBoxLayout(self.frame1)
        self.layout2 = QHBoxLayout(self.frame2)
        self.layout_patient_frame = QVBoxLayout(self.patient_frame)
        self.layout_a = QVBoxLayout(self.frame_a)
        self.layout_b = QVBoxLayout(self.frame_b)
        self.layoutRecording = QHBoxLayout(self.frameRecording)

        self.layout_patient_frame.addWidget(QLabel("Nome: Mario"))
        self.layout_patient_frame.addWidget(QLabel("Cognome: Rossi"))
        self.layout_patient_frame.addWidget(QLabel("ID: 12345"))
        self.layout_patient_frame.addWidget(QLabel("Gruppo: Parkingson"))
        self.layout_patient_frame.addWidget(QLabel("Ospedale: Milano"))
        self.button_seleziona_paziente = QPushButton("Seleziona Paziente")

        self.layout_patient_frame.addWidget(self.button_seleziona_paziente)

                # Chiamiamo la funzione createPlotter e aggiungiamo il plotter al layout di frame1
        self.plotter_widget = self.createPlotter()

        self.layout1.addWidget(self.patient_frame, 2)
        self.layout1.addWidget(self.plotter_widget, 6)
        self.layout1.setContentsMargins(10, 18, 5, 5)

        localcss =  """
            QPushButton {
                border: none;
                background-color: rgba(150, 150, 150, 10%);
                border-radius: 40px;
                text-align: center;
                padding-left: 0px
            }
            QPushButton:hover {
                background-color: rgba(108, 60, 229, 30%); /* Colore di sfondo leggermente trasparente su hover */
            }
            """

        # Crea e aggiungi i pulsanti a frame_a
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(self.icon_path + "play.svg"))
        self.play_button.clicked.connect(self.startExecution)
        self.play_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.play_button.setIconSize(QSize(25, 25)) 
        self.play_button.setStyleSheet(localcss)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("icons/square.svg"))
        self.stop_button.clicked.connect(self.stopExecution)
        self.stop_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.stop_button.setIconSize(QSize(25, 25)) 
        self.stop_button.setStyleSheet(localcss)

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(self.icon_path + "save.svg"))
        self.save_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.save_button.setIconSize(QSize(25, 25)) 
        self.save_button.setStyleSheet(localcss)

        self.layoutRecording.addWidget(self.stop_button)
        self.layoutRecording.addWidget(self.play_button)
        self.layoutRecording.addWidget(self.save_button)

        self.layout_a.addWidget(self.frameRecording)


        # Aggiungi un widget QLabel per visualizzare il tempo
        self.time_label = QLabel("00:00:00")
        self.layout_a.addWidget(self.time_label)
        self.time_label.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Selected Exercise:", self)
        self.layout_b.addWidget(self.label)

        # Crea un selettore per il tipo di esercizio
        self.exercise_selector = QComboBox()
        self.exercise_selector.addItems(["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])
        self.layout_b.addWidget(self.exercise_selector)
        self.exercise_selector.currentTextChanged.connect(lambda text_value=self.exercise_selector.currentText: self.selectExercise(text_value))


        # Crea e aggiungi i pulsanti per la modalità di esercizio
        self.music_buttons_frame = QFrame()
        self.music_buttons_layout = QHBoxLayout(self.music_buttons_frame)
        self.music_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.noMusic_button = QPushButton("No Music")
        self.noMusic_button.clicked.connect(lambda: setattr(self, 'modality', 1))

        self.music_button = QPushButton("Music")
        self.music_button.clicked.connect(lambda: setattr(self, 'modality', 2))

        self.realTimeMusic_button = QPushButton("Real Time Music")
        self.realTimeMusic_button.clicked.connect(lambda: setattr(self, 'modality', 3))

        self.music_buttons_layout.addWidget(self.noMusic_button)
        self.music_buttons_layout.addWidget(self.music_button)
        self.music_buttons_layout.addWidget(self.realTimeMusic_button)

        self.layout_b.addWidget(self.music_buttons_frame)

        self.label2 = QLabel("Selected Music:", self)
        self.layout_b.addWidget(self.label2)
        # Crea un selettore per il tipo di musica
        self.music_selector = QComboBox()
        self.music_selector.addItems(["Music 1", "Music 2"])     # i nomi devono essere recuperati dinamicamente dalla cartella delle musiche
        self.layout_b.addWidget(self.music_selector)
        self.music_selector.currentTextChanged.connect(lambda text_value=self.music_selector.currentText: self.selectExercise(text_value))

        # Aggiungi i due frame a layout2
        self.layout2.addWidget(self.frame_b)
        self.layout2.addWidget(self.frame_a)

        # Imposta la policy di espansione
        self.layout.addWidget(self.frame1, 2)
        self.layout.addWidget(self.frame2, 1)

        # Imposta la policy di espansione
        self.layout2.setStretch(0, 2)
        self.layout2.setStretch(1, 2)


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



    def createPlotter(self):
        # Crea una figura di esempio
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

        # Crea un canvas per il plotter e collega la figura ad esso
        canvas = FigureCanvas(fig)

        return canvas
    
    def get_frame(self):
        return self.frame