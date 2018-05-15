import os
import pytest
import random
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shortstr

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# NOTE: Because of the nature of shortstr, these tests are nondeterminstic.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

TRIALS = 100 # Increase this for more thorough testing, decrease to make tests faster.

ALLOWED_GLYPHS = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
DISALLOWED_HOMOGLYPHS = 'lIoO01'

def _isValidShortStr(ss, length=None):
    # Check that ss doesn't have any homoglyphs in it.
    if length is not None:
        assert len(ss) == length

    for c in ss:
        if c not in ALLOWED_GLYPHS or c in DISALLOWED_HOMOGLYPHS:
            return False
    return True

def test__isValidShortStr():
    assert _isValidShortStr('abc')
    assert not _isValidShortStr('0O0O0O')
    with pytest.raises(AssertionError):
        _isValidShortStr('abc', 42)


def test_glyphs_constant():
    # Test for any changes to glyphs:
    assert shortstr.GLYPHS == ALLOWED_GLYPHS

    # Test that no homoglyph exists in glyphs:
    for homoglyph in DISALLOWED_HOMOGLYPHS:
        assert homoglyph not in shortstr.GLYPHS


def test_generate():
    # Basic validity tests.

    for trial in range(TRIALS): # Because shortstr is random, we'll do multiple trials.

        # Test default args
        ss = shortstr.generate()
        assert type(ss) == str
        assert _isValidShortStr(ss, shortstr.DEFAULT_LENGTH + 1)

        # Test other parameters
        ss = shortstr.generate('******')
        assert type(ss) == str
        assert _isValidShortStr(ss, 6 + 1)


        ss = shortstr.generate('**', True)
        assert type(ss) == str
        assert _isValidShortStr(ss, 2 + 1)

        ss = shortstr.generate('**', False)
        assert type(ss) == str
        assert _isValidShortStr(ss, 2)

        ss = shortstr.generate('**', False, None)
        assert type(ss) == str
        assert _isValidShortStr(ss, 2)

        ss = shortstr.generate('**', True, lambda x: False)
        assert type(ss) == str
        assert _isValidShortStr(ss, 2 + 1)

        ss = shortstr.generate(ssformat='******')
        assert type(ss) == str
        assert _isValidShortStr(ss, 6 + 1)

        ss = shortstr.generate(includeChecksum=False)
        assert type(ss) == str
        assert _isValidShortStr(ss, shortstr.DEFAULT_LENGTH)

        ss = shortstr.generate(repeatFunc=None)
        assert type(ss) == str
        assert _isValidShortStr(ss, shortstr.DEFAULT_LENGTH + 1)


def test_format_param():
    # Test generate()'s ssformat parameter.

    for trial in range(TRIALS): # Because shortstr is random, we'll do multiple trials.
        # Test * format specifier
        ss = shortstr.generate('******', includeChecksum=False)
        assert _isValidShortStr(ss, 6)
        for i in range(6):
            assert ss[i].isalnum()

        # Test d format specifier
        ss = shortstr.generate('d' * 30, includeChecksum=False)
        assert _isValidShortStr(ss, 30)
        for i in range(30):
            assert ss[i].isdigit()

        # Test c format specifier
        ss = shortstr.generate('c' * 27, includeChecksum=False)
        assert _isValidShortStr(ss, 27)
        for i in range(27):
            assert ss[i].isalpha()

        # Test l format specifier
        ss = shortstr.generate('l' * 31, includeChecksum=False)
        assert _isValidShortStr(ss, 31)
        for i in range(31):
            assert ss[i].islower()

        # Test u format specifier
        ss = shortstr.generate('u' * 19, includeChecksum=False)
        assert _isValidShortStr(ss, 19)
        for i in range(19):
            assert ss[i].isupper()

        # Test a big string with all of the format specifiers.
        ss = shortstr.generate('*' * 1000 + 'c' * 1000 + 'd' * 1000 + 'l' * 1000 + 'u' * 1000, includeChecksum=False)
        assert _isValidShortStr(ss, 5000)
        for i in range(0, 1000):
            assert ss[i].isalnum()
        for i in range(1000, 2000):
            assert ss[i].isalpha()
        for i in range(2000, 3000):
            assert ss[i].isdigit()
        for i in range(3000, 4000):
            assert ss[i].islower()
        for i in range(4000, 5000):
            assert ss[i].isupper()


def test_includeChecksum_param():
    # Test the includeChecksum paramter
    for trial in range(TRIALS):
        ss = shortstr.generate('*' * 6, includeChecksum=True)
        assert _isValidShortStr(ss, 6 + 1)
        for i in range(6 + 1):
            assert ss[i].isalnum()

        assert(shortstr.isValid(ss))


def test_repeatFunc_param():
    # Test the repeatFunc param
    for trial in range(TRIALS):
        # Just make sure this doesn't raise any exceptions.
        ss = shortstr.generate('*', repeatFunc=None)
        assert _isValidShortStr(ss, 2)

        # Create a function that only returns False 1 in a 10 times. We're just making sure it doesn't hang completely.
        ss = shortstr.generate('*', repeatFunc=lambda x: False if random.randint(0, 10) == 0 else True)
        assert _isValidShortStr(ss, 2)

        # Keep generating shortstrings until 'A' is generated.
        ss = shortstr.generate('*', includeChecksum=False, repeatFunc=lambda x: x != 'A')
        assert _isValidShortStr(ss, 1)


def test__checkSSFormatArg():
    with pytest.raises(shortstr.ShortStrException):
        shortstr._checkSSFormatArg('')

    with pytest.raises(shortstr.ShortStrException):
        shortstr._checkSSFormatArg(42)

    with pytest.raises(shortstr.ShortStrException):
        shortstr._checkSSFormatArg('**********X')


def test_isValid():
    assert shortstr.isValid('QEynbi')
    assert not shortstr.isValid('QEynbX')

    # Test that 1 or 2 character strings causes an exception.
    with pytest.raises(shortstr.ShortStrException):
        shortstr.isValid('')

    with pytest.raises(shortstr.ShortStrException):
        shortstr.isValid('X')

    # Test that non-strings cause an exception.
    with pytest.raises(shortstr.ShortStrException):
        shortstr.isValid(42)


def test_performance():
    # We should be able to generate far more than 1000 of these in under a
    # second. If not, something is deeply wrong.
    startTime = time.time()
    for i in range(1000):
        shortstr.generate()
    assert time.time() - startTime < 1



if __name__ == '__main__':
    pytest.main()
