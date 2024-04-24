import json
import os
import shutil
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
        # left_layout.addStretch()

        # Add a component with two buttons
        buttons_component = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_component.setLayout(buttons_layout)
        left_layout.addWidget(buttons_component)

        # Button for deleting the repository
        delete_button = QPushButton("Delete Repository")
        delete_button.clicked.connect(self.confirm_delete_repository)
        buttons_layout.addWidget(delete_button)

        # Button for copying the repository
        copy_button = QPushButton("Copy Repository")
        copy_button.clicked.connect(self.copy_repository)
        buttons_layout.addWidget(copy_button)

        self.folder_path = os.path.join(os.getcwd(), "data")

    def confirm_delete_repository(self):
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setText("Are you sure you want to delete the repository?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)
        response = confirm_dialog.exec_()
        if response == QMessageBox.Yes:
            self.delete_repository()

    def delete_repository(self):
        path = os.path.join(self.folder_path, "archive")
        if os.path.exists(self.folder_path):
            try:
                shutil.rmtree(path)
                os.mkdir(path)
                QMessageBox.information(self, "Repository Deleted", "Repository deleted successfully.")

                json_path = os.path.join(self.folder_path, "dataset.json")
                with open(json_path, 'w') as json_file:
                    json_file.write('[]')  # Write an empty JSON object

            except Exception as e:
                QMessageBox.warning(self, "Deletion Error", f"An error occurred while deleting the repository: {e}")
        else:
            QMessageBox.warning(self, "Repository Not Found", "Repository not found.")
            
    def copy_repository(self):
        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if destination_folder:
            try:
                # Perform copy operation to destination_folder
                destination_path = os.path.join(destination_folder, os.path.basename(self.folder_path))
                shutil.copytree(self.folder_path, destination_path)
                os.remove(os.path.join(destination_folder,"data", "settings.json"))
                QMessageBox.information(self, "Repository Copied", "Repository copied successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Copy Error", f"An error occurred while copying the repository: {e}")
