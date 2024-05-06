from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy, QAbstractItemView, QHeaderView, QLabel
from PyQt5 import QtGui


class PatientTable(QTableWidget):
    """
    Custom patient table.
    """
    def __init__(self, reducedTable=False):
        """
        Requires:   
            - reducedTable (bool): indicates the type of table (normal or short)

        Modifies:   
            - self

        Effects:    
            - Initializes a custom PyQt5 Table.
            - Inherits methods from PyQt's QTableWidget.
        """
        super().__init__()

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

        self._setupTable()
        self.setTableData(self.patient_info_data)

    def _setupTable(self):
        """
            MODIFIES:   
                - self

            EFFECTS:    
                - Set up table properties and style.
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
            REQUIRES:   
                - data: a list of tuples, each containing label and corresponding data.

            MODIFIES:   
                - self

            EFFECTS:    
                - Fills the table with passed data.
        """
        for row, (label_text, data_text) in enumerate(data):
            data_widget = QLabel(data_text)
            self.setCellWidget(row, 0, data_widget)
        