"""
ICU — International Components for Unicode

Functions which provide information from the Python ICU library <url>:icu:https://pypi.org/project/pyicu/</url> library.

Examples:

  Load in Mathics3 Module:
  >> LoadModule["pymathics.icu"]
    = pymathics.icu

  Show the language in effect:
  >> $Language
   = English

  Get the alphabet for that language:
  >> Alphabet[]
   = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z}

  Get the alphabet for that locale "es" (Spanish):
  >> Alphabet["es"]
   = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, á, é, í, ñ, ó, ú, ü}

  You can also specify an alphabet using a name:
  >> Alphabet["Ukrainian"]
   = {ʼ, а, б, в, г, д, е, ж, з, и, й, к, л, м, н, о, п, р, с, т, у, ф, х, ц, ч, ш, щ, ь, ю, я, є, і, ї, ґ}
"""

from pymathics.icu.__main__ import Alphabet, AlphabeticOrder, Language
from pymathics.icu.version import __version__

pymathics_version_data = {
    "author": "The Mathics3 Team",
    "version": __version__,
    "name": "icu",
    "requires": ["PyICU"],
}

__all__ = ["Alphabet", "AlphabeticOrder", "Language", "pymathics_version_data", "__version__"]
