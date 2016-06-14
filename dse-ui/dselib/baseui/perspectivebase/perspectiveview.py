from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget


class PerspectiveView(QWidget):
    """
    Represents the base class for a perspective's view.
    """

    # signal raised when the widget is shown / hidden
    # the passed boolean will be True when the widget is being shown and False otherwise
    perspective_visibility_changed = pyqtSignal(bool)
    
    def __init__(self, controller, parent = None):
        """
        Initializes the PerspectiveView instance.
        controller -- The controller that will manage the view.
        parent -- The Qt parent of the view.
        """
        QWidget.__init__(self, parent)
        self.controller = controller
        
    def showEvent(self, show_event):
        """
        QWidget override.
        Event raised when the widget is shown.
        """
        self.perspective_visibility_changed.emit(True)
    
    def hideEvent(self, hide_event):
        """
        QWidget override.
        Event raised when the widget is hidden.
        """
        self.perspective_visibility_changed.emit(False)
        
    def get_controller(self):
        """
        Retrieves the controller for the view.
        """
        return self.controller
