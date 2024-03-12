import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import json
import webbrowser


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sonic-Walk")
        self.resize(1000, 600)

        self.light_theme = None

        self.settings_file = "settings.json" 
        self.load_settings()

        self.menu_expanded = False

        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        self.setup_ui()

    def setup_ui(self):
        self.setup_central_widget()
        self.update_theme()
        self.buttonAnalysis_clicked()

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
        self.frame.setFixedWidth(50)
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
        button.setFixedSize(35, 35)
        button.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 150); }")
        return button

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.update_menu()

    def update_menu(self):
        self.frame.setFixedWidth(150 if self.menu_expanded else 50)
        button_list = [
            (self.hamburger_button, "Menu"),
            (self.buttonAnalysis, "Analysis"),
            (self.buttonArchive, "Archive"),
            (self.buttonStatistics, "Statistics"),
            (self.buttonSettings, "Settings"),
            (self.theme_button, "Theme"),
            (self.buttonInfo, "Info")
        ]
        for button, text in button_list:
            button.setText(text if self.menu_expanded else "")
            button.setFixedSize(140 if self.menu_expanded else 35, 35)


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


    def create_frame_analysis(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: lightblue;")  # Imposta il colore di sfondo
        label = QLabel("Contenuto per l'analisi")
        return frame

    def create_frame_archive(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: lightgreen;")  # Imposta il colore di sfondo
        label = QLabel("Contenuto per l'archivio")
        return frame

    def create_frame_statistics(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: lightcoral;")  # Imposta il colore di sfondo
        label = QLabel("Contenuto per le statistiche")
        return frame

    def create_frame_settings(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: lightsalmon;")  # Imposta il colore di sfondo
        label = QLabel("Contenuto per le impostazioni")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    sys.exit(app.exec_())
