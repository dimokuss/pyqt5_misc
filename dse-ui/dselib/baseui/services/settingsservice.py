import os

from enum import Enum
from PyQt5.Qt import QSettings

from dselib.baseui.services.dseservice import DseService


class MainWindowSettings(Enum):
    """
    Defines the different classes of references associated with tool inputs / outputs.
    """
    MainWindowSize                          = 1,               
    MainWindowPosition                      = 2,
    MainWindowVerticalSplitterState         = 3,
    MainWindowHorizontalSplitterState       = 4


class SettingsService(DseService):
    """
    Represents the service responsible for saving user and application settings
    """   
    def __init__(self, context, service_id):
        """
        Initializes the SettingsService instance.
        context -- The context in which the service is loaded into.
        service_id -- A string identifying the service.
        """
        DseService.__init__(self, context, service_id)
        self.user_settings_file = os.path.join(os.path.expanduser('~'), '.dse/dse_settings.ini')
    
    def set_user_settings(self, group_name, category, value):
        """
        Saves user settings for a given group and category.
        group_name -- The group in which to save the settings value.
        category -- The category in which to save the settings value.
        value -- The value to save.
        """
        settings = QSettings(self.user_settings_file, QSettings.IniFormat)
        settings.beginGroup(group_name)
        settings.setValue(str(category), value)
        settings.endGroup()

    def get_user_settings(self, group_name, category):  
        """
        Retrieves user settings for the given group and category.
        group_name -- The group for which to retrieve settings values.
        category -- The category for which to retrieve settings values.
        """
        settings = QSettings(self.user_settings_file, QSettings.IniFormat)
        settings.beginGroup(group_name)        
        savedValue = settings.value(str(category))
        settings.endGroup()
        
        return savedValue

    def remove_group(self, group_name):
        """
        This is a prevent loading old/deleted groups
        :param group_name: the group name to be removed
        :return:
        """
        settings = QSettings(self.user_settings_file, QSettings.IniFormat)
        settings.remove(group_name)
