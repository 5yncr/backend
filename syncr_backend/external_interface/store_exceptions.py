"""Exceptions for key store and drop peer store."""


class MissingConfigError(Exception):
    """Handle issue of missing config file."""

    pass


class IncompleteConfigError(Exception):
    """Handle issue of incomplete config file."""

    pass


class UnsupportedOptionError(Exception):
    """Handle issue of unsupported store options."""

    pass
