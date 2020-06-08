# coding: utf8
"""Picaro exceptions"""


class PicaroError(Exception):
    pass


class PackageError(PicaroError):
    pass


class RepositoryError(PicaroError):
    pass


class ConfigError(PicaroError):
    pass
