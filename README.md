# shortstr

ShortStr is a Python module to generate unambiguous, homoglyph-less "shortstrings" for URL shortners and similar services.

`pip install shortstr`

Websites such as Pastebin have unique alphanumeric strings IDs, like https://pastebin.com/mKxTdEeT. Code like `''.join([random.choice(string.ascii_letters + string.digits) for x in range(5)])` can be used to generate strings like `'DY6iv'`, but these can include similar-looking characters (called homoglyphs) like O and 0.

The shortstr module generates these shortstrings without the l, I, o, O, 0, and 1 homoglyphs. It also has checksum and can check for repeat shortstrings to ensure you only produce unique shortstrings, and uses `os.urandom()` to produce truly random shortstrings, not pseudorandom shortstrings.

## Examples

    >>> import shortstr
    >>> shortstr.generate()
    'kZXmL9'
    >>> shortstr.generate('ddddd')
    '67249f'
    >>> shortstr.generate('ddddd', includeChecksum=False)
    '39844'
    >>> shortstr.generate('ccccc', includeChecksum=False)
    'gKXda'
    >>> shortstr.generate('lllll', includeChecksum=False)
    'qibkp'
    >>> shortstr.generate('uuuuu', includeChecksum=False)
    'WWXGC'
    >>> shortstr.generate('***dddcccllluuu', includeChecksum=False)
    '5SP534FiBtxtMCG'
    >>> shortstr.isValid('kZXmL9')
    True
    >>> shortstr.isValid('67249f')
    True
    >>> shortstr.isValid('invalid shortstring')
    False


Support
-------

If you find this project helpful and would like to support its development, [consider donating to its creator on Patreon](https://www.patreon.com/AlSweigart).
