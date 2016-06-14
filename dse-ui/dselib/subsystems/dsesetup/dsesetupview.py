from PyQt5.QtWidgets import QVBoxLayout, QLabel
from dselib.baseui.perspectivebase.perspectiveview import PerspectiveView


class DseSetupView (PerspectiveView):
    """
    Represents the main perspective layout for the explorer perspective.
    """

    def __init__(self, controller, parent=None):
        """
        Initializes the ItemManager instance.
        controller -- The controller that will manage the view.
        parent -- The Qt parent of the view.
        """
        PerspectiveView.__init__(self, controller, parent)

        self.settings_service = self.controller.get_context().get_service("Settings")

        # setup the layout, which will consist of the explorer tree, a vertical splitter, and the content area
        self.layout = QVBoxLayout()
        model = controller.get_model()
        hello_label = QLabel("DSE Setup")
        self.layout.addWidget(hello_label)
        self.setLayout(self.layout)
        self._restore_layout()

    def _restore_layout(self):
        """
        Restores the layout of the view.
        """
        pass

    def _save_layout(self):
        """
        Saves the layout of the view.
        """
        pass

    def show_view(self, view):
        """
        Shows the specified view in the content area.
        view -- The view to show in the content area.
        """
        # remove the existing content
        existing_content = self.details_content_view.get_content()
        if existing_content != None:
            existing_content.deleteLater()

        self.details_content_view.set_content(view)