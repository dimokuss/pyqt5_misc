import importlib
import json
import os.path
import fnmatch
import dselib
from dselib.baseui.services.dseservice import (DseService, DseServiceConfigurator)
from dselib.baseui.services.servicemodel import ServiceDefinition

class AppContext(object):
    """
    Represents the context for the ACES application instance.
    Each ACES process is composed of multiple top-level windows, all of which share the same context.
    """

    def __init__(self):
        """
        Initializes the AppContext instance.
        """
        self.argv = []
        self.services = {}
        self.configurators = {}
        self.service_definitions = []
        self.main_window = None

    def initialize(self, argv):
        """
        Initializes the context by loading built-in services, config, etc.
        """
        self.argv = argv
        root_dir = os.path.dirname(dselib.__file__)
        config_path = os.path.join(root_dir, 'config')

        aces_config_file = os.path.join(config_path, 'dseconfig.json')
        local_dev = os.environ.get('LOCAL_DEV')
        if local_dev is not None and os.path.isfile(os.path.join(local_dev, 'dseconfig.json')):
            aces_config_file = os.path.join(local_dev, 'dseconfig.json')
            print('USING ACESCONFIG FILE: ', aces_config_file)

        # first we parse the root dseconfig.json file
        with open(aces_config_file) as config_file:
            data = json.load(config_file)

            # gather the list of services, they will read the rest of the configuration file
            for key in data:
                if key == "serviceDefinition":
                    self._load_service_definition(data[key])
            # we've instantiated the built-in services, now read the rest of the config file using the configurators
            for configurator_id in self.configurators:
                self.configurators[configurator_id].load_config(data)

        # at this point, we've loaded the built-in configuration, everything else must be
        # extensions to the base DSE system - we go through each file and determine if there
        # are additional services with configurators first, then back through each allowing all configurators to load        
        for name in os.listdir(config_path):
            if not fnmatch.fnmatch(name, "*.json"):
                continue
            if name != "dseconfig.json":
                print("Process file:" + str(name))
                with open(os.path.join(config_path, name)) as config_file:
                    data = json.load(config_file)
                    for key in data:
                        if key == "serviceDefinition":
                            self._load_service_definition(data[key])
        for name in os.listdir(config_path):
            if not fnmatch.fnmatch(name, "*.json"):
                continue
            if name != "dseconfig.json":
                with open(os.path.join(config_path, name)) as config_file:
                    data = json.load(config_file)

                    for configurator_id in self.configurators:
                        self.configurators[configurator_id].load_config(data)

        # service initialization is a two-phase workflow where first all services are registered (where they can perform initialization
        # pertaining only to them) followed by initialized (where they can perform initialization that may need other services)
        # we complete the workflow here by initializing the services
        for _service_id, service in list(self.services.items()):
            service.initialize_service()

    def set_window(self, window):
        """
        sets the main window to context
        :param window:
        :return:
        """
        self.main_window = window

    def close(self):
        """
        Terminates the services within the context.
        """
        for _serviceId, service in list(self.services.items()):
            service.unregister_service()

    def _load_service_definition(self, service_definition_entry):
        """
        Loads a service definition configuration entry from the given file and instantiates the services and configurators.
        service_definition_entry -- The service definition entry to load from the configuration file.
        """
        if "services" not in service_definition_entry:
            raise ValueError("Ill-formed service definition - must contain at least one service entry!")

        if not isinstance(service_definition_entry["services"], list):
            raise ValueError("Ill-formed service definition - services entry must be a valid list!")

        for service_entry in service_definition_entry["services"]:
            if "id" not in service_entry:
                raise ValueError("Ill-formed service definition - service entry must have an id!")

            if "global" not in service_entry:
                raise ValueError("Ill-formed service definition - service entry must define whether or not it is a global service!")

            is_global = service_entry["global"]
            if not isinstance(is_global, bool):
                raise ValueError("Ill-formed service definition - service entry's global flag must be a boolean")

            if "module" not in service_entry:
                raise ValueError("Ill-formed service definition - service entry must specify a module!")

            if "service" not in service_entry:
                raise ValueError("Ill-formed service definition - service entry must specify a service class!")

            service_definition = None
            if "configurator" in service_entry:
                service_definition = ServiceDefinition(service_entry["id"], is_global, service_entry["module"], service_entry["service"],
                                                       service_entry["configurator"])
            else:
                service_definition = ServiceDefinition(service_entry["id"], is_global, service_entry["module"], service_entry["service"])

            # read in the service entry, add it to the list
            # and instantiate the service / configurator
            self.service_definitions.append(service_definition)

            # load the module, the configurator, and the service if it exists in a global context
            print(service_definition.get_module()+"\n")
            module = importlib.import_module(service_definition.get_module())
            if service_definition.get_configurator() is not None:
                configurator_class = getattr(module, service_definition.get_configurator())
                configurator = configurator_class(self, service_definition.get_id())
                if not isinstance(configurator, DseServiceConfigurator):
                    raise ValueError(
                        "Configurator with the name \"" + service_definition.get_configurator() + "\" is not a valid DseServiceConfigurator instance!")

                if service_definition.get_id() in self.configurators:
                    raise ValueError("Error, duplicate configurator id detected: " + service_definition.get_id())
                else:
                    self.configurators[service_definition.get_id()] = configurator

            service_class = getattr(module, service_definition.get_service())
            if service_definition.is_global():
                service = service_class(self, service_definition.get_id())
                if not isinstance(service, DseService):
                    raise ValueError("Service with the name \"" + service_definition.get_service() + "\" is not a valid DseService instance!")

                # register the service
                service.register_service()
                if service_definition.get_id() in self.services:
                    raise ValueError("Error, duplicate service id detected: " + service_definition.get_id())
                else:
                    self.services[service_definition.get_id()] = service


    def get_service(self, service_id):
        """
        Retrieves the a service from the context by id.
        service_id -- The id of the service to retrieve.
        """
        if service_id not in self.services:
            raise ValueError("Service: \"" + service_id + "\" does not exist in the context!")

        return self.services[service_id]

    def get_configurator(self, service_id):
        """
        Retrieves a configurator from the context by id.
        service_id -- The id of the service to retrieve the configurator for.
        """
        if service_id not in self.configurators:
            raise ValueError("Configurator: \"" + service_id + "\" does not exist in the context!")

        return self.configurators[service_id]

    def get_command_line_args(self):
        """
        Retrieves the command line arguments ACES was launched with.
        """
        return self.argv

    def get_class_path(self):
        """
        Retrieves the path to the type class definitions.
        """
        # TODO: Hate environment variables defining paths, this should be done through a configuration file!
        return os.path.join(os.environ['ACES_GLOBAL_DIR'], 'classes')
