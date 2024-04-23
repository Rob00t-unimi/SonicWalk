from PyQt5.QtWidgets import QComboBox

class CustomSelect(QComboBox):
    def __init__(self, light = True, options = None):
        """
        Requires: 
            - light: a boolean indicating light or dark theme
            - options: a list of strings representing the options for the ComboBox
            - selectedOptionSetter: a setter function to set the selected option
        Modifies:
            - Initializes self attributes
        Effects: 
            Initializes a custom PyQt5 Combo box (select).
            Inherits methods from PyQt's QComboBox.
        """

        super().__init__()

        # Initialize attributes
        self.options = options
        self.selectedOption = None

        self.light = light
        self.lightTheme = """
            QComboBox {
                border: 1px solid #9B90DB;
                border-radius: 15px;
                padding: 10px; 
                background-color: #FFFFFF; 
                selection-background-color: #9B90DB; 
                font-size: 15px;
                color: #4C4C4C;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-left-color: transparent;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                background-color: #9B90DB;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #9B90DB;
                selection-background-color: #9C6BE5;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #4C4C4C;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 10px;
                margin: 20px 0 20px 0;
            }
            QScrollBar::handle:vertical {
                background: #DCDFE4;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                background: none;
            }
            QScrollBar::sub-line:vertical {
                background: none;
            }
        """
        self.darkTheme = """
            QComboBox {
                border: 1px solid #9B90DB; 
                border-radius: 15px;
                padding: 10px; 
                background-color: #333333; 
                selection-background-color: #9B90DB;
                font-size: 15px;
                color: #FFFFFF;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 0px;
                border-left-color: transparent;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                background-color: #9B90DB; 
            }
            QComboBox QAbstractItemView {
                border: 1px solid #9B90DB;
                selection-background-color: #9C6BE5; 
                background-color: #1E1E1E;
                font-size: 13px;
                color: #FFFFFF; 
            }
            QScrollBar:vertical {
                background: #1E1E1E;
                width: 10px;
                margin: 20px 0 20px 0;
            }
            QScrollBar::handle:vertical {
                background: #4D4D4D;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                background: none;
            }
            QScrollBar::sub-line:vertical {
                background: none;
            }
        """

        # Initialize the object
        self.addItems(options)
        self.setStyleSheet(self.lightTheme if light else self.darkTheme)

    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
            Effects:    Switches between black and white icons.
        """
        self.light = not self.light
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
