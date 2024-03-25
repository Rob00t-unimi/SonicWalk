import json
from PyQt5.QtWidgets import *
import sys
sys.path.append("../")

from components.customButton import CustomButton
from frames.musicFoldersFrame import MusicFolders

class SettingsPage(QFrame):
    def __init__(self, light=True):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.MusicFoldersFrame = MusicFolders(light=light)
        layout.addWidget(self.MusicFoldersFrame)
        layout.addStretch()

