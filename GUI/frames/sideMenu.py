from PyQt5.QtWidgets import *
import webbrowser
import sys
import json

sys.path.append("../")

from components.menuButton import MenuButton

class SideMenu(QFrame):
    def __init__(self, setActivePage=None, light = True, toggleTheme = None):
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

        # initialize attributes
        self.settings_file = "data/settings.json" 
        self.toggleTheme = toggleTheme
        self.light = light
        self.menu_expanded = False  # menu state

        # theme styles
        self.lightTheme = "background-color: #B3B9C4;"
        self.darkTheme = "background-color: #38414A;"

        # Define paths for icons
        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        # Callback function for setting the active page
        self.setActivePage = setActivePage

        # Initialization of Object
        self.setFixedWidth(60)
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        self.sideFrame_layout = QVBoxLayout(self)
        self.sideFrame_layout.setContentsMargins(5, 5, 5, 5)

        # Hamburger menu button
        self.hamburgerMenuButton = MenuButton(icons_paths=[self.blackIconPath + "menu.svg", self.whiteIconPath + "menu.svg"], text="   Menu", light=self.light, stayActive=False)
        self.hamburgerMenuButton.onClick(self.hamburgerFunction)
        self.sideFrame_layout.addWidget(self.hamburgerMenuButton)

        # Separation line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        line.setStyleSheet("color: #6c3ce5;")
        self.sideFrame_layout.addWidget(line)

        # Create main buttons frame
        self._setupMainButtonsFrame()

        # Create a spacer
        self.spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sideFrame_layout.addItem(self.spacer_item)

        # Setup second buttons frame
        self._setupBottomFrame()

        # Default start with the Analysis page
        self.analysisButton.clickCall()

    def _setupMainButtonsFrame(self):
        """
            Modifies:   self
            Effects:    Sets up the frame for the activity buttons.
                        It create the inner frame and the buttons
        """
        # Create frame
        self.inner_frame1 = QFrame()
        self.inner_frame1_layout = QVBoxLayout(self.inner_frame1)
        self.inner_frame1_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_frame1_layout.setSpacing(0)

        # Create buttons
        self.analysisButton = MenuButton(icons_paths=[self.blackIconPath + "activity.svg", self.whiteIconPath + "activity.svg"], text="   Analysis", light=self.light, stayActive=True)
        self.analysisButton.onClick(lambda: self.selectPage("Analysis"))
        self.archiveButton = MenuButton(icons_paths=[self.blackIconPath + "archive.svg", self.whiteIconPath + "archive.svg"], text="   Archive", light=self.light, stayActive=True)
        self.archiveButton.onClick(lambda: self.selectPage("Archive"))
        self.statisticsButton = MenuButton(icons_paths=[self.blackIconPath + "bar-chart-2.svg", self.whiteIconPath + "bar-chart-2.svg"], text="   Statistics", light=self.light, stayActive=True)
        self.statisticsButton.onClick(lambda: self.selectPage("Statistics"))
        self.settingsButton = MenuButton(icons_paths=[self.blackIconPath + "settings.svg", self.whiteIconPath + "settings.svg"], text="   Settings", light=self.light, stayActive=True)
        self.settingsButton.onClick(lambda: self.selectPage("Settings"))

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
        self.inner_frame2_layout = QVBoxLayout(self.inner_frame2)
        self.inner_frame2_layout.setContentsMargins(0, 0, 0, 0)

        # Create Buttons
        self.themeButton = MenuButton(icons_paths=[self.blackIconPath + "moon.svg", self.whiteIconPath + "sun.svg"], text="  Theme", light=self.light)
        self.themeButton.onClick(self._toggleTheme)
        self.infoButton = MenuButton(icons_paths=[self.blackIconPath + "info.svg", self.whiteIconPath + "info.svg"], text="   Info", light=self.light)
        self.infoButton.onClick(self._openDocumentation)

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
        self.analysisButton.deselectButton()
        self.archiveButton.deselectButton()
        self.statisticsButton.deselectButton()
        self.settingsButton.deselectButton()

        if self.setActivePage is not None:
            self.setActivePage(page)
        print(page)

    def _toggleTheme(self):
        """           
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
                        all custom elements
            Effects:    Switches between light and dark themes.
                        Saved changes in the JSON file
        """
        self.light = not self.light
        self._save_theme()

        # Switch theme for all buttons
        self.hamburgerMenuButton.toggleTheme()
        self.analysisButton.toggleTheme()
        self.archiveButton.toggleTheme()
        self.statisticsButton.toggleTheme()
        self.settingsButton.toggleTheme()
        self.infoButton.toggleTheme()
        self.themeButton.toggleTheme()

        self.toggleTheme()   # it set out of the class the value of self.light

        # Update the stylesheet to reflect the new theme
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

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
            Modifies:   JSON settings file
            Effects:    Saves theme settings in the JSON settings file
        """
        settings_to_save = {
            "light_theme": self.light
        }

        try:
            with open(self.settings_file, "w") as file:
                json.dump(settings_to_save, file)
        except Exception as e:
            print("Error saving settings:", e)

