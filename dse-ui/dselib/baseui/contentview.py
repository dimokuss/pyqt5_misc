from PyQt5.QtWidgets import QVBoxLayout, QWidget

class ContentView(QWidget):
    """
    Represents a generic container for holding views in ACES.
    """
    def __init__(self, parent=None):
        """
        Initializes the ContentView instance.
        :param parent: The Qt parent of the content view.
        """
        QWidget.__init__(self, parent)
        self.setObjectName("ContentView")
        self.content = None
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)
        
    def get_content(self):
        """
        Retrieves the content of the view.
        :returns: The widget that was set as the content of the content view.
        """
        return self.content
    
    def set_content(self, content):
        """
        Sets the content of the view.
        :param content: The widget that will be set as the content of the view.
        """
        # remove the existing content
        if self.content is not None:
            self.layout.removeWidget(self.content)
            self.content.setParent(None)
        
        # add the new content
        self.content = content
        
        if self.content is not None:
            self.layout.addWidget(self.content)
