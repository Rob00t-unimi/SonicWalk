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
from pages.analysis_page import AnalysisPage
from pages.archive_page import ArchivePage
from pages.settings_page import SettingsPage
from pages.statistics_page import StatisticsPage
from PyQt5.QtGui import QFont


# da fare in seguito:
# Aggiungere la pagina archivio con la possibilità di visualizzare e aggiungere ospedali e pazienti
# aggiungere la finestra seleziona paziente in analyzer
# ++ ogni pulsante quando premuto deve rimanere "acceso"
# generalizzare di più anche lo stile e il toggle di switch theme in modo che agisca su tutti i file


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sonic-Walk")
        self.resize(1080, 720)

        #self.light_theme = None        rivedere dopo

        # self.settings_file = "data/settings.json" 
        # self.load_settings()

        self.menu_buttons = []

        self.menu_expanded = False

        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        self.setup_ui()

    def setup_ui(self):
        # setup initial widget
        self.setup_initial_widget()
        #self.update_theme()

        # setup and add menu side frame in initial layout
        self.setup_side_frame()
        self.initialLayout.addWidget(self.sideFrame)

        # setup and add main widget in initial layout
        self.setup_main_widget()  
        self.initialLayout.addWidget(self.mainWidget)

        self.setCentralWidget(self.initial_widget)

        self.buttonAnalysis_clicked()

    def setup_initial_widget(self):
        self.initial_widget = QWidget()
        self.initialLayout = QHBoxLayout(self.initial_widget)
        self.initialLayout.setContentsMargins(0, 0, 0, 0)

    def setup_side_frame(self):
        self.sideFrame = QFrame()
        self.sideFrame.setFixedWidth(60)
        self.sideFrame.setStyleSheet("background-color: #B3B9C4;")
        self.sideFrame_layout = QVBoxLayout(self.sideFrame)
        self.sideFrame_layout.setContentsMargins(5, 5, 5, 5)

        self.setup_hamburger_button()
        self.setup_inner_frame1()
        self.setup_spacer()
        self.setup_inner_frame2()

    def setup_hamburger_button(self):
        self.hamburger_button = self.create_button(self.blackIconPath + "menu.svg")
        self.hamburger_button.clicked.connect(self.toggle_menu)
        self.sideFrame_layout.addWidget(self.hamburger_button)

        line = QFrame(self.sideFrame)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        line.setStyleSheet("color: #6c3ce5;")
        self.sideFrame_layout.addWidget(line)

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
        self.sideFrame_layout.addWidget(self.inner_frame1)

    def setup_spacer(self):
        self.spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sideFrame_layout.addItem(self.spacer_item)

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

        self.sideFrame_layout.addWidget(self.inner_frame2)

    def create_button(self, icon_path):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setFixedSize(50, 50)
        button.setIconSize(QSize(25, 25)) 
        button.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        font = QFont("Sans-serif", 11)
        button.setFont(font)

        return button
    
    
    def setup_main_widget(self):
        self.mainWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Creiamo le istanze delle pagine
        self.analysisPage = AnalysisPage()
        self.archivePage = ArchivePage()
        self.settingsPage = SettingsPage()
        self.statisticsPage = StatisticsPage()

        self.mainWidget.setLayout(layout)

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.update_menu()

    def update_menu(self):
        self.sideFrame.setFixedWidth(170 if self.menu_expanded else 60)
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
            button.setFixedSize(160 if self.menu_expanded else 50, 50)


    def toggle_theme(self):
        # self.light_theme = not self.light_theme
        # self.save_settings()
        # theme_icon = self.blackIconPath + "moon.svg" if self.light_theme else self.whiteIconPath + "sun.svg"
        # self.theme_button.setIcon(QIcon(theme_icon))
        # self.update_theme()
        return

    # def update_theme(self):
    #     self.update_icon_paths()
    #     theme_stylesheet = "background-color: #2b2b2b; color: white;" if not self.light_theme else ""
    #     self.setStyleSheet(theme_stylesheet)
    #     frame_stylesheet = "background-color: #3a3a3a;" if not self.light_theme else "background-color: lightgray;"
    #     self.frame.setStyleSheet(frame_stylesheet)

    #     # Aggiorna l'icona del tema dopo aver aggiornato lo stile
    #     theme_icon_path = self.blackIconPath + "moon.svg" if self.light_theme else self.whiteIconPath + "sun.svg"
    #     self.theme_button.setIcon(QIcon(theme_icon_path))

    # def update_icon_paths(self):
    #     path = self.whiteIconPath if not self.light_theme else self.blackIconPath
    #     self.hamburger_button.setIcon(QIcon(path + "menu.svg"))
    #     self.buttonAnalysis.setIcon(QIcon(path + "activity.svg"))
    #     self.buttonArchive.setIcon(QIcon(path + "archive.svg"))
    #     self.buttonStatistics.setIcon(QIcon(path + "bar-chart-2.svg"))
    #     self.buttonSettings.setIcon(QIcon(path + "settings.svg"))
    #     self.buttonInfo.setIcon(QIcon(path + "info.svg"))
    #     self.play_button.setIcon(QIcon(path + "play.svg"))
    #     self.save_button.setIcon(QIcon(path + "save.svg"))

    # def save_settings(self):
    #     settings_to_save = {
    #         "light_theme": self.light_theme
    #     }

    #     with open(self.settings_file, "w") as file:
    #         json.dump(settings_to_save, file)

    # def load_settings(self):
    #     try:
    #         with open(self.settings_file, "r") as file:
    #             settings = json.load(file)
    #             self.light_theme = settings.get("light_theme", True)  # Se "light_theme" non è presente, imposta il valore predefinito su True
    #     except FileNotFoundError:
    #         # Se il file non è stato trovato, usa le impostazioni predefinite
    #         print("Error loading settings json file")



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
        self.deactivate_buttons()
        self.buttonAnalysis.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); } }")
        self.show_frame(self.analysisPage.get_frame())
        print("analysis")

    def buttonArchive_clicked(self):
        self.deactivate_buttons()
        self.buttonArchive.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); } }")
        self.show_frame(self.archivePage.get_frame())
        print("archive")

    def buttonSettings_clicked(self):
        self.deactivate_buttons()
        self.buttonSettings.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); } }")
        self.show_frame(self.settingsPage.get_frame())
        print("settings")

    def buttonStatistics_clicked(self):
        self.deactivate_buttons()
        self.buttonStatistics.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); } }")
        self.show_frame(self.statisticsPage.get_frame())
        print("statistics")

    def deactivate_buttons(self):
        # Disattiva tutti i pulsanti del menu
        self.buttonAnalysis.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.buttonSettings.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.buttonStatistics.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")
        self.buttonArchive.setStyleSheet("QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; } QPushButton:hover { background-color: rgba(108, 60, 229, 30%); }")

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

    
    def set_font_recursive(widget, font):
        """
        Imposta ricorsivamente il font per tutti i widget figli di widget.
        """
        widget.setFont(font)
        for child_widget in widget.findChildren(QWidget):
            set_font_recursive(child_widget, font)

    # Imposta il font per tutti i widget figli di self.frame
    set_font_recursive(app, QFont("Sans-serif", 10))


    sys.exit(app.exec_())
