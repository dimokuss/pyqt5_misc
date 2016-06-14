from PyQt5.QtCore import *

class DseConfigurationModel():
    """
    Represents a specific model for browsing the local workspace / CPD content.
    """
    def __init__(self, context):
        """
        Initializes the ExplorerModel instance.
        context -- The context in which the model is instantiated.
        parent -- The Qt parent of the model.
        """
        self.context = context
        self.framework_service = self.context.get_service("Framework")
        self.item_service = self.context.get_service("Item")
        #Todo: construct logical model here. All necessary ACES data shall be retrieved from DSE services
