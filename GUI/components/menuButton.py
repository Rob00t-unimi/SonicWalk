from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize

class MenuButton(QPushButton):
    def __init__(self, name, text):

        super().__init__()

        self.setProperty('class', 'menu_button')

        # Initialize attributes
        self.text = text

        # initialize button
        self.setProperty('icon_name', name)
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

