# -*- coding: utf-8 -*-
"""Scans your environment for all needed licenses"""

from importlib.metadata import version

__author__ = """Tom Nijhof-Verhees"""
__version__ = version("license_scanner")

# Add here import to all the functions you need

from .get_all_licenses import get_all_licenses
