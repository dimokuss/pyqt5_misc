from PyQt5.QtCore import *


class DseServiceConfigurator(QObject):
    """
    Represents a configurator capable of loading configuration for a service from a file.
    """
    def __init__(self, app_context, service_id):
        """
        Initializes the AcesServiceConfigurator instance.
        app_context -- The application context hosting the configurator.
        servier_id -- A string defining the id of the service the configurator reads information for.
        """
        QObject.__init__(self)
        self.app_context = app_context
        self.service_id = service_id
        
    def get_id(self):
        """
        Retrieves the id of the service the configurator reads information for.
        """
        return self.service_id
    
    def load_config(self, config_file):
        """
        Loads the service's configuration from the given configuration file.
        Inheritors must override this method to read the information they are interested in from the configuration file.
        config_file -- The configuration file information read as a json dictionary.
        """
        raise NotImplementedError

class DseService(QObject):
    """
    Represents a base service object for DSE.  A service is an object that provides "services"
    for all entities inside of the DSE system.  This includes things like menus, clipboard, etc.
    These services encapsulate the non-UI logic required by the UI.
    Services can be "general" or "view" services.  
    General services guarantee to use no UI and can be loaded into a batch context, these services are configured with "global": true in the configuration file
    and are loaded into the root application context.
    View services may use UI methods and cannot be loaded into a batch context.  These services are configured with "global": false in the configuration file
    and are loaded into each perspective context that is created by the DSE UI.
    """
    def __init__(self, context, service_id):
        """
        Initializes the AcesService instance.
        context -- The context in which the service is hosted.  General services are hosted in an application context, view services in a perspective context.
        service_id -- A string uniquely identifying the service and by which the service can be queried from the context.
        """
        QObject.__init__(self)
        self.context = context
        self.service_id = service_id
        
    def register_service(self):
        """
        Invoked when the service is first loaded by the ACES system, allowing the service to perform initialization actions.
        """
        pass
    
    def initialize_service(self):
        """
        Initializes the service.  This takes place after all services have been registered and all configuration items have been loaded.
        """
        pass
    
    def unregister_service(self):
        """
        Invoked when the service is unloaded by the ACES system, allowing the service to perform clean-up actions.
        """
        pass

    def get_id(self):
        """
        Retrieves the id of the service that will be used for querying the service by entities in the ACES system.
        """
        return self.service_id
