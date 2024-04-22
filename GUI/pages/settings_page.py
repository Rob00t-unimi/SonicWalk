import json
from PyQt5.QtWidgets import *
import sys
sys.path.append("../")

from components.customButton import CustomButton
from frames.musicFoldersFrame import MusicFolders

class SettingsPage(QFrame):
    def __init__(self, light=True):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        left_box = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_box.setLayout(left_layout)
        layout.addWidget(left_box)
        
        self.MusicFoldersFrame = MusicFolders(light=light)
        left_layout.addWidget(self.MusicFoldersFrame)

        left_box.setFixedWidth(500)
        layout.addStretch()
        left_layout.addStretch()

