import os

from PyQt5.QtWidgets import QDialog

import dselib
from dselib.baseui.services.dseservice import DseService
import logging

class CpdServerInfo(object):
    """
    Represents information about a particular CPD server.
    """
    def __init__(self, server_id, server_url):
        """
        Initializes the CpdServerInfo instance.
        server_id -- A string identifying the server.
        server_url -- A string defining the URL of the server.
        """
        self.server_id = server_id
        self.server_url = server_url
        self.pki_app_id = None
        self.pki_url = None

    def get_server_id(self):
        """
        Retrieves the id of the server.
        """
        return self.server_id

    def get_server_url(self):
        """
        Retrieves the URL of the server.
        """
        return self.server_url

    def get_pki_app_id(self):
        """
        Retrieves the PKI app id.
        """
        return self.pki_app_id

    def get_pki_url(self):
        """
        Retrieves the PKI url.
        """
        return self.pki_url

    def set_pki_app_id(self, pki_app_id):
        """
        Sets the PKI app id.
        pki_app_id -- The PKI app id to set.
        """
        self.pki_app_id = pki_app_id

    def setPkiUrl(self, pki_url):
        """
        Sets the PKI url.
        pki_url -- The PKI URL to set.
        """
        self.pki_url = pki_url

class FrameworkService(DseService):
    """
    Represents the service encapsulating all framework functionality.
    """
    def __init__(self, context, service_id):
        """
        Initializes the FrameworkService instance.
        context -- The context in which the service is loaded.
        service_id -- A string identifying the service.
        """
        DseService.__init__(self, context, service_id)
        self.framework = None
        self.lws_manager = None
        self.cpd_manager = None
        self.definition_service = None
        self.aces_session = None
        self.bom_manager = None
        self.cpd_servers = []
        self.aces_factory = None

    def register_service(self):
        """
        Invoked when the service is first loaded by the ACES system, allowing the service to perform initialization actions.
        """

        # initialize the framework
        lws_path = ''
        command_line_args = self.context.get_command_line_args()
        if len(command_line_args) > 2:
            # TODO: should switch the args over to options so we don't have to assume fixed placement for things
            # arg[0] is launch script
            # arg[1] is default perspective
            # arg[2] is local workspace path
            lws_path = os.path.expanduser(command_line_args[2])
        else:
            lws_path = os.path.join(os.path.expanduser('~'), '.aces_local_workspace')

        # DOK:  self.framework = Framework.Instance()
        #self.framework.lws_path = lws_path
        #self.framework.definition_path = self.context.get_class_path()
        #self.framework.login_callback = self._on_login
        #self.framework.initialize()
        #self.lws_manager = self.framework.lws_manager
        #self.cpd_manager = self.framework.cpd_manager
        #self.definition_service = self.framework.definition_service
        #self.aces_session = self.framework.session
        #self.aces_factory = self.framework.aces_factory

        # parse the list of TC servers
        # TODO: should really make this fully generic by adding a configurator to the framework service to specify the provider is TC, but for now we just assume TC
        root_dir = os.path.dirname(dselib.__file__)
        config_path = os.path.join(root_dir, 'config')

    def initialize_service(self):
        """
        Initializes the service.  This takes place after all services have been registered and all configuration items have been loaded.
        """
        pass

    def unregister_service(self):
        """
        Unregisters the service from the ACES application.
        """
        # close the framework
        #self.framework.destroy()

    def to_easy(self, data_item_revision):
        """
        Converts the given raw data item revision into an easy object.
        data_item_revision -- The raw data item revision to convert into an easy object.
        """
        if isinstance(data_item_revision, AcesItemRevision):
            return data_item_revision
        return self.aces_factory.createFacade(data_item_revision)
