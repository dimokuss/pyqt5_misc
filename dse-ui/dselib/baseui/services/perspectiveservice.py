import importlib

from dselib.baseui.perspectivebase.perspective import Perspective
from dselib.baseui.perspectivebase.perspectivemodel import PerspectiveDefinition
from dselib.baseui.services.dseservice import (DseService,
                                               DseServiceConfigurator)


class PerspectiveConfigurator(DseServiceConfigurator):
    """
    Represents the configurator for perspective definitions.
    """
    def __init__(self, app_context, service_id):
        """
        Initializes the PerspectiveConfigurator instance.
        app_context -- The context in which the configurator is instantiated.
        service_id -- The id of the service the configurator belongs to.
        """
        DseServiceConfigurator.__init__(self, app_context, service_id)
        self.perspective_definitions = []
        self.perspective_extension_definitions = []
        
    def get_perspective_definitions(self):
        """
        Retrieves the loaded perspective definitions.
        """
        return self.perspective_definitions
    
    def get_perspective_extension_definitions(self):
        """
        Retrieves the loaded perspective extension definitions.
        """
        return self.perspective_extension_definitions
        
    def load_config(self, config_file):
        """
        Loads the set of perspective definitions that define the perspectives.
        config_file: A loaded json configuration files defining the perspectives
        (and other non-interesting information).
        """
        if config_file is None:
            return
        
        for key in config_file:
            if key == "perspectiveDefinition":
                self.load_perspective_definition(config_file[key])

    def load_perspective_definition(self, perspective_definition_entry):
        """
        Loads the perspective definitions from the given loaded configuration file.
        perspective_definition_entry -- The perspective definition to load from the configuration file.
        """
        # TODO: convert this method from raising ValueErrors to logging an error notification
        # and continuing on - we don't want to stop the processing of all other perspective definitions 
        # for one bad one
        if "perspectives" not in perspective_definition_entry:
            raise ValueError("Ill-formed perspective definition - "
                             "perspective definition must have at least one perspective!")
        
        if not isinstance(perspective_definition_entry["perspectives"], list):
            raise ValueError("Ill-formed perspective definition - perspectives must be a valid list!")
        
        perspectives = perspective_definition_entry["perspectives"]
        
        for perspective_tag in perspectives:
            # ensure it has a name
            if 'name' not in perspective_tag:
                raise ValueError("Ill-formed perspective definition - no name is given!")

            if 'module' not in perspective_tag:
                raise ValueError("Ill-formed perspective definition - no module is given!")

            if 'controller' not in perspective_tag:
                raise ValueError("Ill-formed perspective definition - no controller is given!")

            loaded_perspective_definition = PerspectiveDefinition(perspective_tag['name'], perspective_tag['module'],
                                                                  perspective_tag['controller'])
            self.perspective_definitions.append(loaded_perspective_definition)
        
class PerspectiveService(DseService):
    """
    Represents the service that creates perspective contexts and loads perspectives.
    """
    def __init__(self, context, service_id):
        """
        Initializes the PerspectiveService instance.
        context -- The context in which the service is instantiated.
        service_id -- A string defining the id of the service.
        """
        DseService.__init__(self, context, service_id)
        
    def load_perspective(self, perspective_name):
        """
        Loads the perspective with the given name from the information in the definition file.
        perspective_name -- The name of the perspective to load.
        perspective_context -- The context in which to load the perspective.
        """
        perspective_definition = None
        for loaded_perspective_definition in \
                self.context.get_configurator("Perspective").get_perspective_definitions():
            if loaded_perspective_definition.get_name() == perspective_name:
                perspective_definition = loaded_perspective_definition
                break
            
        if perspective_definition is None:
            raise ValueError("No perspective with the name \"" + perspective_name + "\" was defined!")
        
        # the perspective definition indicates the controller we need to load from what module
        module = importlib.import_module(perspective_definition.get_module())
        perspective_controller = getattr(module, perspective_definition.get_controller())
        perspective = perspective_controller(perspective_name, self.context)
        if not isinstance(perspective, Perspective):
            raise ValueError("Perspective controller with the name \"" +
                             perspective_definition.get_controller() + "\" is not a valid Perspective instance!")
    
        perspective.set_definition(perspective_definition)
        perspective.initialize_perspective()

        return perspective
