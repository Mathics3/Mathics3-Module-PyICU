"""Mathics3 Module PyICU

This module provides Mathics functions and varialbles to work with
Languages and Translations.
"""

from pymathics.language.__main__ import Alphabet
from pymathics.language.version import __version__

pymathics_version_data = {
    "author": "The Mathics Team",
    "version": __version__,
    "name": "Language",
    "requires": ["PyICU"],
}

__all__ = ["Alphabet", "pymathics_version_data", "__version__"]
