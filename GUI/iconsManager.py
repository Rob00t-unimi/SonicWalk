from PyQt5.QtGui import QIcon

class IconsManager:
    """
    Manages the loading and switching of icons for the application interface.
    """
    def __init__(self):
        """
        MODIFIES: 
            - self

        EFFECTS:   
            - initialize the object with icons paths
        """

        self.color = "black"

        self.blackpath = "icons/black/"
        self.whitepath = "icons/white/"

        self.trash_name = "trash.svg"
        self.link_name = "external-link.svg"
        self.minus_cirle_name = "minus-circle.svg"
        self.plus_cirle_name = "plus-circle.svg"
        self.play_name = "play.svg"
        self.save_name = "save.svg"
        self.moon_name = "moon.svg"
        self.sun_name = "sun.svg"
        self.menu_name = "menu.svg"
        self.activity_name = "activity.svg"
        self.archive_name = "archive.svg"
        self.info_name = "info.svg"
        self.statistics_name = "bar-chart-2.svg"
        self.settings_name = "settings.svg"
        self.stop_name = "square.svg"

        self.stop_link = "icons/"+ self.stop_name
        # self.set_black()

    def switch_icons_color(self):
        """
        MODIFIES: 
            - self

        EFFECTS:  
            - Switches the color of the icons attributes between black and white internally in this class.
        """
        if self.color == "black": self.set_white()
        else: self.set_black()

    def set_white(self):
        """
        MODIFIES: 
            - self

        EFFECTS:  
            - Loads all icons from the white icon directory.
        """
        self.color = "white"
        self.trash = QIcon(self.whitepath+self.trash_name)
        self.link = QIcon(self.whitepath+self.link_name)
        self.minus_circle = QIcon(self.whitepath + self.minus_cirle_name)
        self.plus_circle = QIcon(self.whitepath + self.plus_cirle_name)
        self.play = QIcon(self.whitepath + self.play_name)
        self.save = QIcon(self.whitepath + self.save_name)
        self.moon = QIcon(self.whitepath + self.moon_name)
        self.sun = QIcon(self.whitepath + self.sun_name)
        self.menu = QIcon(self.whitepath + self.menu_name)
        self.activity = QIcon(self.whitepath + self.activity_name)
        self.archive = QIcon(self.whitepath + self.archive_name)
        self.info = QIcon(self.whitepath + self.info_name)
        self.statistics = QIcon(self.whitepath + self.statistics_name)
        self.settings = QIcon(self.whitepath + self.settings_name)
        self.stop = QIcon(self.stop_link)

    def set_black(self):
        """
        MODIFIES: 
            - self

        EFFECTS:  
            - Loads all icons from the black icon directory.
        """
        self.color = "black"
        self.trash = QIcon(self.blackpath+self.trash_name)
        self.link = QIcon(self.blackpath+self.link_name)
        self.minus_circle = QIcon(self.blackpath + self.minus_cirle_name)
        self.plus_circle = QIcon(self.blackpath + self.plus_cirle_name)
        self.play = QIcon(self.blackpath + self.play_name)
        self.save = QIcon(self.blackpath + self.save_name)
        self.moon = QIcon(self.blackpath + self.moon_name)
        self.sun = QIcon(self.blackpath + self.sun_name)
        self.menu = QIcon(self.blackpath + self.menu_name)
        self.activity = QIcon(self.blackpath + self.activity_name)
        self.archive = QIcon(self.blackpath + self.archive_name)
        self.info = QIcon(self.blackpath + self.info_name)
        self.statistics = QIcon(self.blackpath + self.statistics_name)
        self.settings = QIcon(self.blackpath + self.settings_name)
        self.stop = QIcon(self.stop_link)

    def getIcon(self, name):
        """
        REQUIRES: 
            - name (str): The name of the icon.

        EFFECTS: 
            - Returns QIcon object corresponding to the specified icon name.
        """
        return getattr(self, name)



