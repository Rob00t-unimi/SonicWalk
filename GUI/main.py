import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QIcon
import sys
from GUI.frames.sideMenu import SideMenu
from GUI.pages.analysis_page import AnalysisPage
from GUI.pages.archive_page import ArchivePage
from GUI.pages.settings_page import SettingsPage
from GUI.pages.statistics_page import StatisticsPage
from GUI.iconsManager import IconsManager
from qt_material import apply_stylesheet, list_themes

icons_manager = IconsManager()

class MainWindow(QMainWindow):
    """
    Main window of a PyQt5 hospital application that manages the analysis, recording, and visualization of rehabilitative exercises using MTW Awinda sensors.
    It handles a dataset of patients with their respective exercise recordings.
    """
    def __init__(self, app):
        """
        MODIFIES: 
            - self

        EFFECTS: 
            - initializes the class and starts the GUI
        """
        super().__init__()

        self.app = app

        self.setWindowTitle("SonicWalk")
        self.resize(1100, 720)
        
        self.setWindowIcon(QIcon('GUI/icons/SonicWalk_logo.png'))

        self.settings_path = 'GUI/data/settings.json'
        self.dataset_path = 'GUI/data/dataset.json'

        # Load theme from the JSON file
        try:
            self.theme_name = self._load_theme()
            if self.theme_name not in list_themes(): self.theme_name = "light_teal_500.xml"
        except:
            self.theme_name = "light_teal_500.xml"

        # Check the light or dark status
        if "dark_" in self.theme_name: self.light = False
        else: self.light = True

        self.icons_color = True # True = black, icons will be switched if light is False

        self.setup_ui()

        self.pageHandler = "Analysis"
        self.apply_theme()


    def apply_theme(self, theme = None, write_theme = False):
        """
        REQUIRES:
            - theme (str): A valid theme file name from the list of qt-material themes. Default is None.
            - write_theme (bool): Indicates if the theme should be written in the JSON settings file. Default is False.

        MODIFIES: 
            - self.light
            - self.theme_name
            - settings.JSON
            - self

        EFFECTS:
            - Applies the specified theme. If None, applies the theme obtained from the settings. If not available in the settings, applies a default theme.
            - Updates self.light and the color of icons when switching between light and dark themes.
            - Updates the theme name in self.theme_name.
            - Enables or disables the theme toggle button in the menu based on the availability of the applied theme in both light and dark versions.
        """
        # extra options of qt-material
        extra = {
            # Button colors
            'danger': '#dc3545',
            'warning': '#ffc107',
            'success': '#0eb51c',
            # Density
            'density_scale': '0',
        }
        css_path = "GUI/custom_css.css"
        if theme is None: apply_stylesheet(self.app, theme=self.theme_name, extra=extra, invert_secondary=self.light, css_file = css_path)
        else: 
            self.light = True if "dark_" not in theme else False
            apply_stylesheet(self.app, theme=theme, extra=extra, invert_secondary=self.light, css_file = css_path)

        if write_theme and theme is not None:
            self.theme_name = theme
            self._write_theme()

        themes = list_themes()
        if theme is None: theme = self.theme_name
        if "light_" in theme: theme = theme.replace("light_", "dark_")
        elif "dark_" in theme: theme = theme.replace("dark_", "light_")
        if theme not in themes: self.side_menu.themeButton.setEnabled(False)
        else: self.side_menu.themeButton.setEnabled(True)

        self.archivePage.light = self.light
        self.set_icons()

    def set_icons(self):
        """
        MODIFIES: 
            - self
            - all pyqt5 widgets with property "icon_name"

        EFFECTS: 
            - Sets new icons with inverted colors for all widgets with the property "icon_name"
        """
        if self.light: icons_manager.set_black()
        else: icons_manager.set_white()
        widgets = self.findWidgets("icon_name")
        for widget in widgets:
            name = widget.property("icon_name")
            if name == "sun":
                if self.light:
                    widget.setProperty("icon_name", "moon")
                    widget.setIcon(icons_manager.getIcon("moon"))
                else: widget.setIcon(icons_manager.getIcon("sun"))
            elif name == "moon":
                if not self.light:
                    widget.setProperty("icon_name", "sun")
                    widget.setIcon(icons_manager.getIcon("sun"))
                else: widget.setIcon(icons_manager.getIcon("moon"))
            else:
                widget.setIcon(icons_manager.getIcon(name))

    def findWidgets(self, property):
        """
        REQUIRES: 
            - property (string): must be a valid pyqt5 widget property

        EFFECTS: 
            - returns a list of widgets with the specified property
        """
        widgets = []
        for widget in QApplication.allWidgets():
            name = widget.property(property)
            if name is not None:
                widgets.append(widget)
        return widgets
            
    def setup_ui(self):
        """
        MODIFIES: 
            - self

        EFFECTS: 
            - sets up the gui by creating all components
        """
        self.initial_widget = QWidget()
        self.initialLayout = QHBoxLayout(self.initial_widget)
        self.initialLayout.setContentsMargins(0, 0, 0, 0)
        
        # sets up all the pages
        self.setup_content_widget()  
        
        # Instantiate SideMenu
        self.side_menu = SideMenu(setActivePage=self.pageHandler, toggleTheme=self.toggleTheme, light= self.light)

        # Set menu and content widget in initial layout
        self.initialLayout.addWidget(self.side_menu)
        self.initialLayout.addWidget(self.contentWidget)

        self.setCentralWidget(self.initial_widget)

    def setup_content_widget(self):
        """
        MODIFIES: 
            - self

        EFFECTS: 
            - sets up all the pages and components, analysis page, archive page, settings page, statistics page
        """
        self.contentWidget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create instances of pages
        self.analysisPage = AnalysisPage(light=self.light)
        self.archivePage = ArchivePage(light = self.light, icons_manager = icons_manager)
        self.analysisPage.set_update_patient_list(self.archivePage.reload_patient_list)
        self.settingsPage = SettingsPage(self.apply_theme, self.theme_name, self.archivePage.clean_all, icons_manager)
        self.statisticsPage = StatisticsPage()

        self.contentWidget.setLayout(layout)

    def pageHandler(self, page):
        """
        REQUIRES: 
            - page (string): valid page Indicator from (Analysis, Settings, Statistics, Archive)

        EFFECTS: 
            - Hide every page frame and show the selected page frame.
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
        REQUIRES: 
            - frame (QWidget): valid pyqt5 widget

        EFFECTS: 
            - Hide every page frame and show the passed page frame.
        """
        # hide all widgets in contentWidget
        layout = self.contentWidget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().hide()
        # show the specified frame
        layout.addWidget(frame)
        frame.show()

    def toggleTheme(self):
        """
        MODIFIES: 
            - self
            - settings.JSON

        Effects: 
            - Switch the theme.
        """
        if self.light and "light_" in self.theme_name: new_theme_name = self.theme_name.replace("light_", "dark_")
        elif not self.light and "dark_" in self.theme_name: new_theme_name = self.theme_name.replace("dark_", "light_")
        else: raise Exception("Impossible to switch theme")

        if new_theme_name in list_themes(): 
            self.theme_name = new_theme_name
            self.light = not self.light
            self.apply_theme()
            self._write_theme()

        else: raise Exception("Theme not found")
        
    def _write_theme(self):
        """
        MODIFIES: 
            - settings.JSON

        EFFECTS: 
            - write the current theme in settings.JSON.
        """
        try:
            with open(self.settings_path, "r") as file:
                settings = json.load(file)
            settings["theme"] = self.theme_name
            with open(self.settings_path, "w") as file:
                json.dump(settings, file)
        except FileNotFoundError:
            print("Settings file not found. Using default theme (light).")
            return True

    def _load_theme(self):
        """
        EFFECTS: 
            - Loads theme from settings.JSON and returns the theme name
        """
        with open(self.settings_path, "r") as file:
            settings = json.load(file)
            if settings["theme"] is not None and settings["theme"] != "":
                return settings["theme"]
            raise ValueError("Not theme present")
    
    def closeEvent(self, event):
        """
        EFFECTS: 
            - Calls the close method of the recording_frame widget, ensuring that any ongoing recording is stopped and processes communicating with MTW devices are safely terminated.
            - This ensures a safe exit.
            - Finally, calls the superclass closeEvent.
        """
        frame_to_close = self.findChild(QWidget, "recording_frame")
        frame_to_close.close()
        super().closeEvent(event)
        

def run_main():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())