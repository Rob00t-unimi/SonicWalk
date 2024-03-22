from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class RecButton(QPushButton):
    def __init__(self, light=True, icons_paths = None, tooltip = None):
        """ 
        Requires: 
            - icons_paths: list of two strings, where the first string represents the path of the black icon and the second string represents the path of the white icon
            - tooltip: a string representing the tooltip text for the button
            - light: a boolean value indicating light or dark theme
        Modifies:
            - Initializes self attributes
        Effects: 
            Initializes a custom PyQt5 recording button.
            Inherits methods from PyQt's QPushButton.
        """
        super().__init__()

        # Attributes initialization
        self.light = light
        self.icons_paths = icons_paths

        # Theme
        self.theme = "QPushButton { border: none; background-color: rgba(150, 150, 150, 30%); border-radius: 40px;} QPushButton:hover { background-color: rgba(108, 60, 229, 40%); } QPushButton:pressed { background-color: rgba(108, 60, 229, 60%); } "
        #self.dark = "QPushButton { border: none; background-color: rgba(50, 50, 50, 30%); border-radius: 40px;} QPushButton:hover { background-color: rgba(108, 60, 229, 40%); } QPushButton:pressed { background-color: rgba(108, 60, 229, 60%); } "

        # initialization of the object
        self.setIcon(QIcon(icons_paths[0] if self.light else icons_paths[1]))
        self.setFixedSize(85, 85)
        self.setIconSize(QSize(25, 25))
        self.setToolTip(tooltip)
        #self.setStyleSheet(self.light if light else self.dark)
        self.setStyleSheet(self.theme)
        self.onClickFunction = None


    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
            Effects:    Switches between black and white icons.
        """
        self.light = not self.light
        self.setIcon(QIcon(self.icons_paths[0] if self.light else self.icons_paths[1]))

    def onClick(self, function):
        """
            Requires:   function: a callable object to be called on click event
            Modifies:   self.onClickFunction
            Effects:    Sets the click event function to be executed.
        """
        self.onClickFunction = function
        # sets directly function to be executed
        self.clicked.connect(function)

    def clickCall(self):
        """
            Effects:    Simulates a click event on the button.
        """
        self.onClickFunction()
