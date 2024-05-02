import json
import os
import shutil
from PyQt5.QtWidgets import *
import sys
sys.path.append("../")

from frames.musicFoldersFrame import MusicFolders
from qt_material import apply_stylesheet, list_themes


class SettingsPage(QWidget):
    def __init__(self, apply_theme, current_theme, reload_archive, icons_manager = None):
        super().__init__()

        self.apply_theme = apply_theme
        self.current_theme = current_theme
        self.global_toggle_theme = None
        self.reload_archive = reload_archive

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        left_box = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_box.setLayout(left_layout)
        layout.addWidget(left_box)
        
        self.MusicFoldersFrame = MusicFolders(icons_manager)
        left_layout.addWidget(self.MusicFoldersFrame)

        left_box.setMinimumWidth(650)

        right_box = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_box.setLayout(right_layout)
        layout.addWidget(right_box)        

        # Style box
        style_box = QWidget()
        style_layout = QVBoxLayout()
        style_box.setLayout(style_layout)
        right_layout.addWidget(style_box)

        style_header = QFrame()
        style_header_layout = QHBoxLayout()
        style_label = QLabel("Style Options:")
        style_label.setContentsMargins(0, 10, 0, 10)
        style_label.setStyleSheet("font-size: 20px")
        style_header_layout.addWidget(style_label)
        style_header.setLayout(style_header_layout)
        style_layout.addWidget(style_header)

        style_combobox = QComboBox()
        themes = list_themes()
        style_combobox.addItems(themes)
        style_combobox.currentIndexChanged.connect(lambda index: self.select_style(style_combobox.itemText(index)))
        style_layout.addWidget(style_combobox)
        try:
            initial_theme_index = themes.index(self.current_theme)
            style_combobox.setCurrentIndex(initial_theme_index)
        except:
            print("no theme selected")

        # Creating a QWidget to hold the repository options
        repo_box = QWidget()
        repo_layout = QVBoxLayout()
        repo_box.setLayout(repo_layout)
        right_layout.addWidget(repo_box)

        # Creating a QFrame for the repository header
        repo_header = QFrame()
        repo_header_layout = QHBoxLayout()
        repo_label = QLabel("Repository Options:")
        repo_label.setContentsMargins(0, 10, 0, 10)
        repo_label.setStyleSheet("font-size: 20px")
        repo_header_layout.addWidget(repo_label)
        repo_header.setLayout(repo_header_layout)
        repo_layout.addWidget(repo_header)

        # Adding a QWidget for the buttons component
        buttons_component = QFrame()
        buttons_layout = QHBoxLayout()
        buttons_component.setLayout(buttons_layout)
        repo_layout.addWidget(buttons_component)

        # Button for copying the repository
        copy_button = QPushButton("Copy Repository")
        copy_button.setProperty('class', 'fill_button_inverted')
        copy_button.clicked.connect(self.copy_repository)
        buttons_layout.addWidget(copy_button)

        # Button for deleting the repository
        delete_button = QPushButton("Delete Repository")
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.confirm_delete_repository)
        buttons_layout.addWidget(delete_button)

        left_layout.addStretch()
        right_layout.addStretch()

        self.folder_path = os.path.join(os.getcwd(), "data")

    def select_style(self, theme):
        try: 
            self.current_theme = theme
            self.apply_theme(theme=theme, write_theme=True)
        except Exception as e:
            print(str(e))

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

                self.reload_archive()
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
