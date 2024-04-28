import json
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
sys.path.append("../")

class NameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a Name")
        
        self.nameLineEdit = QLineEdit()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(self.nameLineEdit)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

class MusicFolders(QWidget):
    def __init__(self):
        super().__init__()

        self.light = True 
        try:
            with open("data/settings.json", "r") as file:
                settings = json.load(file)
            if "light" in settings["theme"]: self.light = True 
            elif "dark" in settings["theme"]: self.light = False 
        except FileNotFoundError:
            print("Settings file not found. Using default theme (light).")
            return True
        
        self.settingsPath = "data/settings.json"
        self.MusicNames = []
        self.MusicPaths = []
        self.loadMusicFolders()
        self.rows = None
        self.noMusicLabel = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.musicFoldersLabel = QLabel("Music Folders:")
        self.musicFoldersLabel.setStyleSheet("font-size: 20px")
        self.musicFrame = QFrame()
        music_frame_layout = QVBoxLayout()
        music_frame_layout.setAlignment(Qt.AlignTop)
        self.musicFrame.setLayout(music_frame_layout)

        self.addMusicButton = QPushButton(text="Add Music Folder")
        self.addMusicButton.setProperty('class', 'fill_button_inverted')
        self.addMusicButton.clicked.connect(self.addMusic)
        self.addMusicButton.setToolTip("Add new Folder")

        headerFrame = QFrame()
        layoutHeader = QHBoxLayout()
        layoutHeader.addWidget(self.musicFoldersLabel)
        layoutHeader.addWidget(self.addMusicButton)
        headerFrame.setLayout(layoutHeader)

        layout = QVBoxLayout()
        layout.addWidget(headerFrame)

        self.tableWidget = QTableWidget()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "Path", "Samples", "Format", "Actions"])
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)

        self.populateMusicFrame()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)


    def populateMusicFrame(self):
        self.tableWidget.setRowCount(0)  # Clear existing rows
        if not self.MusicNames and not self.MusicPaths:
            noMusicLabel = QLabel("No Music Folders Found")
            self.tableWidget.setCellWidget(0, 0, noMusicLabel)
        else:
            for i, (name, path) in enumerate(zip(self.MusicNames, self.MusicPaths)):
                nameLabel = QTableWidgetItem(name)
                pathLabel = QTableWidgetItem(path)
                pathLabel.setToolTip(path)
                
                num_samples, file_format = self.get_music_info(path)
                samplesLabel = QTableWidgetItem(f"{num_samples}")
                formatLabel = QTableWidgetItem(f"{file_format}")
                
                removeButton = QPushButton()
                removeButton.setIcon(QIcon("icons/black/trash.svg" if self.light else "icons/white/trash.svg"))
                removeButton.setProperty('class', 'danger')
                removeButton.clicked.connect(lambda _, n=name, p=path: self.deleteMusicFolder(n, p))
                removeButton.setToolTip("Remove Folder")

                openButton = QPushButton()
                openButton.setIcon(QIcon("icons/black/external-link.svg" if self.light else "icons/white/external-link.svg"))
                openButton.clicked.connect(lambda _, p=path: self.openFolder(p))
                openButton.setToolTip("Open Folder")

                buttonsLayout = QHBoxLayout()
                buttonsLayout.addWidget(openButton)
                buttonsLayout.addWidget(removeButton)
                buttonsLayout.setContentsMargins(0, 0, 0, 0)

                buttonsWidget = QWidget()
                buttonsWidget.setLayout(buttonsLayout)

                self.tableWidget.insertRow(i)
                self.tableWidget.setItem(i, 0, nameLabel)
                self.tableWidget.setItem(i, 1, pathLabel)
                self.tableWidget.setItem(i, 2, samplesLabel)
                self.tableWidget.setItem(i, 3, formatLabel)
                self.tableWidget.setCellWidget(i, 4, buttonsWidget)

    def openFolder(self, path):
        path = os.path.join(os.getcwd(), path)
        print("Opening folder:", path)
        try:
            if sys.platform.startswith('win'):
                # Windows
                os.startfile(path)
            elif sys.platform.startswith('darwin'):
                # macOS
                os.system(f"open '{path}'")
            elif sys.platform.startswith('linux'):
                # Linux
                os.system(f"xdg-open '{path}'")
            else:
                print("Operating system not supported.")
        except Exception as e:
            print(f"Error Opening Folder: {e}")

    def get_music_info(self, folder_path):
        total_samples = 0
        file_format = ""

        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith((".wav", ".mp3")):
                        total_samples += 1
                        if file.endswith(".wav") and ".wav" not in file_format:
                            file_format += " .wav"
                        elif ".mp3" not in file_format:
                            file_format += " .mp3"

            splitted = file_format.split()
            extensions = [ext for ext in ["mp3", "wav"] if ext in file_format]
            file_format = ", ".join(extensions) if extensions else ""

            return total_samples, file_format
        except Exception as e:
            print(f"Error getting music info for folder {folder_path}: {e}")
            return total_samples, file_format               


    def deleteMusicFolder(self, name, path):
        confirmation = QMessageBox()
        confirmation.setIcon(QMessageBox.Warning)
        confirmation.setText(f'Are you sure you want to remove "{name}" folder?')
        confirmation.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation.setDefaultButton(QMessageBox.No)
        response = confirmation.exec_()

        if response == QMessageBox.Yes:
            try:
                with open('data/settings.json', 'r') as f:
                    settings = json.load(f)
                
                music_directories = settings.get('music_directories', [])
                music_names = settings.get('music_names', [])
                
                if path in music_directories:
                    index = music_directories.index(path)
                    del music_directories[index]
                    del music_names[index]
                    
                    # Update the settings dictionary
                    settings['music_directories'] = music_directories
                    settings['music_names'] = music_names
                    
                    # Write the updated settings back to the JSON file
                    with open('data/settings.json', 'w') as f:
                        json.dump(settings, f, indent=4)
                    
                    print(f"Music folder '{name}' at path '{path}' deleted successfully.")
                    self.MusicPaths.remove(path)
                    self.MusicNames.remove(name)
                    self.populateMusicFrame()
                else:
                    print(f"Music folder '{name}' at path '{path}' not found.")
                    
            except FileNotFoundError:
                print("Error: settings.json file not found.")

    def loadMusicFolders(self):
        try:
            with open(self.settingsPath, 'r') as f:
                settings = json.load(f)
            music_directories = settings.get('music_directories', [])
            music_names = settings.get('music_names', [])
            self.MusicPaths = music_directories
            self.MusicNames = music_names
        except FileNotFoundError:
            print("Error: settings.json file not found.")

    def addMusic(self):
        music_folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella musica")

        if music_folder:
            name_dialog = NameDialog(self)
            if name_dialog.exec_():
                music_name = name_dialog.nameLineEdit.text()

                if music_name:
                    with open(self.settingsPath, 'r') as f:
                        settings = json.load(f)

                    settings.setdefault('music_directories', []).append(music_folder)

                    settings.setdefault('music_names', []).append(music_name)

                    with open(self.settingsPath, 'w') as f:
                        json.dump(settings, f, indent=4)
                    
                    self.MusicPaths.append(music_folder)
                    self.MusicNames.append(music_name)
                    self.populateMusicFrame()