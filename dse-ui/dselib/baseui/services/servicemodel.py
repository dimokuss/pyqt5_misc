class ServiceDefinition(object):
    """
    Represents the meta-data definition for a service.
    """
    def __init__(self, service_id, global_flag, module, service, configurator=None):
        """
        Initializes the ServiceDefinition instance.
        service_id -- A string identifying the service.
        global_flag -- A boolean indicating whether or not the service is a global service or not.
        module -- The module that holds the service.
        service -- The name of the class to instantiate.
        configurator -- The configurator class to instantiate.
        """
        self.service_id = service_id
        self.global_flag = global_flag
        self.module = module
        self.service = service
        self.configurator = configurator

    def get_id(self):
        """
        Retrieves the id of the service.
        """
        return self.service_id

    def is_global(self):
        """
        Retrieves whether or not the service is a global service.
        """
        return self.global_flag

    def get_module(self):
        """
        Retrieves the module the service is defined in.
        """
        return self.module

    def get_service(self):
        """
        Retrieves the class name of the service to instantiate.
        """
        return self.service

    def get_configurator(self):
        """
        Retrieves the class name of the configurator to instantiate.
        """
        return self.configurator
