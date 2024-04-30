from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

class MenuButton(QPushButton):
    def __init__(self, icons_paths, text, light = True):

        super().__init__()

        self.setProperty('class', 'menu_button')

        # Initialize attributes
        self.text = text

        # initialize button
        self.setIcon(QIcon(icons_paths[0] if not light else icons_paths[1]))
        self.setFixedSize(50, 50)
        self.setIconSize(QSize(25, 25))

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

