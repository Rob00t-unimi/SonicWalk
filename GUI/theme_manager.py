# theme_manager.py

import json

class ThemeManager:
    def __init__(self, settings_file="settings.json"):
        
        # Carica le ultime impostazioni del tema dal json
        def load_settings():
            try:
                with open(self.settings_file, "r") as file:
                    settings = json.load(file)
                    light_theme = settings.get("light_theme", True)
            except FileNotFoundError:
                print("Error loading settings json file")
                light_theme = True  # Impostazione predefinita se il file non esiste

            return light_theme

        self.settings_file = settings_file
        self.light_theme = load_settings()

    def toggle_theme(self):

        # salva le nuove impostazioni del tema nel json
        def save_settings():
            settings_to_save = {
                "light_theme": self.light_theme
            }

            with open(self.settings_file, "w") as file:
                json.dump(settings_to_save, file)

        self.light_theme = not self.light_theme
        save_settings()

        return self.getTheme()

    def getTheme(self):
        """ 
            Returns: path of css theme file
                     path of icon pack folder
        """

        if self.light_theme:
            # Light Theme
            theme_css_path = "light_theme.css"
            icon_pack_folder_path = "icons/black/"
        else:
            # Dark Theme
            theme_css_path = "dark_theme.css"
            icon_pack_folder_path = "icons/white/"
    
        return theme_css_path, icon_pack_folder_path





    