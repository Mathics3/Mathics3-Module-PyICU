# -*- coding: utf-8 -*-

from mathics.core.atoms import String
from mathics.core.load_builtin import import_and_load_builtins
from mathics.session import MathicsSession

import_and_load_builtins()

session = MathicsSession(character_encoding="UTF-8")
assert session.evaluate('LoadModule["pymathics.icu"]') == String("pymathics.icu")


def check_evaluation(str_expr: str, expected: str, assert_message=""):
    """Helper function to test that a Mathics expression against
    its results"""
    result = session.evaluate(str_expr).value

    if assert_message:
        assert result == expected, f"{assert_message}: got: {result}"
    else:
        assert result == expected


def test_alphabet():
    check_evaluation(
        'Alphabet["es"]',
        (
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "á",
            "é",
            "í",
            "ñ",
            "ó",
            "ú",
            "ü",
        ),
    )
