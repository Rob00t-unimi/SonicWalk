# MIT License

# Copyright (c) 2024 Roberto Tallarini

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QFrame
from frames.sideMenu import SideMenu
from pages.analysis_page import AnalysisPage
from pages.archive_page import ArchivePage
from pages.settings_page import SettingsPage
from pages.statistics_page import StatisticsPage
import sys

# from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sonic-Walk")
        self.resize(1100, 720)

        # Define the path to the settings file
        self.settings_file = "data/settings.json" 

        # Load theme settings from the JSON file
        try:
            self.light = self._load_theme()
        except:
            self.light = True

        # Define colors for light and dark themes
        self.lightTheme = "background-color: #DCDFE4;"
        self.darkTheme = "background-color: #1D2125;"

        self.setup_ui()

        self.pageHandler = "Analysis"

    def setup_ui(self):

        self.initial_widget = QWidget()
        self.initialLayout = QHBoxLayout(self.initial_widget)
        self.initialLayout.setContentsMargins(0, 0, 0, 0)
        self.initial_widget.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

        # Setup and add content widget in initial layout
        self.setup_content_widget()  
        
        # Instantiate SideMenu
        self.side_menu = SideMenu(setActivePage=self.pageHandler, toggleTheme=self.toggleTheme, light = self.light)

        # Set menu and content widget in initial layout
        self.initialLayout.addWidget(self.side_menu)
        self.initialLayout.addWidget(self.contentWidget)

        # Set sideMenu as central widget
        self.setCentralWidget(self.initial_widget)

    def setup_content_widget(self):
        self.contentWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create instances of pages
        self.analysisPage = AnalysisPage(light = self.light)
        self.archivePage = ArchivePage(light = self.light)
        self.settingsPage = SettingsPage(light = self.light)
        self.statisticsPage = StatisticsPage(light = self.light)

        self.contentWidget.setLayout(layout)

    def pageHandler(self, page):
        """
        Effects: Hide every page frame and show the selected page frame.
                 This function is passed and called inside the buttons.
        """
        if page == "Analysis":
            self.show_frame(self.analysisPage)
        elif page == "Settings":
            self.show_frame(self.settingsPage)
        elif page == "Statistics":
            self.show_frame(self.statisticsPage)
        elif page == "Archive":
            self.show_frame(self.archivePage)

    def show_frame(self, frame):
        """
        Effects: Hide every page frame and show the passed page frame.
        """
        layout = self.contentWidget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().hide()  # Hide the widget instead of deleting it

        layout.addWidget(frame)
        frame.show()  # Show the new frame

    def toggleTheme(self):
        """
        Effects: Switch the theme.
                 It is passed to the sideMenu object.
        """
        self.light = not self.light
        self.initial_widget.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        self.analysisPage.toggleTheme()

    def _load_theme(self):
        """
            Effects:    Loads theme settings from the JSON settings file and sets self.light (True for light, False for dark)
        """
        try:
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                return settings.get("light_theme", True)  # If "light_theme" is not present, default to True
        except FileNotFoundError:
            print("Settings file not found. Using default theme (light).")
            return True
        except Exception as e:
            print("Error loading settings:", e)
            return True  # Use default theme (light) in case of any errors
        
    def closeEvent(self, event):
        # close the recording frame safely if running
        frame_to_close = self.findChild(QFrame, "recording_frame")
        frame_to_close.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # apply_stylesheet(app, theme='light_blue.xml')
    window.show()
    sys.exit(app.exec_())
