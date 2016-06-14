from PyQt5.Qt import pyqtSignal

class Perspective():
    """
    Represents the base perspective plug-in for all perspectives in ACES.
    """
    # signal raised when the active view within the perspective changes
    # this allows the ACES base ui to activate the right ribbon items
    active_view_changed = pyqtSignal()
    
    # signal raised when the title of the window should change
    title_changed = pyqtSignal()    
    
    def __init__(self, name, context):
        """
        Initializes the Perspective instance.
        name -- The name of the perspective.
        context -- The context in which the perspective will reside.
        """
        self.context = context
        self.name = name
        self.definition = None
        self.model = None

    def get_name(self):
        """
        Retrieves the name of the perspective.
        """
        return self.name
        
    def get_title(self):
        """
        Retrieves the title of the perspective to display in the title bar.
        """
        raise NotImplementedError
        
    def initialize_perspective(self):
        """
        Performs initialization the first time the perspective is loaded.
        Inheriting classes MUST call this method.
        """
        pass
        
    def load_view(self):
        """
        Retrieves the root view of the perspective that will be plugged into the ACES content area.
        """
        raise NotImplementedError

    def get_definition(self):
        """
        Retrieves the perspective's definition.
        """    
        return self.definition
    
    def set_definition(self, definition):
        """
        Sets the perspective's definition.
        definition -- The PerspectiveDefinition instance defining the perspective.
        """
        self.definition = definition

    def get_context(self):
        """
        Retrieves the context associated with the perspective.
        """
        return self.context

    def set_model(self, perspective_model):
        """
        Sets the model for the perspective
        """
        self.model = perspective_model

    def get_model(self):
        """
        Returns the model for the perspective
        """
        self.model