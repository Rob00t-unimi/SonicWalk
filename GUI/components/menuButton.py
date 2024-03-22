from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

class MenuButton(QPushButton):
    def __init__(self, icons_paths, text, light = True, stayActive = False):
        """ 
        Requires: 
            - icons_paths: list of two strings, where the first string represents the path of the black icon and the second string represents the path of the white icon
            - text: a string representing the button text
            - light: a boolean value indicating the theme (light or dark)
            - stayActive: a boolean value indicating if the button should stay colored after being clicked
        Modifies:
            - Initializes self attributes
        Effects: 
            Initializes a custom PyQt5 button.
            Inherits methods from PyQt's QPushButton.
        """
        super().__init__()

        # Initialize attributes
        self.stayActive = stayActive
        self.icons_paths = icons_paths
        self.light = light
        self.text = text
        self.onClickFunction = None
        self.active = False

        # light style
        self.lightTheme = "QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; color: black;} QPushButton:hover { background-color: rgba(108, 60, 229, 0.3);} QPushButton:pressed { background-color: rgba(108, 60, 229, 0.5);}"
        self.lightThemeSelected = "QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); color: black;}"

        # dark style
        self.darkTheme = "QPushButton { border: none; text-align: left; padding-left: 10px; border-radius: 10px; color: white;} QPushButton:hover { background-color: rgba(108, 60, 229, 0.3);} QPushButton:pressed { background-color: rgba(108, 60, 229, 0.5);}"
        self.darkThemeSelected = "QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); color: white;}"

        # initialize button
        self.setIcon(QIcon(icons_paths[0] if light else icons_paths[1]))
        self.setFixedSize(50, 50)
        self.setIconSize(QSize(25, 25))
        self.setStyleSheet(self.lightTheme if light else self.darkTheme)
        font = QFont("Sans-serif", 11)
        self.setFont(font)
        

    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
            Effects:    Switches between light and dark themes.
                        Switches between black and white icons.
        """
        self.light = not self.light
        if self.active and self.stayActive:
            self.setStyleSheet(self.lightThemeSelected if self.light else self.darkThemeSelected)
        else: 
            self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

        self.setIcon(QIcon(self.icons_paths[0] if self.light else self.icons_paths[1]))

    def expandButton(self):
        """
            Modifies:   self
            Effects:    Expands the dimensions of the button and sets the text.
        """
        self.setText(self.text)
        self.setFixedSize(160, 50)

    def collapseButton(self):
        """
            Modifies:  self
            Effects:   Contracts the dimensions of the button and removes the text.
        """
        self.setText("")
        self.setFixedSize(50, 50)

    def onClick(self, function):
        """
            Requires:   function: a callable object to be called on click event
            Modifies:   self.onClickFunction
            Effects:    Sets the click event function to be executed.
        """
        self.onClickFunction = function
        # Connects the private _onClickAction method, which will execute some actions and then execute the setted onClickFunction
        self.clicked.connect(self._onClickAction)

    def _onClickAction(self):
        """
            Effects:    Executes the onClickFunction and handles button selection/deselection based on settings.
        """
        if self.onClickFunction is not None:
            self.onClickFunction()

        self.selectButton()

    def deselectButton(self):
        """
            Modifies:   self.active: updates the active status
                        self.stylesheet: updates the stylesheet based on the light theme status
            Effects:    Deselects and decolors the button.
        """
        if self.active and self.stayActive:
            self.active = False
            self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

    def selectButton(self):
        """
            Modifies:   self.active: updates the active status
                        self.stylesheet: updates the stylesheet based on the light theme status
            Effects:    Selects and colors the button.
        """
        if not self.active and self.stayActive:
            self.active = True
            self.setStyleSheet(self.lightThemeSelected if self.light else self.darkThemeSelected)

    def clickCall(self):
        """
            Effects:    Simulates a click event on the button.
        """
        self._onClickAction()


