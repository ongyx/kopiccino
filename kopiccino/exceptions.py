# coding: utf8
"""Kopiccino exceptions."""


class KopiError(Exception):
    pass


class PackageError(KopiError):
    pass


class RepositoryError(KopiError):
    pass


class ConfigError(KopiError):
    pass
