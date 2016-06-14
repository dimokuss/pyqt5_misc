__author__ = 'Eric L. Frederich'

from aceslib.baseui.services.acesservice import AcesService


class SearchService(AcesService):
    """
    Defines a service that can be used for searching.
    """
    def __init__(self, context, service_id):
        """
        Initializes the SearchService instance.
        context -- The context into which the service will be loaded.
        service_id -- A string identifying the service.
        """
        super(SearchService, self).__init__(context, service_id)

    def register_service(self):
        """
        Invoked when the service is first loaded by the ACES system, allowing the service to perform initialization actions.
        """
        super(SearchService, self).register_service()

    def initialize_service(self):
        """
        Initializes the service.  This takes place after all services have been registered and all configuration items have been loaded.
        """
        super(SearchService, self).initialize_service()
        self.lws_manager = self.context.get_service('Framework').lws_manager

    def unregister_service(self):
        """
        Invoked when the service is unloaded by the ACES system, allowing the service to perform clean-up actions.
        """
        super(SearchService, self).unregister_service()

    def do_search(self, s, include_cpd=False):
        """
        Executes a search on the specified string.
        s -- The string to search for.
        include_cpd -- A flag indicating whether or not to include the CPD system data in the search or not.
        """
        return self.lws_manager.search(s, include_cpd)
   
    def do_expression_search(self, expression):
        """
        Executes an expression search on the specified string.
        expression -- The expression instance defining what to search for.
        """
        return self.lws_manager.expression_search(expression)
