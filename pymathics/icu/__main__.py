# -*- coding: utf-8 -*-

"""
Languages - Human-Language Alphabets and Locales via PyICU.
"""

# PYTHON MODULES USED IN HERE

# PyICU: human-language alphabets and locales


from typing import List, Optional

from icu import Locale, LocaleData
from mathics.core.atoms import String
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation

availableLocales = Locale.getAvailableLocales()
language2locale = {
    availableLocale.getDisplayLanguage(): locale_name
    for locale_name, availableLocale in availableLocales.items()
}

# The current value of $Language
LANGUAGE = "English"

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
      <dd>gives the list of lowercase letters a-z in the English alphabet.

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
        "Alphabet[]": """Alphabet[Pymathics`$Language]""",
    }

    summary_text = "lowercase letters in an alphabet"

    def eval(self, alpha: String, evaluation):
        """Alphabet[alpha_String]"""
        alphabet_list = eval_alphabet(alpha)
        if alphabet_list is None:
            evaluation.message("Alphabet", "nalph", alpha)
            return
        return alphabet_list

## FIXME: move to mathics-core. Will have to change references to Pymathics`$Language to $Language
class Language(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/\\$Language.html</url>

    <dl>
      <dt>'\\$Language'
      <dd>is a settable global variable for the default language used in Mathics3.
    </dl>

    See the language in effect used for functions like 'Alphabet[]':

    >> old_language = $Language
     = ...

    By setting its value, The letters of 'Alphabet[]' are changed:

    >> $Language = "German"; Alphabet[]
     = ...

    #> $Language = old_language;

    See also <url>
    :Alphabet:
     /doc/mathics3-modules/icu-international-components-for-unicode/languages-human-language-alphabets-and-locales-via-pyicu/alphabet/</url>.
    """

    name = "$Language"
    messages = {
        "notstr": "`1` is not a string. Only strings can be set as the value of $Language.",
    }

    summary_text = "settable global variable giving the default language"
    value = f'"{LANGUAGE}"'
    # Rules has to come after "value"
    rules = {
        "Pymathics`$Language": value,
    }

    def eval_set(self, value, evaluation: Evaluation):
        """Set[Pymathics`$Language, value_]"""
        if isinstance(value, String):
            evaluation.definitions.set_ownvalue("$Language", value)
        else:
            evaluation.message("Pymathics`$Language", "notstr", value)
        return value
