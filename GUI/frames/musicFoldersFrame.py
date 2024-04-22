import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


import sys
sys.path.append("../")

from components.customButton import CustomButton

## DA SISTEMARE GRAFICAMENTE E DA AGGIUNGERE TOGGLE THEME

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

class MusicFolders(QFrame):
    def __init__(self, light=True):
        super().__init__()
        self.settingsPath = "data/settings.json"
        self.MusicNames = []
        self.MusicPaths = []
        self.loadMusicFolders()
        self.rows = None
        self.noMusicLabel = None
        self.light = light

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(
            "MusicFolders {"
            "   border-bottom-left-radius: 15px;"
            "   border-bottom-right-radius: 15px;"
            "   background-color: #B6C2CF;"
            "}"
        )

        self.musicFoldersLabel = QLabel("Music Folders:")
        self.font = QFont("Sans-serif", 16)
        self.musicFoldersLabel.setFont(self.font)
        self.musicFrame = QFrame()
        self.musicFrame.setStyleSheet(
            """
            QFrame {
               background-color: transparent;
              
            }
            QLabel {
                background-color: rgba(0, 0, 0, 0%);
            }
            """
        )
        self.musicFrame.setLayout(QVBoxLayout())  # Set layout for musicFrame
        self.scrollArea = QScrollArea()
        self.scrollArea.setStyleSheet(
            """
            QScrollArea {
                border: 2px solid rgba(160, 130, 240, 80%);
                border-radius: 15px;
                background-color: transparent;
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
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.musicFrame)

        self.populateMusicFrame()

        self.addMusicButton = CustomButton(text="Add Music Folder", light=light, dimensions=[200, 50])
        self.addMusicButton.clicked.connect(self.addMusic)
        self.addMusicButton.setToolTip("Add new Folder")


        headerFrame = QFrame()
        headerFrame.setStyleSheet(
            """
            QFrame {
               background-color: rgba(0, 0, 0, 0%);
               border-radius: 15px;
            }
            """
        )
        layoutHeader = QHBoxLayout()
        layoutHeader.addWidget(self.musicFoldersLabel)
        layoutHeader.addWidget(self.addMusicButton)
        headerFrame.setLayout(layoutHeader)

        layout = QVBoxLayout()
        layout.addWidget(headerFrame)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)



    def populateMusicFrame(self):

        if self.noMusicLabel is not None:
            self.noMusicLabel.deleteLater()
            self.noMusicLabel = None

        if self.rows is not None:
            for row in self.rows:
                for widget in row:
                    widget.deleteLater()

        self.rows = []

        if not self.MusicNames and not self.MusicPaths:
            self.noMusicLabel = QLabel("No Music Folders Found")
            self.musicFrame.layout().addWidget(self.noMusicLabel)
        else:
            for name, path in zip(self.MusicNames, self.MusicPaths):
                rowLayout = QHBoxLayout()

                font = QFont("Sans-serif", 12)
                nameLabel = QLabel(name)
                nameLabel.setFont(font)
                nameLabel.setMaximumWidth(100)
                nameLabel.setToolTip(name)
                nameLabel.setWordWrap(False)
                nameLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Create path label
                pathLabel = QLabel(path)
                # pathLabel.setFont(font)
                pathLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Imposta l'allineamento del testo a sinistra
                pathLabel.setMaximumWidth(220)  # Imposta una larghezza fissa per il percorso
                pathLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                pathLabel.setToolTip(path)  # Mostra il percorso completo al passaggio del mouse
                pathLabel.setWordWrap(False)  # Disabilita il word wrapping


                removeButton = CustomButton(text="", light=self.light, icons_paths=["icons/black/trash.svg", "icons/white/trash.svg"], dimensions=[50, 50])
                removeButton.setStyleSheet("QPushButton { text-align: center; border-radius: 10px; background-color: rgba(255,0,0,30%);} QPushButton:hover { background-color: rgba(255,0,0,50%); } QPushButton:pressed { background-color: rgba(255,0,0,70%); ")
                removeButton.clicked.connect(lambda _, n=name, p=path: self.deleteMusicFolder(n, p))
                removeButton.setToolTip("Remove Folder")

                rowLayout.addWidget(nameLabel)
                rowLayout.addStretch()
                rowLayout.addWidget(pathLabel)
                rowLayout.addStretch()
                rowLayout.addWidget(removeButton)

                rowLayout.setSizeConstraint(QLayout.SetMaximumSize)

                row = [nameLabel, pathLabel, removeButton]
                rowLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                self.rows.append(row)

                self.musicFrame.layout().addLayout(rowLayout)


    def deleteMusicFolder(self, name, path):
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