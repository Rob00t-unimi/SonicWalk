from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy, QAbstractItemView, QHeaderView, QLabel
from PyQt5 import QtGui


class PatientTable(QTableWidget):
    def __init__(self, reducedTable=False, parent=None):
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
        self.reducedTable = reducedTable

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

    def _setupTable(self):
        """
            Effects:    Set up table properties and style.
        """
        self.setColumnCount(1)
        self.setRowCount(len(self.patient_info_data))
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.horizontalHeader().hide()
        self.setVerticalHeaderLabels(["Name", "Surname", "ID", "Group", "Hospital"])

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def setTableData(self, data):
        """
            Requires:   data: a list of tuples, each containing label and corresponding data.
            Effects:    Fills the table with passed data.
        """
        for row, (label_text, data_text) in enumerate(data):
            data_widget = QLabel(data_text)
            self.setCellWidget(row, 0, data_widget)
        