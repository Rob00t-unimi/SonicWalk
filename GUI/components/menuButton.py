from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize

class MenuButton(QPushButton):
    """
    Custom expandable menu button with the class property menu_button and an icon_name property.
    """
    def __init__(self, name, text):
        """
        Requires:   
            - name (string): indicates the name to assing in the "icon_name" property
            - text (string): indicates the text of the button

        Modifies:   
            - self

        Effects:    
            - Initializes a custom PyQt5 Button.
            - Inherits methods from PyQt5's Button.
        """
        super().__init__()

        self.setProperty('class', 'menu_button')
        self.setProperty('icon_name', name)
        self.text = text
        self.setFixedSize(50, 50)
        self.setIconSize(QSize(25, 25))

    def expandButton(self):
        """
            Modifies:   
                - self

            Effects:    
                - Expands the dimensions of the button and sets the text.
        """
        self.setText(self.text)
        self.setFixedSize(160, 50)

    def collapseButton(self):
        """
            Modifies:  
                - self

            Effects:   
                - Contracts the dimensions of the button and removes the text.
        """
        self.setText("")
        self.setFixedSize(50, 50)

