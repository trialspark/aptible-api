class Error(Exception):
    """Base class for other exceptions"""


class UnknownResourceInflation(Error):
    """Raised when there is an unknown Task state"""


class UnknownEmbeddedResourceType(Error):
    """Raised when the input value is too small"""
