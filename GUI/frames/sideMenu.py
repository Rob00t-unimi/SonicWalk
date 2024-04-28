import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import webbrowser
import sys
import json
from qt_material import apply_stylesheet, list_themes

sys.path.append("../")

from components.menuButton import MenuButton


class SideMenu(QFrame):
    def __init__(self, setActivePage=None, toggleTheme = None, light = True):
        """
        Requires:
            - setActivePage: Callback function for setting the active page called upon clicking an activity button
            - toggleTheme: a callback function for setting the theme
            - light: a boolean indicating light or dark theme
        Modifies:
            - Initializes self attributes and layout
            - Sets up the buttons and frames for the side menu
        Effects:
            - Initializes a custom side menu frame.
        """
        super().__init__()

        self.setProperty('class', 'custom_menu')
        # initialize attributes
        self.settings_file = "data/settings.json" 
        self.toggleThemeMain = toggleTheme
        self.menu_expanded = False  # menu state
        self.light = light

        # Define paths for icons
        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        # Callback function for setting the active page
        self.setActivePage = setActivePage

        # Initialization of Object
        self.setFixedWidth(60)
        self.sideFrame_layout = QVBoxLayout(self)
        self.sideFrame_layout.setContentsMargins(5, 5, 5, 5)

        # Hamburger menu button
        self.hamburgerMenuButton = MenuButton(icons_paths=[self.blackIconPath + "menu.svg", self.whiteIconPath + "menu.svg"], text="   Menu", light=self.light)
        self.hamburgerMenuButton.clicked.connect(self.hamburgerFunction)
        self.sideFrame_layout.addWidget(self.hamburgerMenuButton)

        # Separation line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        self.sideFrame_layout.addWidget(line)

        # Create main buttons frame
        self._setupMainButtonsFrame()

        # Create a spacer
        self.sideFrame_layout.addStretch()

        # Setup second buttons frame
        self._setupBottomFrame()

        # Default start with the Analysis page
        self.analysisButton.click()
        self.analysisButton.setChecked(True)

    def _setupMainButtonsFrame(self):
        """
            Modifies:   self
            Effects:    Sets up the frame for the activity buttons.
                        It create the inner frame and the buttons
        """
        # Create frame
        self.inner_frame1 = QFrame()
        self.inner_frame1.setProperty('class', 'custom_menu')
        self.inner_frame1_layout = QVBoxLayout(self.inner_frame1)
        self.inner_frame1_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_frame1_layout.setSpacing(0)

        # Create buttons
        self.analysisButton = MenuButton(icons_paths=[self.blackIconPath + "activity.svg", self.whiteIconPath + "activity.svg"], text="   Analysis", light=self.light)
        self.analysisButton.clicked.connect(lambda: self.selectPage("Analysis"))
        self.archiveButton = MenuButton(icons_paths=[self.blackIconPath + "archive.svg", self.whiteIconPath + "archive.svg"], text="   Archive", light=self.light)
        self.archiveButton.clicked.connect(lambda: self.selectPage("Archive"))
        self.statisticsButton = MenuButton(icons_paths=[self.blackIconPath + "bar-chart-2.svg", self.whiteIconPath + "bar-chart-2.svg"], text="   Statistics", light=self.light)
        self.statisticsButton.clicked.connect(lambda: self.selectPage("Statistics"))
        self.settingsButton = MenuButton(icons_paths=[self.blackIconPath + "settings.svg", self.whiteIconPath + "settings.svg"], text="   Settings", light=self.light)
        self.settingsButton.clicked.connect(lambda: self.selectPage("Settings"))

        self.analysisButton.setCheckable(True)
        self.archiveButton.setCheckable(True)
        self.statisticsButton.setCheckable(True)
        self.settingsButton.setCheckable(True)

        # Add buttons to frame
        self.inner_frame1_layout.addWidget(self.analysisButton)
        self.inner_frame1_layout.addWidget(self.archiveButton)
        self.inner_frame1_layout.addWidget(self.statisticsButton)
        self.inner_frame1_layout.addWidget(self.settingsButton)

        # Add inner frame 1 to main frame
        self.inner_frame1_layout.setStretch(0, 1)
        self.sideFrame_layout.addWidget(self.inner_frame1)

    def _setupBottomFrame(self):
        """
            Modifies:   self
            Effects:    Sets up the frame for the bottom buttons
                        It create the inner frame and the buttons
        """
        # Create frame
        self.inner_frame2 = QFrame()
        self.inner_frame2.setProperty('class', 'custom_menu')
        self.inner_frame2_layout = QVBoxLayout(self.inner_frame2)
        self.inner_frame2_layout.setContentsMargins(0, 0, 0, 0)

        # Create Buttons
        self.themeButton = MenuButton(icons_paths=[self.blackIconPath + "sun.svg", self.whiteIconPath + "moon.svg"], text="  Theme", light=self.light)
        self.themeButton.clicked.connect(self.toggleTheme)
        self.infoButton = MenuButton(icons_paths=[self.blackIconPath + "info.svg", self.whiteIconPath + "info.svg"], text="   Info", light=self.light)
        self.infoButton.clicked.connect(self._openDocumentation)

        # Add buttons to frame
        self.inner_frame2_layout.addWidget(self.themeButton)
        self.inner_frame2_layout.addWidget(self.infoButton)

        # Add inner frame 2 to main frame
        self.sideFrame_layout.addWidget(self.inner_frame2)

    def hamburgerFunction(self):
        """
            Modifies:   self
            Effects:    Expands/Collapses the menu and the buttons in it
        """
        self.menu_expanded = not self.menu_expanded
        self.setFixedWidth(170 if self.menu_expanded else 60)

        if self.menu_expanded:
            self.hamburgerMenuButton.expandButton()
            self.analysisButton.expandButton()
            self.archiveButton.expandButton()
            self.statisticsButton.expandButton()
            self.settingsButton.expandButton()
        else:
            self.hamburgerMenuButton.collapseButton()
            self.analysisButton.collapseButton()
            self.archiveButton.collapseButton()
            self.statisticsButton.collapseButton()
            self.settingsButton.collapseButton()
            
    def selectPage(self, page):
        """
        Requires:   page: a string from "Analysis, Settings, Archive, Statistics"
        Modifies:   self
        Effects:    Deselects buttons based on the selected page.
                    Sets the active page.
        """
        self.analysisButton.setChecked(False)
        self.archiveButton.setChecked(False)
        self.statisticsButton.setChecked(False)
        self.settingsButton.setChecked(False)

        if page == "Analysis": self.analysisButton.setChecked(True)
        elif page == "Settings":  self.settingsButton.setChecked(True)
        elif page == "Archive": self.archiveButton.setChecked(True)
        elif page == "Statistics": self.statisticsButton.setChecked(True)

        if self.setActivePage is not None:
            self.setActivePage(page)
        print(page)

    def toggleTheme(self, notcallmain = False):
        self.light = not self.light
        if not notcallmain: self.toggleThemeMain()
        self.themeButton.setIcon(QIcon(self.blackIconPath + "moon.svg" if self.light else self.whiteIconPath + "sun.svg"))
        themes = list_themes()
        try:
            with open("data/settings.json", "r") as file:
                settings = json.load(file)
            theme = settings["theme"]
            if "light" in theme: theme = theme.replace("light", "dark")
            elif "dark" in theme: theme = theme.replace("dark", "light")
            if not theme in themes: self.themeButton.setEnabled(False)
            else: self.themeButton.setEnabled(True)
        except FileNotFoundError:
            print("Settings file not found. Theme not setted.")

    def _openDocumentation(self):
        """
            Effects:    Opens the HTML documentation in a web browser
        """
        try:
            webbrowser.open('documentation.html')
        except Exception as e:
            print("Error opening documentation file:", e)

    def _save_theme(self):
        """
        Modify: JSON settings file
        Effects: Saves theme settings in the JSON settings file
        """
        try:
            # Load current settings from the JSON file
            with open(self.settings_file, "r") as file:
                current_settings = json.load(file)
        except Exception as e:
            print("Error loading settings:", e)
            return

        # Modify the current settings
        current_settings["light_theme"] = self.light

        try:
            # Save the modified settings to the JSON file
            with open(self.settings_file, "w") as file:
                json.dump(current_settings, file)
        except Exception as e:
            print("Error saving settings:", e)

