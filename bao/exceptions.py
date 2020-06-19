# coding: utf8
"""Bao exceptions"""


class BaoError(Exception):
    pass


class PackageError(BaoError):
    pass


class RepositoryError(BaoError):
    pass


class ConfigError(BaoError):
    pass
