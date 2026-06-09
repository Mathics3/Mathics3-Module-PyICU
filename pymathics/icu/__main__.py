# -*- coding: utf-8 -*-

"""
Languages - Human-Language Alphabets and Locales via PyICU.
"""

from dataclasses import dataclass
from typing import Any, Final, Optional

from icu import Collator, Locale, LocaleData, UCollAttribute, UCollAttributeValue
from mathics.builtin.system import LANGUAGE
from mathics.core.atoms import Integer, String
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic

available_locales = Locale.getAvailableLocales()
language2locale = {
    availableLocale.getDisplayLanguage(): locale_name
    for locale_name, availableLocale in available_locales.items()
}

StringAutomatic: Final[String] = String("System`Automatic")
LowerFirst: Final[set[String]] = {String("System`LowerFirst"), String("LowerFirst")}
StringUpperFirst: Final[String] = String("UpperFirst")
SymbolLanguage: Final[String] = Symbol("System`$Language")


@dataclass(frozen=True)
class AlphabeticOrderOptions:
    """
    Stores options associated with AlphbeticOrder[] builtin.

    One initialized, this structure is immutable or frozen.
    """

    lowercase_ordering: Optional[bool] = None
    """'True" if ordering should be lowercase first, 'False" if should uppercase first,
      and 'None' if we should use the natural alphabet ordering case."""

    ignore_case: bool = False
    """whether to ignore upper versus lower case"""

    ignore_diacritics: bool = False
    """whether to ignore diacritics for ordering"""

    ignore_punctuation: bool = False
    """whether to ignore punctuation for ordering"""

    language: str = LANGUAGE
    """what language or alphabet to assume"""

    @classmethod
    def from_dict(
        cls, options: dict[str, Any], evaluation: Evaluation
    ) -> Optional["AlphabeticOrderOptions"]:
        """Factory method that normalizes, type-checks, and builds the frozen structure
        from a raw dict[str, str].
        """
        key_mapping = {
            "System`CaseOrdering": "lowercase_ordering",
            "System`IgnoreCase": "ignore_case",
            "System`IgnoreDiacritics": "ignore_diacritics",
            "System`IgnorePunctuation": "ignore_punctuation",
            "System`Language": "language",
        }

        # This will hold our cleaned, type-converted parameters
        processed_args: dict[str, Any] = {
            "lowercase_ordering": None,
            "ignore_case": False,
            "ignore_diacritics": False,
            "ignore_punctuation": False,
            "language": LANGUAGE,
        }

        # Iterate through the user-provided options dictionary
        for raw_key, option_value in options.items():
            normalized_key = key_mapping.get(raw_key)

            if not normalized_key:
                evaluation.message("AlphabeticOrder", "nodef", Symbol(raw_key), String("AlphabeticOrder"))
                return

            # Type parsing and validation based on the target field name
            if normalized_key in (
                "ignore_case",
                "ignore_diacritics",
                "ignore_punctuation",
            ):
                if option_value not in (SymbolTrue, SymbolFalse):
                    evaluation.message("AlphabeticOrder", "nodef", Symbol(raw_key), String("AlphabeticOrder"))
                    return
                processed_args[normalized_key] = option_value.value

            elif normalized_key == "language":
                if option_value is SymbolLanguage:
                    option_value = String(LANGUAGE)

                if not isinstance(option_value, String):
                    evaluation.message("AlphabeticOrder", "nodef", Symbol(raw_key), String("AlphabeticOrder"))
                    return
                processed_args[normalized_key] = option_value

            elif normalized_key == "lowercase_ordering":
                if (option_value is SymbolAutomatic) or option_value == "Automatic":
                    processed_args[normalized_key] = None
                elif option_value in LowerFirst:
                    processed_args[normalized_key] = True
                elif option_value == StringUpperFirst:
                    processed_args[normalized_key] = False
                else:
                    evaluation.message("AlphabeticOrder", "nodef", Symbol(raw_key), String("AlphabeticOrder"))
                    return

        # Initialize and return the frozen dataclass using our verified arguments
        return cls(**processed_args)


def eval_alphabet(language_name: String) -> Optional[list[String]]:

    py_language_name = language_name.value
    locale = language2locale.get(py_language_name, py_language_name)
    if locale not in available_locales:
        return
    alphabet_set = LocaleData(locale).getExemplarSet(0, 0)
    return to_mathics_list(*alphabet_set, elements_conversion_fn=String)


def eval_alphabetic_order(
    string1: str, string2: str, language_name, options: AlphabeticOrderOptions
) -> int:
    """
    Compare two strings using locale-sensitive alphabetic order.

    Returns:
        1 if string1 appears before string2 in alphabetic order,
        -1 if string1 appears after string2,
        0 if they are identical.
    """
    locale_str = language_to_locale(language_name)
    collator = Collator.createInstance(Locale(locale_str))

    # Configure Case and Diacritic (Accent) rules via Collator Strength
    # - PRIMARY:   Only looks at the base letter (ignores case AND accents).
    # - SECONDARY: Looks at base letters + accents (ignores case).
    # - TERTIARY:  Looks at base letters + accents + case (Default strict sorting).

    if options.ignore_case and options.ignore_diacritics:
        # Ignore both accent variations and case sizes
        collator.setStrength(Collator.PRIMARY)

    elif options.ignore_case and not options.ignore_diacritics:
        # Ignore upper vs lower case, but treat 'e' and 'é' as different letters
        collator.setStrength(Collator.SECONDARY)

    elif not options.ignore_case and options.ignore_diacritics:
        # Ignore accents, but treat 'A' and 'a' as different letters.
        # ICU handles this by setting strength to PRIMARY but turning on Case Level.
        collator.setStrength(Collator.PRIMARY)
        collator.setAttribute(UCollAttribute.CASE_LEVEL, UCollAttributeValue.ON)

    else:
        # Default: strict matching on both case and diacritics
        collator.setStrength(Collator.TERTIARY)

    # Configure Punctuation ignoring
    # In ICU, ignoring punctuation is called "Alternate Handling". Turning it
    # to SHIFTED moves punctuation tokens to the very end of the weight table,
    # effectively ignoring them during normal alphanumeric string comparison.
    if options.ignore_punctuation:
        collator.setAttribute(
            UCollAttribute.ALTERNATE_HANDLING, UCollAttributeValue.SHIFTED
        )
    else:
        collator.setAttribute(
            UCollAttribute.ALTERNATE_HANDLING, UCollAttributeValue.NON_IGNORABLE
        )

    if options.lowercase_ordering:
        collator.setAttribute(
            UCollAttribute.CASE_FIRST, UCollAttributeValue.LOWER_FIRST
        )
    elif options.lowercase_ordering is False:
        collator.setAttribute(
            UCollAttribute.CASE_FIRST, UCollAttributeValue.UPPER_FIRST
        )

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
        "nalph": "The alphabet `1` is not known or not available.",
    }

    rules = {
        "Alphabet[]": """Alphabet[$Language]""",
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

     The alphabetic order of two characters:
     >> AlphabeticOrder["e", "f"]
      = 1

     The alphabetic order of two strings:
     >> AlphabeticOrder["apple", "banana"]
      = 1

     >> AlphabeticOrder["parrot", "parrot"]
      = 0

     When words are the same but only differ in case, usually lowercase letters come first:
     >> AlphabeticOrder["A", "a"]
      = -1

     However, you can for which case comes first using the 'CaseOrdering' option:
     >> AlphabeticOrder["a", "A", CaseOrdering -> "LowerFirst"]
      = 1

     >> AlphabeticOrder["a", "A", CaseOrdering -> "UpperFirst"]
      = -1

     >> AlphabeticOrder["a", "A"] ==  AlphabeticOrder["a", "A", CaseOrdering -> "LowerFirst"]
      = True

     Longer words follow their prefixes:
     >> AlphabeticOrder["Papagayo", "Papa", "Spanish"]
      = -1

     But accented letters usually appear at the end of the alphabet:
     >> AlphabeticOrder["Papá", "Papa", "Spanish"]
      = -1

     >> AlphabeticOrder["Papá", "Papagayo", "Spanish"]
      = 1

     The alphabetic ordering is determined by the value of <url>:$Language:
     doc/reference-of-built-in-symbols/global-system-information/$language/</url>. However, \
     specify a the language as the third argument:
     >> AlphabeticOrder["ñ", "n", "Spanish"]
      = -1

     Option 'IgnorePunctuation' specifies whether to remove puctuation characters before comparing the strings:

     >> AlphabeticOrder["Name-1", "Name.1", "Spanish", IgnorePunctuation -> True]
      = 0

     >> AlphabeticOrder["it's", "its", "English", IgnorePunctuation -> False]
      = 1

     >> AlphabeticOrder["it's", "its", "English", IgnorePunctuation -> True]
      = 0
    """

    eval_error = Builtin.generic_argument_error
    expected_args = range(1, 4)
    options = {
        "System`CaseOrdering": "Automatic",
        "System`IgnoreCase": "False",
        "System`IgnoreDiacritics": "False",
        "System`IgnorePunctuation": "False",
        "System`Language": "$Language",
    }
    summary_text = "return -1, 0, 1 comparing the alphabetic order of two strings"

    def eval(
        self, string1: String, string2: String, evaluation: Evaluation, options: dict
    ):
        """AlphabeticOrder[string1_String, string2_String, OptionsPattern[%(name)s]]"""
        lang = String(LANGUAGE)
        return self.eval_with_lang(string1, string2, lang, options, evaluation)

    def eval_with_lang(
        self,
        string1: String,
        string2: String,
        lang: String,
        options: dict,
        evaluation: Evaluation,
    ):
        """AlphabeticOrder[string1_String, string2_String, lang_String, OptionsPattern[%(name)s]]"""

        alphabetic_order_options = AlphabeticOrderOptions.from_dict(options, evaluation)
        if alphabetic_order_options is None:
            return

        return Integer(
            eval_alphabetic_order(
                string1.value,
                string2.value,
                lang.value,
                alphabetic_order_options,
            )
        )
