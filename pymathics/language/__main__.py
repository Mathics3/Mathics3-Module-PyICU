# -*- coding: utf-8 -*-

"""
Languages & Translations
"""

# PYTHON MODULES USED IN HERE

# PyICU: human-language alphabets and locales


from typing import List, Optional

from icu import Locale, LocaleData
from mathics.core.atoms import String
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list

availableLocales = Locale.getAvailableLocales()
language2locale = {
    availableLocale.getDisplayLanguage(): locale_name
    for locale_name, availableLocale in availableLocales.items()
}


def eval_alphabet(language_name: String) -> Optional[List[String]]:

    py_language_name = language_name.value
    locale = language2locale.get(py_language_name, py_language_name)
    if locale not in availableLocales:
        return
    alphabet_set = LocaleData(locale).getExemplarSet(0, 0)
    return to_mathics_list(*alphabet_set, elements_conversion_fn=String)


class Alphabet(Builtin):
    """
     Basic lowercase alphabet via <url>:Unicode: https://home.unicode.org/</url> and <url>:PyICU: https://pypi.org/project/PyICU/</url>
     <dl>
      <dt>'Alphabet'[]
      <dd>gives the list of lowercase letters a-z in the English alphabet .

      <dt>'Alphabet[$type$]'
      <dd> gives the alphabet for the language or class $type$.
    </dl>

    >> Alphabet["Ukrainian"]
     = {a, ä, b, c, d, e, f, g, h, i, j, k, l, m, n, o, ö, p, q, r, s, ß, t, u, ü, v, w, x, y, z}

    The alphabet when nothing is specified, "English" is used:
    >> Alphabet[]
     = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z}

    Instead of a language name, you can give a local value:
    >> Alphabet["es"]
     = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, á, é, í, ñ, ó, ú, ü}

    Many locales are the same basic set of letters.
    >> Alphabet["en_NZ"] == Alphabet["en"]
     = True
    """

    messages = {
        "nalph": "The alphabet `` is not known or not available.",
    }

    rules = {
        "Alphabet[]": """Alphabet["English"]""",
    }

    summary_text = "lowercase letters in an alphabet"

    def eval(self, alpha: String, evaluation):
        """Alphabet[alpha_String]"""
        alphabet_list = eval_alphabet(alpha)
        if alphabet_list is None:
            evaluation.message("Alphabet", "nalph", alpha)
            return
        return alphabet_list
