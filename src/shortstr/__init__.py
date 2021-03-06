# ShortStr is a Python module to generate unambiguous, homoglyph-less strings for URL shortners or similar services.
# By Al Sweigart al@inventwithpython.com

# For example, Pastebin generates "shortstrings" for its URLs: https://pastebin.com/mKxTdEeT

# In orthography and typography, a homoglyph is one of two or more graphemes,
# characters, or glyphs with shapes that appear identical or very similar.
# Example: 0 and O

import doctest
import random
import sys
import zlib

__version__ = '1.0.1'

# Doesn't contain homoglyphs: l, I, o, O, 0, 1
GLYPHS = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
LEN_GLYPHS = len(GLYPHS)

LETTERS   = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
LOWERCASE = 'abcdefghijkmnpqrstuvwxyz'
UPPERCASE = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
DIGITS    = '23456789'

HOMOGLYPHS = 'lIoO01'
HOMOGLYPHS_LETTERS = 'lIoO'
HOMOGLYPHS_LOWERCASE = 'lo'
HOMOGLYPHS_UPPERCASE = 'IO'
HOMOGLYPHS_DIGITS = '01'

GLYPHS_INCLUDING_HOMOGLYPHS    = GLYPHS    + HOMOGLYPHS
LETTERS_INCLUDING_HOMOGLYPHS   = LETTERS   + HOMOGLYPHS_LETTERS
LOWERCASE_INCLUDING_HOMOGLYPHS = LOWERCASE + HOMOGLYPHS_LOWERCASE
UPPERCASE_INCLUDING_HOMOGLYPHS = UPPERCASE + HOMOGLYPHS_UPPERCASE
DIGITS_INCLUDING_HOMOGLYPHS    = DIGITS    + HOMOGLYPHS_DIGITS

DEFAULT_LENGTH = 5

RUNNING_PY_2 = sys.version_info[0] < 3


# Quick sanity check; the GLYPHS string assignment line should NEVER change and NEVER contain homoglyphs.
assert len(frozenset(GLYPHS)) == 56 # Note: Don't use LEN_GLYPHS here; we want to specifically check that GLYPHS assignment source code hasn't changed.
assert 'l' not in GLYPHS
assert 'I' not in GLYPHS
assert 'o' not in GLYPHS
assert 'O' not in GLYPHS
assert '0' not in GLYPHS
assert '1' not in GLYPHS

# Uses the platform's source of entropy for true randomness, not pseudorandomness.
SYS_RAND = random.SystemRandom()


class ShortStrException(Exception):
    """This exception is raised for any shortstr-releated exception. If the
    shortstr module ever raises an exception besides ShortStrException, assume
    that it is caused by a bug."""
    pass


def generate(ssformat='*' * DEFAULT_LENGTH, includeChecksum=True, repeatFunc=None):
    """Returns a short string with the given format. The format string is
    a mini-language, with each character representing a range of characters:

    * - Any character.
    c - Any letter character.
    l - Any lowercase letter character.
    u - Any uppercase letter character.
    d - Any digit, 2-9.

    For example, '******' will return a shortstring of 6 characters. For another
    example, 'cdddcc' will return a shortstring that starts with a letter,
    followed by three digits, followed by three more letters.

    (These ranges will never include the homoglyph characters l, I, o, O, 0, 1.)

    If includeChecksum is True, the last character is not random but rather used
    to provide a checksum for the rest of the short string.

    Optionally, a function can be provided to check if the short string is a
    repeat of one made before. This function is passed one string argument and
    returns True if the string has been generated before and False if it hasn't.

    If repeatFunc is None, no function is called.

    If you have a list of strings that have been generated before, you can pass:

        repeatFunc=lambda ss: ss in ['list', 'of', 'repeats']

    ...for the repeatFunc parameter.
    """

    # Generate a random shortstr
    while True: # loop until an unrepeated shortstr has been generated
        ss = []

        for i, specifier in enumerate(ssformat):
            if specifier == '*':
                ss.append(SYS_RAND.choice(GLYPHS))
            elif specifier == 'c':
                ss.append(SYS_RAND.choice(LETTERS))
            elif specifier == 'd':
                ss.append(SYS_RAND.choice(DIGITS))
            elif specifier == 'l':
                ss.append(SYS_RAND.choice(LOWERCASE))
            elif specifier == 'u':
                ss.append(SYS_RAND.choice(UPPERCASE))
            else:
                raise ShortStrException('"%s" is an invalid shortstr format specifier: must be *, c, d, l, or u' % specifier)

        # Add checksum, if needed.
        if includeChecksum:
            if RUNNING_PY_2:
                checksum = zlib.adler32(''.join(ss).decode('utf-8'))
            else:
                checksum = zlib.adler32(bytes(''.join(ss), encoding='utf-8'))
            ss.append(GLYPHS[checksum % LEN_GLYPHS])

        ssAsString = ''.join(ss)

        if repeatFunc is None or not repeatFunc(ssAsString):
            return ssAsString # sAsStringt is not a repeat, so we can now return
        # Otherwise, continue and try generating a new shortstring.


def isValid(ssToCheck):
    """Returns True if ssToCheck is a shortstr with a valid checksum. Note that
    to have a valid checksum, ssToCheck must have been generated by
    generate() with includeChecksum=True.

    >>> isValid('QEynbi')
    True
    >>> isValid('QEynbX')
    False
    """

    # Validate ssToCheck argument.
    if not isinstance(ssToCheck, str) or len(ssToCheck) < 2:
        raise ShortStrException('ssToCheck argument must be a string at least two characters long')

    if RUNNING_PY_2:
        checksum = zlib.adler32(ssToCheck[:-1].decode('utf-8'))
    else:
        checksum = zlib.adler32(bytes(ssToCheck[:-1], encoding='utf-8'))

    return ssToCheck[-1] == GLYPHS[checksum % LEN_GLYPHS] # Make sure last character in ssToCheck is the correct checksum character.


def _checkSSFormatArg(ssformat):
    """Checks if ssformat is a valid format string for generate(). A
    valid format string only contains the characters *, c, l, u, and d. Raises
    ShortStrException if an invalid character is found. The ssformat argument
    cannot be an empty string. Always returns None.

    >>> _checkSSFormatArg('******')
    >>> _checkSSFormatArg('cdddcc')
    >>> _checkSSFormatArg('XYZ')
    Traceback (most recent call last):
      ...
    ShortStrException: ssformat argument must be a string with only characters *, c, l, u, and d
    """
    if ssformat == '':
        raise ShortStrException('ssformat argument cannot be the empty string')

    if not isinstance(ssformat, str):
        raise ShortStrException('ssformat argument must be a string with only characters *, c, l, u, and d')

    for c in ssformat:
        if c not in '*clud':
            raise ShortStrException('ssformat argument must be a string with only characters *, c, l, u, and d')



if __name__ == '__main__':
    doctest.testmod()
