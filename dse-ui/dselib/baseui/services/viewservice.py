from PyQt5.QtCore import *

from dselib.baseui.services.dseservice import AcesService


class ViewService(AcesService):
    """
    Represents the service responsible for handling selection and other view-related activities.
    """
    selection_changed = pyqtSignal(object)
    
    def __init__(self, context, service_id):
        """
        Initializes the ViewService instance.
        context -- The context in which the service is loaded.
        service_id -- A string identifying the service.
        """
        AcesService.__init__(self, context, service_id)
        self.selected_item = None
        self.selected_context = None
    
    def set_selected_item(self, selected_item):
        """
        Sets the currently selected item.  This will trigger an update for BaseUI items that depend on the current selection.
        selected_item -- The item that will be used as the selected item within the view context.
        """
        self.selected_item = selected_item
        self.selection_changed.emit(self.selected_item)
       
    def get_selected_item(self):
        """
        Retrieves the currently selected item.
        """
        return self.selected_item
    
    def update_selected_item(self):
        """
        Allows callers to request a system-wide update based on changes to the selected item.
        """
        self.selection_changed.emit(self.selected_item)