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


# Aggiungere la pagina archivio con la possibilità di visualizzare e aggiungere ospedali e pazienti
# aggiungere la finestra seleziona paziente in analyzer
# ++ ogni pulsante quando premuto deve rimanere "acceso"

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sonic-Walk")
        self.resize(1000, 600)

        self.light_theme = None

        self.settings_file = "settings.json" 
        self.load_settings()

        self.menu_expanded = False

        self.selectedExercise = 1
        self.modality = 1
        self.selectedMusic = 1

        self.execution = False
        self.startTime = None

        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        self.setup_ui()

    def setup_ui(self):
        self.setup_central_widget()
        self.update_theme()
        self.buttonAnalysis_clicked()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeUpdater)
        self.timer.start(1000)  # Aggiorna ogni secondo

    def setup_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setup_side_frame()
        layout.addWidget(self.frame)

        self.setup_main_widget()  

    def setup_side_frame(self):
        self.frame = QFrame()
        self.frame.setFixedWidth(60)
        self.frame.setStyleSheet("background-color: lightgray;")
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(5, 5, 5, 5)

        self.setup_hamburger_button()
        self.setup_inner_frame1()
        self.setup_spacer()
        self.setup_inner_frame2()

    def setup_main_widget(self):
        self.mainWidget = QWidget()
        layout = QVBoxLayout(self.mainWidget)  # Imposta un QVBoxLayout per il mainWidget
        self.centralWidget().layout().addWidget(self.mainWidget)

        self.frameAnalysis = self.create_frame_analysis()  
        self.frameArchive = self.create_frame_archive()
        self.frameSettings = self.create_frame_settings()
        self.frameStatistics = self.create_frame_statistics()

    def setup_hamburger_button(self):
        self.hamburger_button = self.create_button(self.blackIconPath + "menu.svg")
        self.hamburger_button.clicked.connect(self.toggle_menu)
        self.frame_layout.addWidget(self.hamburger_button)

        line = QFrame(self.frame)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        line.setStyleSheet("color: #6c3ce5;")
        self.frame_layout.addWidget(line)

    def setup_inner_frame1(self):
        self.inner_frame1 = QFrame()
        self.inner_frame1_layout = QVBoxLayout(self.inner_frame1)
        self.inner_frame1_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_frame1_layout.setSpacing(0)

        self.buttonAnalysis = self.create_button(self.blackIconPath + "activity.svg")
        self.buttonAnalysis.clicked.connect(self.buttonAnalysis_clicked)
        self.buttonArchive = self.create_button(self.blackIconPath + "archive.svg")
        self.buttonArchive.clicked.connect(self.buttonArchive_clicked)
        self.buttonStatistics = self.create_button(self.blackIconPath + "bar-chart-2.svg")
        self.buttonStatistics.clicked.connect(self.buttonStatistics_clicked)
        self.buttonSettings = self.create_button(self.blackIconPath + "settings.svg")
        self.buttonSettings.clicked.connect(self.buttonSettings_clicked)
        self.inner_frame1_layout.addWidget(self.buttonAnalysis)
        self.inner_frame1_layout.addWidget(self.buttonArchive)
        self.inner_frame1_layout.addWidget(self.buttonStatistics)
        self.inner_frame1_layout.addWidget(self.buttonSettings)

        self.inner_frame1_layout.setStretch(0, 1)
        self.frame_layout.addWidget(self.inner_frame1)

    def setup_spacer(self):
        self.spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.frame_layout.addItem(self.spacer_item)

    def setup_inner_frame2(self):
        self.inner_frame2 = QFrame()
        self.inner_frame2_layout = QVBoxLayout(self.inner_frame2)
        self.inner_frame2_layout.setContentsMargins(0, 0, 0, 0)
 
        self.theme_button = self.create_button(self.blackIconPath + "moon.svg")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.buttonInfo = self.create_button(self.blackIconPath + "info.svg")
        self.buttonInfo.clicked.connect(self.openDocumentation)
        self.inner_frame2_layout.addWidget(self.theme_button)
        self.inner_frame2_layout.addWidget(self.buttonInfo)

        self.frame_layout.addWidget(self.inner_frame2)

    def create_button(self, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setFixedSize(50, 50)
        button.setIconSize(QSize(25, 25)) 
        button.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        return button

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.update_menu()

    def update_menu(self):
        self.frame.setFixedWidth(150 if self.menu_expanded else 60)
        button_list = [
            (self.hamburger_button, "  Menu"),
            (self.buttonAnalysis, "  Analysis"),
            (self.buttonArchive, "  Archive"),
            (self.buttonStatistics, "  Statistics"),
            (self.buttonSettings, "  Settings"),
            (self.theme_button, "  Theme"),
            (self.buttonInfo, "  Info")
        ]
        for button, text in button_list:
            button.setText(text if self.menu_expanded else "")
            button.setFixedSize(140 if self.menu_expanded else 50, 50)


    def toggle_theme(self):
        self.light_theme = not self.light_theme
        self.save_settings()
        theme_icon = self.blackIconPath + "moon.svg" if self.light_theme else self.whiteIconPath + "sun.svg"
        self.theme_button.setIcon(QIcon(theme_icon))
        self.update_theme()

    def update_theme(self):
        self.update_icon_paths()
        theme_stylesheet = "background-color: #2b2b2b; color: white;" if not self.light_theme else ""
        self.setStyleSheet(theme_stylesheet)
        frame_stylesheet = "background-color: #3a3a3a;" if not self.light_theme else "background-color: lightgray;"
        self.frame.setStyleSheet(frame_stylesheet)

        # Aggiorna l'icona del tema dopo aver aggiornato lo stile
        theme_icon_path = self.blackIconPath + "moon.svg" if self.light_theme else self.whiteIconPath + "sun.svg"
        self.theme_button.setIcon(QIcon(theme_icon_path))

    def update_icon_paths(self):
        path = self.whiteIconPath if not self.light_theme else self.blackIconPath
        self.hamburger_button.setIcon(QIcon(path + "menu.svg"))
        self.buttonAnalysis.setIcon(QIcon(path + "activity.svg"))
        self.buttonArchive.setIcon(QIcon(path + "archive.svg"))
        self.buttonStatistics.setIcon(QIcon(path + "bar-chart-2.svg"))
        self.buttonSettings.setIcon(QIcon(path + "settings.svg"))
        self.buttonInfo.setIcon(QIcon(path + "info.svg"))
        self.play_button.setIcon(QIcon(path + "play.svg"))
        self.save_button.setIcon(QIcon(path + "save.svg"))

    def save_settings(self):
        settings_to_save = {
            "light_theme": self.light_theme
        }

        with open(self.settings_file, "w") as file:
            json.dump(settings_to_save, file)

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                self.light_theme = settings.get("light_theme", True)  # Se "light_theme" non è presente, imposta il valore predefinito su True
        except FileNotFoundError:
            # Se il file non è stato trovato, usa le impostazioni predefinite
            print("Error loading settings json file")

    def createPlotter(self):
        # Crea una figura di esempio
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

        # Crea un canvas per il plotter e collega la figura ad esso
        canvas = FigureCanvas(fig)

        return canvas

    def create_frame_analysis(self):
        frame = QFrame()

        # Imposta un layout verticale per il frame principale
        layout = QVBoxLayout(frame)

        # Creazione frames
        frame1 = QFrame()
        frame2 = QFrame()
        patient_frame = QFrame()        
        frame_a = QFrame()
        frame_b = QFrame()
        frameRecording = QFrame()

        # layout frames
        layout1 = QHBoxLayout(frame1)
        layout2 = QHBoxLayout(frame2)
        layout_patient_frame = QVBoxLayout(patient_frame)
        layout_a = QVBoxLayout(frame_a)
        layout_b = QVBoxLayout(frame_b)
        layoutRecording = QHBoxLayout(frameRecording)
        

        layout_patient_frame.addWidget(QLabel("Nome: Mario"))
        layout_patient_frame.addWidget(QLabel("Cognome: Rossi"))
        layout_patient_frame.addWidget(QLabel("ID: 12345"))
        layout_patient_frame.addWidget(QLabel("Gruppo: Parkingson"))
        layout_patient_frame.addWidget(QLabel("Ospedale: Milano"))
        button_seleziona_paziente = QPushButton("Seleziona Paziente")

        layout_patient_frame.addWidget(button_seleziona_paziente)

        # Chiamiamo la funzione createPlotter e aggiungiamo il plotter al layout di frame1
        plotter_widget = self.createPlotter()

        layout1.addWidget(patient_frame, 2)
        layout1.addWidget(plotter_widget, 6)
        layout1.setContentsMargins(10, 18, 5, 5)

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

        # Crea e aggiungi i pulsanti a frame_a
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(self.whiteIconPath + "play.svg"))
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
        self.save_button.setIcon(QIcon(self.whiteIconPath + "save.svg"))
        self.save_button.setFixedSize(85, 85)  # Imposta la dimensione fissa del pulsante
        self.save_button.setIconSize(QSize(25, 25)) 
        self.save_button.setStyleSheet(localcss)

        layoutRecording.addWidget(self.stop_button)
        layoutRecording.addWidget(self.play_button)
        layoutRecording.addWidget(self.save_button)

        layout_a.addWidget(frameRecording)

        # Aggiungi un widget QLabel per visualizzare il tempo
        self.time_label = QLabel("00:00:00")
        layout_a.addWidget(self.time_label)
        self.time_label.setAlignment(Qt.AlignCenter)

        label = QLabel("Selected Exercise:", self)
        layout_b.addWidget(label)
        # Crea un selettore per il tipo di esercizio
        exercise_selector = QComboBox()
        exercise_selector.addItems(["Walk", "March in place (Hight Knees)", "March in place (Butt Kicks)", "Swing", "Double Step"])
        layout_b.addWidget(exercise_selector)
        exercise_selector.currentTextChanged.connect(lambda text_value=exercise_selector.currentText: self.selectExercise(text_value))


        # Crea e aggiungi i pulsanti per la velocità
        music_buttons_frame = QFrame()
        music_buttons_layout = QHBoxLayout(music_buttons_frame)
        music_buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.noMusic_button = QPushButton("No Music")
        self.noMusic_button.clicked.connect(lambda: setattr(self, 'modality', 1))

        self.music_button = QPushButton("Music")
        self.music_button.clicked.connect(lambda: setattr(self, 'modality', 2))

        self.realTimeMusic_button = QPushButton("Real Time Music")
        self.realTimeMusic_button.clicked.connect(lambda: setattr(self, 'modality', 3))

        music_buttons_layout.addWidget(self.noMusic_button)
        music_buttons_layout.addWidget(self.music_button)
        music_buttons_layout.addWidget(self.realTimeMusic_button)

        layout_b.addWidget(music_buttons_frame)

        label2 = QLabel("Selected Music:", self)
        layout_b.addWidget(label2)
        # Crea un selettore per il tipo di musica
        music_selector = QComboBox()
        music_selector.addItems(["Music 1", "Music 2"])     # i nomi devono essere recuperati dinamicamente dalla cartella delle musiche
        layout_b.addWidget(music_selector)
        music_selector.currentTextChanged.connect(lambda text_value=music_selector.currentText: self.selectExercise(text_value))

        # Aggiungi i due frame a layout2
        layout2.addWidget(frame_b)
        layout2.addWidget(frame_a)

        # Imposta la policy di espansione
        layout.addWidget(frame1, 2)
        layout.addWidget(frame2, 1)

        # Imposta la policy di espansione
        layout2.setStretch(0, 2)
        layout2.setStretch(1, 2)

        return frame

    def create_frame_archive(self):
        frame = QFrame()
        return frame

    def create_frame_statistics(self):
        frame = QFrame()
        return frame

    def create_frame_settings(self):
        frame = QFrame()
        return frame


    def show_frame(self, frame):
        layout = self.mainWidget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().hide()  # Nasconde il widget invece di eliminarlo

        layout.addWidget(frame)
        frame.show()  # Mostra il nuovo frame

    
    def buttonAnalysis_clicked(self):
        self.show_frame(self.frameAnalysis)
        print("analysis")

    def buttonArchive_clicked(self):
        self.show_frame(self.frameArchive)
        print("archive")

    def buttonSettings_clicked(self):
        self.show_frame(self.frameSettings)
        print("settings")

    def buttonStatistics_clicked(self):
        self.show_frame(self.frameStatistics)
        print("statistics")
    
    def openDocumentation(self):
        try:
            # Apre il file HTML nel browser predefinito
            webbrowser.open('documentation.html')
        except:
            print("Error opening documentation file")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    sys.exit(app.exec_())
