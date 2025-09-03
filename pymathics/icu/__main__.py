# -*- coding: utf-8 -*-

"""
Languages - Human-Language Alphabets and Locales via PyICU.
"""

from typing import List, Optional

from icu import Collator, Locale, LocaleData
from mathics.core.atoms import Integer, String
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation

available_locales = Locale.getAvailableLocales()
language2locale = {
    availableLocale.getDisplayLanguage(): locale_name
    for locale_name, availableLocale in available_locales.items()
}

# The current value of $Language
LANGUAGE = "English"


def eval_alphabet(language_name: String) -> Optional[List[String]]:

    py_language_name = language_name.value
    locale = language2locale.get(py_language_name, py_language_name)
    if locale not in available_locales:
        return
    alphabet_set = LocaleData(locale).getExemplarSet(0, 0)
    return to_mathics_list(*alphabet_set, elements_conversion_fn=String)


def eval_alphabetic_order(string1: str, string2: str, language_name=LANGUAGE) -> int:
    """
    Compare two strings using locale-sensitive alphabetic order.

    Returns:
        1 if string1 appears before string2 in alphabetic order,
        -1 if string1 appears after string2,
        0 if they are identical.
    """
    locale_str = language_to_locale(language_name)
    collator = Collator.createInstance(Locale(locale_str))
    comparison = collator.compare(string1, string2)
    if comparison < 0:
        return 1
    elif comparison > 0:
        return -1
    else:
        return 0


def language_to_locale(language_name: str, fallback="en_US") -> str:
    """
    Convert a language name (e.g., "English") to an ICU locale string (e.g., "en_US").
    Returns the first matching locale string or a fallback if not found.

    Args:
        language_name (str): Language name in English (e.g., "English", "French").
        fallback (str): Locale string to return if not found.

    Returns:
        str: Locale string (e.g., "en_US", "fr_FR").
    """
    # Normalize input
    language_name = language_name.strip().lower()

    for loc_str in available_locales:
        loc = Locale(loc_str)
        # Get display language in English.
        # FIXME? Generalize or do better later?
        disp_lang = loc.getDisplayLanguage(Locale("en")).lower()
        if disp_lang == language_name:
            return loc_str

    # Could not find exact match, return fallback
    return fallback


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
     = {ʼ, а, б, в, г, д, е, ж, з, и, й, к, л, м, н, о, п, р, с, т, у, ф, х, ц, ч, ш, щ, ь, ю, я, є, і, ї, ґ}

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


class AlphabeticOrder(Builtin):
    """
     <url>:WMA:https://reference.wolfram.com/language/ref/AlphabeticOrder.html</url>
     <dl>
      <dt>'AlphabetOrder'[$string_1$, $string_2$]
      <dd>gives 1 if $string_1$ appears before $string_2$ in alphabetical order, -1 if it is after, and 0 if it is identical.
    </dl>

     >> AlphabeticOrder["apple", "banana"]
      = 1

     >> AlphabeticOrder["parrot", "parrot"]
      = 0

     When words are the same but only differ in case, usually lowercase letters come first:
     >> AlphabeticOrder["A", "a"]
      = -1

     Longer words follow their prefixes:
     >> AlphabeticOrder["Papagayo", "Papa", "Spanish"]
      = -1

     But accented letters usually appear at the end of the alphabet:
     >> AlphabeticOrder["Papá", "Papa", "Spanish"]
      = -1

     >> AlphabeticOrder["Papá", "Papagayo", "Spanish"]
      = 1
    """

    summary_text = "compare strings according to an alphabet"

    def eval(self, string1: String, string2: String, evaluation: Evaluation):
        """AlphabeticOrder[string1_String, string2_String]"""
        return Integer(eval_alphabetic_order(string1.value, string2.value))

    def eval_with_lang(self, string1: String, string2: String, lang: String, evaluation: Evaluation):
        """AlphabeticOrder[string1_String, string2_String, lang_String]"""
        return Integer(eval_alphabetic_order(string1.value, string2.value, lang.value, ))


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

    By setting its value, The letters of 'Alphabet[]' are changed:

    >> $Language = "German"; Alphabet[]
     = ...

    #> $Language = "English"
     = English

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
