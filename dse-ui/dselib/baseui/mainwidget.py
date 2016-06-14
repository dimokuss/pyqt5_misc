from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QToolButton, QSizePolicy, QMenu, QAction
from PyQt5.QtCore import *
from dselib.baseui.contentview import ContentView

class MainWidget(QWidget):
    """
    Represents the main content area for a ribbon-controlled window.
    This widget controls how the ribbon is shown to the user.
    When the Start Page is selected, the ribbon hides the ribbon bar to show a full-tab view.
    When any other ribbon tab is selected, the ribbon shows the ribbon bar plus content that is set by the
    application based on which perspective is being shown.
    """
    command_invoked = pyqtSignal(str)

    def __init__(self, start_page, parent=None):
        """
        Initializes the MainWidget instance.
        :param start_page: The widget defining the full-tab view to show when the Start tab is selected.
        :param parent: The AcesAppWindow instance that is hosting this widget.
        """
        QWidget.__init__(self, parent)
        self.content = ContentView()
        rc_layout = QVBoxLayout()
        rc_layout.addWidget(self.content)
        rc_layout.setContentsMargins(0, 0, 0, 0)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content)
        self.setObjectName("main_widget")
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)

    def set_view(self, view):
        """
        Sets the view in the content portion of the ribbon widget.
        :param view: The widget to set in the content portion of the ribbon widget.
        """
        self.content.set_content(view)

