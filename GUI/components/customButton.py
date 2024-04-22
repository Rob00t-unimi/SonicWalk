from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

class CustomButton(QPushButton):
    def __init__(self, dimensions = [100, 40], icons_paths = None, iconDimensions = [25, 25], text = None, light = True, stayActive = False, onClickDeactivate = True):
        """ 
        Requires: 
            - dimensions: list of two integers specifying width and height
            - icons_paths: list of two strings, where the first string represents the path of the black icon and the second string represents the path of the white icon
            - iconDimensions: list of two integers specifying width and height of the icon
            - text: a string representing the button text
            - light: a boolean value indicating the theme (light or dark)
            - stayActive: a boolean value indicating if the button should stay colored after being clicked
            - onClickDeactivate: a boolean value indicating if the button should be deselected on click when stayActive is True
        Modifies:
            - Initializes self attributes
        Effects: 
            Initializes a custom PyQt5 button.
            Inherits methods from PyQt's QPushButton.
        """
        super().__init__()

        # Attributes initialization
        self.onClickFunction = None
        self.active = False

        self.light = light
        self.stayActive = stayActive
        self.onClickDeactivate = onClickDeactivate
        self.icons_paths = icons_paths

        # light style
        self.lightTheme = "QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 30%); color: black;} QPushButton:hover { background-color: rgba(108, 60, 229, 50%); } QPushButton:pressed { background-color: rgba(108, 60, 229, 70%); }"
        self.lightThemeSelected = "QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 65%); color: black;}"

        # dark style
        self.darkTheme = "QPushButton { border: none; padding-left: 10px; border-radius: 10px; background-color: rgba(108, 60, 229, 30%); color: white;} QPushButton:hover { background-color: rgba(108, 60, 229, 50%); } QPushButton:pressed { background-color: rgba(108, 60, 229, 70%); }"
        self.darkThemeSelected = "QPushButton { border: none; border-radius: 10px; background-color: rgba(108, 60, 229, 50%); color: white;}"

        # initialization of the object
        if icons_paths is not None:
            self.setIcon(QIcon(icons_paths[0] if light else icons_paths[1]))
            self.setIconSize(QSize(iconDimensions[0], iconDimensions[1]))
        self.setFixedSize(dimensions[0], dimensions[1])
        self.setStyleSheet(self.lightTheme if light else self.darkTheme)
        font = QFont("Sans-serif", 11)
        self.setFont(font)
        if text is not None:
            self.setText(text)


    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
            Effects:    Switches between light and dark themes.
                        Switches between black and white icons.
        """
        self.light = not self.light
        if self.stayActive and self.active :
            self.setStyleSheet(self.lightThemeSelected if self.light else self.darkThemeSelected)
        else: 
            self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        if self.icons_paths is not None:
            self.setIcon(QIcon(self.icons_paths[0] if self.light else self.icons_paths[1]))

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

        if self.onClickDeactivate: 
            if self.active:
                self.deselectButton()
            else:
                self.selectButton()
        else:
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

