from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy, QAbstractItemView, QHeaderView, QLabel
from PyQt5 import QtGui


class PatientTable(QTableWidget):
    def __init__(self, reducedTable=False, light=True, parent=None):
        """
        Requires:
            - reducedTable: a boolean value indicating the type of table (normal or short)
            - light: a boolean value indicating light or dark theme
        Modifies:
            - Initializes self attributes
        Effects: 
            Initializes a custom PyQt5 Table.
            Inherits methods from PyQt's QTableWidget.
        """
        super().__init__(parent)

        # initialize attributes
        self.light = light
        self.reducedTable = reducedTable

        # Theme styles
        self.lightTheme = "QTableWidget {border: 2px solid  rgba(160, 130, 240, 100%);border-radius: 10px;font-family: Arial; color: black; background-color: rgba(185, 153, 255, 7%); gridline-color:  rgba(160, 130, 240, 100%);}"
        self.darkTheme = "QTableWidget {border: 2px solid rgba(185, 153, 255, 60%);border-radius: 10px;font-family: Arial; color: white; background-color: rgba(185, 153, 255, 7%); gridline-color: rgba(185, 153, 255, 60%);}"

        # Initialize patient info data based on table type
        if reducedTable:
            self.patient_info_data = [
                ("Name:", ""),
                ("Surname:", ""),
                ("ID:", ""),
                ("Group:", ""),
                ("Hospital:", "")
            ]
        else:
            self.patient_info_data = [
                ("Name:", ""),
                ("Surname:", ""),
                ("ID:", ""),
                ("Group:", ""),
                ("Hospital:", ""),
                ("CF:", ""),
                ("Right_Leg_Length:", ""),
                ("Left_Leg_Length:", ""),
                ("Weight:", ""),
                ("Height:", ""),
                ("Gender:", ""),
                ("Date_of_Birth:", "")
            ]

        # initialize the object
        self._setupTable()

        # set datas and the style
        self.setTableData(self.patient_info_data)
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)

    def _setupTable(self):
        """
            Effects:    Set up table properties and style.
        """
        self.setColumnCount(2)
        self.setRowCount(len(self.patient_info_data))
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.setAlternatingRowColors(True)
    
    def toggleTheme(self):
        """
            Modifies:   self.light: toggles the light theme status
                        self.stylesheet: updates the stylesheet based on the light theme status
            Effects:    Switches between light and dark themes.
                        Switches between black and white text color.
        """
        self.light = not self.light
        self.setStyleSheet(self.lightTheme if self.light else self.darkTheme)
        # switch all labels theme
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.cellWidget(row, col)
                if item is not None and isinstance(item, QLabel):
                    item.setStyleSheet("padding-left: 10px; border-radius:10px; background-color: transparent; color: black" if self.light else "padding-left: 10px; border-radius:10px; background-color: transparent; color: white")

    def setTableData(self, data):
        """
            Requires:   data: a list of tuples, each containing label and corresponding data.
            Effects:    Fills the table with passed data.
        """
        for row, (label_text, data_text) in enumerate(data):
            label_widget = QLabel(label_text)
            data_widget = QLabel(data_text)

            label_widget.setFont(QtGui.QFont("Verdana", 11))  
            data_widget.setFont(QtGui.QFont("Verdana", 11))

            label_widget.setStyleSheet("padding-left: 10px; border-radius:10px; background-color: transparent; ; color: black" if self.light else "padding-left: 10px; border-radius:10px; background-color: transparent; ; color: white")  
            data_widget.setStyleSheet("padding-left: 10px; border-radius:10px; background-color: transparent; ; color: black" if self.light else "padding-left: 10px; border-radius:10px; background-color: transparent; ; color: white")  

            self.setCellWidget(row, 0, label_widget)
            self.setCellWidget(row, 1, data_widget)
        