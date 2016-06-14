import logging
import time
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dselib.baseui.perspectivebase.perspective import Perspective
from dselib.subsystems.itemmanager.itemmanagermodel import ItemManagerModel
from dselib.subsystems.itemmanager.itemmanagerview import ItemManagerView

class ItemManagerPerspective(Perspective):
    """
    Represents the view perspective for browsing and working with content between the LWS and CPD systems.
    """
    def __init__(self, perspective_name, context):
        """
        Initializes the Explorer instance.
        perspective_name -- The name of the perspective.
        context -- The context in which the perspective is instantiated.
        """
        Perspective.__init__(self, perspective_name, context)
        self.item_manager_model = None
        self.item_manager_view = None
        self.clipboard_service = None
        self.settings_service = None

    def get_title(self):
        """
        Retrieves the title of the perspective to display in the title bar.
        """
        return "ItemManager"

    def initialize_perspective(self):
        """
        Initializes the perspective the first time it is loaded.
        """
        # invoke the base class - this will register the perspective for the commands
        Perspective.initialize_perspective(self)

        # retrieve the framework service so we can get a handle to the lwsManager
        self.framework_service = self.context.get_service("Framework")
        self.item_service = self.context.get_service("Item")
        self.clipboard_service = self.context.get_service("Clipboard")
        self.settings_service = self.context.get_service("Settings")

    def load_view(self):
        """
        Loads the perspective for the first time.
        Overrides base perspective implementation.
        Returns the perspective's view layout.
        """
        # create the model that will represent LWS and CPD content
        self.item_manager_model = ItemManagerModel(self.context)
        self.set_model(self.item_manager_model)
        # create the view that will display the model
        self.item_manager_view = ItemManagerView(self)
        # return the view
        return self.item_manager_view

    def get_model(self):
        """
        returns the model of the perspective
        :return:
        """
        return self.item_manager_model
