from enum import Enum
from PyQt5.QtCore import *

from dselib.baseui.services.dseservice import DseService


class ClipboardMode(Enum):
    """
    Represents an enumeration for specifying the mode that the clipboard is currently in.
    """
    Cut = 1,
    Copy = 2

class ClipboardService(DseService):
    """
    Represents a service hosting a clipboard for copying and pasting objects in-process.
    """
    # Invoked when a clipboard operation is complete.
    operation_complete = pyqtSignal(ClipboardMode, list)
    
    # Invoked when a clipboard operation is canceled by starting a new operation without ending the original one.
    operation_canceled = pyqtSignal(ClipboardMode, list)
    
    def __init__(self, context, service_id):
        """
        Initializes the ClipboardService instance.
        context -- The context in which the service lives.
        service_id -- A string defining the id of the service.
        """
        DseService.__init__(self, context, service_id)
        self.clipboard = []
        self.clipboard_mode = ClipboardMode.Copy
        self.in_transaction = False
    
    def start_operation(self, clipboard_mode):
        """
        Starts a new cut / copy operation on the clipboard.
        clipboard_mode -- A ClipboardMode enumerated object describing whether the operation should be a Cut or Copy.
        """
        if self.in_transaction:
            # we were previously in a transaction, so we cancel that one and create a new one
            # this can happen, for example, if the user cuts something, never pastes
            # but then copies something else
            self.operation_canceled.emit(self.clipboard_mode, self.clipboard)
        
        self.clipboard = []
        self.clipboard_mode = clipboard_mode
        self.in_transaction = True
        
    def add_item_to_clipboard(self, item):
        """
        Adds an item to the clipboard contents.
        This can only be invoked after starting a clipboard operation.
        item -- The item to add to the clipboard.
        """
        # at the moment we store the raw item, but it might be nice in the future to use the mime data objects
        # so that we can support scenarios like copying an item revision from ACES and pasting it into notepad.
        if not self.in_transaction:
            raise RuntimeError("Unable to add items to the clipboard before a clipboard operation has been started!")
        
        self.clipboard.append(item)
        
    def get_clipboard_contents(self):
        """
        Retrieves the current contents of the clipboard as a list of objects.
        This method is used for inspection of the clipboard, but not to complete an operation.
        returns -- A list of objects that are currently on the clipboard.
        """
        return self.clipboard
    
    def end_operation(self):
        """
        Ends the current operation on the clipboard and raises the operation_complete signal.
        Copy operations can be completed multiple times to perform multiple pastes with the same content.
        If the current operation is a cut, the clipboard will be cleared.
        If the current operation is a copy, the clipboard contents will remain.
        """
        # end the operation
        self.operation_complete.emit(self.clipboard_mode, self.clipboard)
        
        # if it's a cut, clear the clipboard
        self.in_transaction = False
        if self.clipboard_mode == ClipboardMode.Cut:
            self.clipboard = []
    
    def is_in_operation(self):
        """
        Returns True if the clipboard is in the middle of an operation, False otherwise.
        """    
        return self.in_transaction
