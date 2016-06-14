from PyQt5.QtCore import *


class AcesTypes(object):
    """
    Defines available built-in ACES types.
    """
    ItemRevision = QVariant.UserType + 1,
    Folder = QVariant.UserType + 2,
    Workset = QVariant.UserType + 3

class ItemRevisionMimeData(QMimeData):
    """
    Represents a specific subclass of QMimeData for item revisions.
    """
    def __init__(self):
        """
        Initializes the ItemRevisionMimeData instance.
        """
        QMimeData.__init__(self)

    def formats(self):
        """
        Retrieves the formats supported by the mime data.
        returns -- A list of strings defining the supported formats.
        """
        return ["application/x-aces-itemrevision"]
    
class FolderMimeData(QMimeData):
    """
    Represents a specific subclass of QMimeData for folders.
    """
    def __init__(self):
        """
        Initializes the FolderMimeData instance.
        """
        QMimeData.__init__(self)
        
    def formats(self):
        """
        Retrieves the formats supported by the mime data.
        returns -- A list of strings defining the supported formats.
        """
        return ["application/x-aces-folder"]
    
class WorksetMimeData(QMimeData):
    """
    Represents a specific subclass of QMimeData for worksets.
    """
    def __init__(self):
        """
        Initializes the WorksetMimeData instance.
        """
        QMimeData.__init__(self)
        
    def formats(self):
        """
        Retrieves the formats supported by the mime data.
        returns -- A list of strings defining the supported formats.
        """
        return ["application/x-aces-workset"]
