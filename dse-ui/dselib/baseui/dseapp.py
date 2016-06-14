from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QSplitter, QWidget
from dselib.baseui.mainwidget import MainWidget
from dselib.baseui.perspectivebase.perspectiveview import PerspectiveView
from dselib.baseui.services.settingsservice import MainWindowSettings


class DseApp(QObject):
    """
    Represents the controller for a top-level window.
    """
    def __init__(self, app_context):
        """
        Initializes the DseApp instance.
        :param app_context: The application context in which the instance lives.
        """
        QObject.__init__(self)
        self.app_context = app_context
        self.active_perspective = None
        self.active_perspective_view = None
        self.dse_win = None
        self.loaded_perspectives = {}

        # store services we need
        self.perspective_service = self.app_context.get_service("Perspective")
        self.settings_service = self.app_context.get_service("Settings")

    def get_context(self):
        """
        Retrieves the perspective context of the app.
        :returns: perspective_context
        """
        return self.app_context

    def _on_window_closed(self):
        # save window settings
        self._write_window_settings()

    def create_view(self, initial_perspective=None):
        """
        Creates and shows the top-level window associated with the controller.
        :param initial_perspective: the perspective to show when creating the new view.
        """
        self.dse_win = DseAppWindow(self)
        self._read_window_settings()
        self.dse_win.closed.connect(self._on_window_closed)
        # attach the main window to the context
        self.app_context.set_window(self.dse_win)

        if initial_perspective is not None:
            self.switch_perspective(initial_perspective)
        self.dse_win.show()

    def get_active_perspective(self):
        """
        Retrieves the active perspective of the application.
        :returns: The controller of the perspective currently active in the view.
        """
        return self.active_perspective

    def switch_perspective(self, perspective_name):
        """
        Switches the application window to display the perspective with the given name.
        :param perspective_name: The name of the perspective to load into the current view.
        """
        # do we have a local instantiation of this perspective yet?
        if perspective_name in self.loaded_perspectives:
            perspective = self.loaded_perspectives[perspective_name]
        else:
            # we haven't instantiated the perspective in this view yet
            # so we have to ask the perspective service to instantiate a new perspective for us
            perspective = self.perspective_service.load_perspective(perspective_name)

        # the entity returned from loading is the perspective controller
        # this will have a method to retrieve the view for the perspective
        perspective_view = perspective.load_view()
        if not isinstance(perspective_view, PerspectiveView):
            raise ValueError("Unable to switch perspectives, perspective view provided "
                             "is not a valid perspective view!")

        # create the main content containing the perspective and feedback view
        main_content = self._create_main_content(perspective_view)
        # re-parent the perspective view
        self.dse_win.main_widget.set_view(main_content)
        if self.active_perspective_view is not None:
            self.active_perspective_view.hide()

        # now show the new perspective
        self.active_perspective = perspective
        self.active_perspective_view = perspective_view
        main_content.show()
        # update the title
        self.dse_win.setWindowTitle("DSE - " + self.active_perspective.get_title())

    def _create_main_content(self, perspective_view):
        """
        Creates the main content from the given view the perspective created.
        The main content area in the main widget is composed of the perspective view and the feedback view.
        :param perspective_view: the view created by the perspective controller.
        :returns: An aggregate widget consisting of the perspective view and the feedback view that can be hosted
        by the main widget.
        """
        perspective_context = perspective_view.controller.get_context()
        perspective_definition = perspective_view.controller.get_definition()

        return perspective_view

    def _on_perspective_title_changed(self):
        """
        Invoked when the perspective title changes so we can update the window.
        """
        self.dse_win.setWindowTitle("DSE - " + self.active_perspective.get_title())

    def _write_window_settings(self):
        """
        Saves the window settings for the user.
        """
        self.settings_service.set_user_settings('main_window', MainWindowSettings.MainWindowSize,
                                                self.dse_win.size())
        self.settings_service.set_user_settings('main_window', MainWindowSettings.MainWindowPosition,
                                                self.dse_win.pos())

    def _read_window_settings(self):
        """
        Reads the saved window settings for the user.
        """
        window_size = self.settings_service.get_user_settings('main_window', MainWindowSettings.MainWindowSize)
        window_pos = self.settings_service.get_user_settings('main_window', MainWindowSettings.MainWindowPosition)
        if window_size:
            self.dse_win.resize(window_size)
        else:
            self.dse_win.resize(QSize(1600, 900))
        if window_pos:
            self.dse_win.move(window_pos)
        else:
            self.dse_win.move(QPoint(30, 30))

        if not window_size or not window_pos:
            self._write_window_settings()


class DseAppWindow(QMainWindow):
    """
    Represents the main window for the ACES application.
    There can be multiple ACES applications open within the same process instance.
    """
    # event raised when the window is closing
    closing = pyqtSignal()

    # event raised when the window is closed
    closed = pyqtSignal()

    def __init__(self, controller, parent=None):
        """
        Initializes the AcesAppWindow instance.
        :param controller: The AcesApp controller of the view.
        :param parent: The Qt parent of the view.
        """
        QMainWindow.__init__(self, parent)
        self.controller = controller
        self.setWindowTitle("DSE")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.set_style()

        # build the start page
        start_page = QWidget()

        # set up the main widget that will host the ribbon and content
        self.main_widget = MainWidget(start_page, self)
        # set up the main content
        self.setCentralWidget(self.main_widget)

    def set_style(self):
        """
        sets the style sheet of the main aces application
        """
        style_sheet = """
                        #centralwidget{
                        background-color: #FFF;
                        color: #333;
                        }
                        """
        self.setStyleSheet(style_sheet)

    def get_controller(self):
        """
        :returns: the controller for the window.
        """
        return self.controller

    def closeEvent(self, event):
        """
        QMainWindow override.
        Invoked when the window is about to close.
        :param event: the QCloseEvent signal
        """
        # raise the closing signal to give subscribers the opportunity to perform actions before closing the Window
        self.closing.emit()
        event.accept()
        self.closed.emit()
