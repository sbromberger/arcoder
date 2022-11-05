# pylint: disable=invalid-name, too-few-public-methods
"""
arcoder.py implements an abstract base class called `Encoder` along with two concrete
implementations: `ARCoder` and `Holmes`. Each has an `encode` method that takes a
string and encodes it into a series of symbols designed to be used for similarity
measurements.
"""
from abc import ABC, abstractmethod
import itertools
import re
from typing import List, Set, Tuple


class Encoder(ABC):
    """An abstract base class requiring an encode() method"""

    @abstractmethod
    def encode(self, s: str) -> List[str]:
        """Encodes a string into a list of possible encodings."""


class ARCoder(Encoder):
    """ARCoder implements the Transliterated Arabic Name Matching algorithm described
    in Moore, J., Hamid, S., and Bromberger, S., _An Evaluation of Transliterated
    Arabic Name Matching Methods_.

    Example:

    >>> from arcoder import ARCoder
    >>> a = ARCoder()
    >>> a.encode("Sohaib")
    ['suhaeb', 'suhib']
    """

    encoder = {
        "c": ["s"],
        "g": ["k", "j"],
        "i": ["i", "e"],
        "o": ["u"],
        "p": ["b"],
        "q": ["k"],
        "u": ["u"],
        "v": ["f"],
        "w": ["u"],
        "y": ["e"],
        "z": ["s"],
        "Ch": ["h"],
        "e.": ["", "e"],
        "h.": [""],
        "t.": ["t", "d"],
        "ai": ["i", "ae"],
        "ay": ["i"],
        "eh": ["e"],
        "ch": ["0"],
        "gh": ["k"],
        "iy": ["e"],
        "kh": ["k"],
        "ph": ["f"],
        "ou": ["u"],
        "oo": ["u"],
        "sh": ["0"],
        "th": ["z"],
        "ua": ["a", "ua", "uwa"],
        "wu": ["u"],
        "‘": ["a"],
        "'": ["", "w"],
    }
    VALID_CHARS = re.compile(r"[a-zA-Z\‘\'\- ]")

    def _encode(self, s: str, final: bool = False) -> Tuple[List[str], int]:
        # if None, nothing was found.
        # s is either 1 or 2 chars. Only 1 if final.
        len_s = len(s)
        d = ARCoder.encoder

        # first, try to get 2-char matches, but only for two-char inputs.
        if len_s == 2 or final:
            force_two_char = s + "." if len_s == 1 else s
            encoded: Set[str] = set()
            encoded = encoded.union(d.get(force_two_char, []))
            encoded = encoded.union(d.get(force_two_char.lower(), []))
            if encoded:
                return (list(encoded), 2)

        # No two char? ok, so let's just take the first character.
        ch = s[0]
        encoded = encoded.union(d.get(ch, []))
        encoded = encoded.union(d.get(ch.lower(), []))
        if encoded:
            return (list(encoded), 1)

        # not found - return the first character unchanged.
        return ([ch.lower()], 1)

    def _compress(s: str) -> str:  # pylint: disable=no-self-argument
        return re.sub(r'(.)\1+', r'\1', s)

    def encode(self, s: str) -> List[str]:
        """encode encodes a string into a sequence of tokens using
        the given encoding method."""

        filtered = ''.join(filter(ARCoder.VALID_CHARS.match, s.lower()))
        filtered_spaces = filtered.replace('-', ' ')
        undup = ''.join(i for i, _ in itertools.groupby(filtered_spaces))
        undup_title = ''.join(word.capitalize() for word in undup.split())

        l_comp_str = len(undup_title)
        i = 0
        encoded = []
        while i < l_comp_str:
            substr = undup_title[i : i + 2]
            encodings, inc = self._encode(substr, i == l_comp_str - 1)
            encoded.append(encodings)
            i += inc

        cartprod = itertools.product(*encoded)
        return list(set(ARCoder._compress("".join(list(x))) for x in cartprod))


class Holmes(Encoder):
    """Holmes implements the Transliterated Arabic Name Matching algorithm described
    in Holmes, D., Kashfi, S., Aqeel, S. U.: _Transliterated arabic name search_,
    Communications, Internet, and Information Technology, pp. 267--273. (2004).

    Example:

    >>> from arcoder import Holmes
    >>> h = Holmes()
    >>> h.encode("Sohaib")
    ['sohayb']
    """

    P = "prefix"
    S = "suffix"
    A = "anywhere"
    rules = {
        1.001: ("al-", "", P),
        1.002: ("al ", "", P),
        1.003: ("el-", "", P),
        1.004: ("el ", "", P),
        1.005: ("abul", "", P),
        1.006: ("abu ", "", P),
        2.001: ("-", "", A),
        2.002: ("'", "", A),
        2.003: (" ", "", A),
        3.001: ("abdal", "abdul", A),
        3.002: ("abdel", "abdul", A),
        3.003: ("abdol", "abdul", A),
        3.004: ("der", "dur", A),
        3.005: ("q", "k", A),
        3.006: ("allah", "ullah", A),
        3.007: ("ean", "id", S),
        3.008: ("ead", "id", S),
        3.009: ("ai", "ay", A),
        3.010: ("e", "i", A),
        3.011: ("ou", "u", A),
        3.012: ("aee", "ay", A),
        3.013: ("o", "u", P),
        3.014: ("ah", "a", A),
        3.015: ("ae", "ay", A),
        3.016: ("ei", "ay", P),
        3.017: ("gh", "k", P),
        3.018: ("kh", "k", A),
        3.019: ("kah", "ka", A),
        3.020: ("ie", "i", A),
        3.021: ("awo", "ao", A),
        3.022: ("awu", "au", A),
        3.023: ("awz", "az", A),
        3.024: ("dh", "d", A),
        3.025: ("ou", "k", A),  # really?
        3.026: ("kua", "ka", A),
        3.027: ("aw", "au", A),
        3.028: ("v", "w", A),
        3.029: ("say", "sy", P),
        3.030: ("g", "j", P),
        3.031: ("sw", "s", P),
        4.005: ("ee", "i", A),
        4.015: ("oo", "u", A),
        # 4.* - all other doubles, reduce to single
        5.001: ("ed", "ad", S),
        5.002: ("el", "al", S),
        5.003: ("eh", "a", S),
        5.004: ("y", "i", S),
        5.005: ("ii", "i", S),
        5.006: ("iya", "ia", A),
        5.007: ("ah", "a", A),
        5.008: ("ry", "ri", A),
        5.009: ("mo", "mu", P),
        5.010: ("eya", "ia", S),
    }

    def _encode_rule(num: float, s: str) -> str:  # pylint: disable=no-self-argument
        if 4.015 < num < 5.000:
            s = re.sub(r'(.)\1+', r'\1', s)
        else:
            (orig, subst, location) = Holmes.rules[num]
            if location == Holmes.P:
                if s.startswith(orig):
                    s = s.replace(orig, subst, 1)

            elif location == Holmes.S:
                if s.endswith(orig):
                    l = len(orig)
                    s = s[:-l] + subst

            elif location == Holmes.A:
                s = s.replace(orig, subst)
            else:
                raise ValueError("Invalid Location")

        return s

    def encode(self, s: str) -> List[str]:
        s = s.lower()

        rules = sorted(list(Holmes.rules.keys()) + [4.200])
        for rule in rules:
            s = Holmes._encode_rule(rule, s)

        return [s]
