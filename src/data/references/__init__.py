"""
CP2B Maps - Academic References Package
Professional citation management and reference database
"""

from .reference_database import ReferenceDatabase, Reference, ReferenceCategory, get_reference_database

__all__ = [
    'ReferenceDatabase',
    'Reference',
    'ReferenceCategory',
    'get_reference_database'
]