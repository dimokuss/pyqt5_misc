class PerspectiveDefinition(object):
    """
    Represents a perspective definition loaded from content from a definition file.
    :param name -- The name of the perspective.
    :param module -- The python module that defines the perspective class.
    :param controller -- The class name of the controller that will be instantiated when the perspective is loaded.
    """
    def __init__(self, name, module, controller):
        self.name = name
        self.module = module
        self.controller = controller
        self.commands = []

    def get_name(self):
        """
        :returns -- the name of the perspective.
        """
        return self.name

    def get_module(self):
        """
        :returns -- the python module the perspective controller resides.
        """
        return self.module

    def get_controller(self):
        """
        :returns -- the name of the class containing the perspective logic.
        """
        return self.controller
