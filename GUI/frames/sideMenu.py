from PyQt5.QtWidgets import *
import webbrowser
import sys

sys.path.append("../")

from components.menuButton import MenuButton


class SideMenu(QFrame):
    """
    Custom expandable side menu frame. 
    """
    def __init__(self, setActivePage=None, toggleTheme = None, light = True):
        """
        REQUIRES:
            - setActivePage (callable): a callback function for setting the active page called upon clicking an activity button
            - toggleTheme (callable): a callback function for setting the theme
            - light (bool): indicates light or dark theme

        MODIFIES:
            - self

        EFFECTS:
            - Initializes a custom side menu frame.
        """
        super().__init__()

        self.setProperty('class', 'custom_menu')
        # initialize attributes
        self.settings_file = "data/settings.json" 
        self.toggleThemeMain = toggleTheme
        self.menu_expanded = False  # menu state
        self.light = light

        # Define paths for icons
        self.whiteIconPath = "icons/white/"
        self.blackIconPath = "icons/black/"

        # Callback function for setting the active page
        self.setActivePage = setActivePage

        # Initialization of Object
        self.setFixedWidth(60)
        self.sideFrame_layout = QVBoxLayout(self)
        self.sideFrame_layout.setContentsMargins(5, 5, 5, 5)

        # Hamburger menu button
        self.hamburgerMenuButton = MenuButton(name="menu", text="   Menu")
        self.hamburgerMenuButton.clicked.connect(self.hamburgerFunction)
        self.sideFrame_layout.addWidget(self.hamburgerMenuButton)

        # Separation line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setLineWidth(1)
        self.sideFrame_layout.addWidget(line)

        # Create main buttons frame
        self._setupMainButtonsFrame()

        # Create a spacer
        self.sideFrame_layout.addStretch()

        # Setup second buttons frame
        self._setupBottomFrame()

        # Default start with the Analysis page
        self.analysisButton.click()
        self.analysisButton.setChecked(True)

    def _setupMainButtonsFrame(self):
        """
        Modifies:   
            - self

        Effects:    
            - Sets up the frame for the activity buttons.
            - creates the inner frame and the buttons
        """
        # Create frame
        self.inner_frame1 = QFrame()
        self.inner_frame1.setProperty('class', 'custom_menu')
        self.inner_frame1_layout = QVBoxLayout(self.inner_frame1)
        self.inner_frame1_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_frame1_layout.setSpacing(0)

        # Create buttons
        self.analysisButton = MenuButton(name="activity", text="   Analysis")
        self.analysisButton.clicked.connect(lambda: self.selectPage("Analysis"))
        self.archiveButton = MenuButton(name="archive", text="   Archive")
        self.archiveButton.clicked.connect(lambda: self.selectPage("Archive"))
        self.statisticsButton = MenuButton(name="statistics", text="   Statistics")
        self.statisticsButton.clicked.connect(lambda: self.selectPage("Statistics"))
        self.settingsButton = MenuButton(name="settings", text="   Settings")
        self.settingsButton.clicked.connect(lambda: self.selectPage("Settings"))

        self.analysisButton.setCheckable(True)
        self.archiveButton.setCheckable(True)
        self.statisticsButton.setCheckable(True)
        self.settingsButton.setCheckable(True)

        # Add buttons to frame
        self.inner_frame1_layout.addWidget(self.analysisButton)
        self.inner_frame1_layout.addWidget(self.archiveButton)
        # self.inner_frame1_layout.addWidget(self.statisticsButton)        # to implement this page
        self.inner_frame1_layout.addWidget(self.settingsButton)

        # Add inner frame 1 to main frame
        self.inner_frame1_layout.setStretch(0, 1)
        self.sideFrame_layout.addWidget(self.inner_frame1)

    def _setupBottomFrame(self):
        """
        Modifies:   
            - self

        Effects:    
            - Sets up the frame for the bottom buttons
            - Creates the inner frame and the buttons
        """
        # Create frame
        self.inner_frame2 = QFrame()
        self.inner_frame2.setProperty('class', 'custom_menu')
        self.inner_frame2_layout = QVBoxLayout(self.inner_frame2)
        self.inner_frame2_layout.setContentsMargins(0, 0, 0, 0)

        # Create Buttons
        self.themeButton = MenuButton(name="sun", text="  Theme")
        self.themeButton.clicked.connect(self.toggleTheme)
        self.infoButton = MenuButton(name="info", text="   Info")
        self.infoButton.clicked.connect(self._openDocumentation)

        # Add buttons to frame
        self.inner_frame2_layout.addWidget(self.themeButton)
        self.inner_frame2_layout.addWidget(self.infoButton)

        # Add inner frame 2 to main frame
        self.sideFrame_layout.addWidget(self.inner_frame2)

    def hamburgerFunction(self):
        """
        Modifies:   
            - self

        Effects:   
            - Expands/Collapses the menu and the buttons in it
        """
        self.menu_expanded = not self.menu_expanded
        self.setFixedWidth(170 if self.menu_expanded else 60)

        if self.menu_expanded:
            self.hamburgerMenuButton.expandButton()
            self.analysisButton.expandButton()
            self.archiveButton.expandButton()
            self.statisticsButton.expandButton()
            self.settingsButton.expandButton()
        else:
            self.hamburgerMenuButton.collapseButton()
            self.analysisButton.collapseButton()
            self.archiveButton.collapseButton()
            self.statisticsButton.collapseButton()
            self.settingsButton.collapseButton()
            
    def selectPage(self, page):
        """
        Requires:   
            - page (str): a string from "Analysis, Settings, Archive, Statistics"

        Modifies:   
            - self

        Effects:    
            - Deselects buttons based on the selected page.
            - Sets the active page.
        """
        self.analysisButton.setChecked(False)
        self.archiveButton.setChecked(False)
        self.statisticsButton.setChecked(False)
        self.settingsButton.setChecked(False)

        if page == "Analysis": self.analysisButton.setChecked(True)
        elif page == "Settings":  self.settingsButton.setChecked(True)
        elif page == "Archive": self.archiveButton.setChecked(True)
        elif page == "Statistics": self.statisticsButton.setChecked(True)

        if self.setActivePage is not None:
            self.setActivePage(page)
        print(page)

    def toggleTheme(self):
        """
        MODIFIES:
            - self.light
            - GUI theme

        EFFECTS:
            - modifies the GUI theme (light/dark)
            - invert self.light
        """
        self.light = not self.light
        try:
            self.toggleThemeMain()
        except Exception as e:
            print(str(e))

    def _openDocumentation(self):
        """
        Effects:    
            - Opens the HTML documentation in a web browser
        """
        try:
            webbrowser.open('documentation.html')
        except Exception as e:
            print("Error opening documentation file:", e)


