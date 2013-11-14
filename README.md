handy-python
============

Some handy python code.

DebugWraper.py
--------------

Contains wrapper for debugging calls on object
plus few handy functions, including one to show
type in similar fashion to Haskell types.

extract-partial-zip.py
----------------------

This simple tool is intended for cases when you download large zip
archive and want inspect content in already downloaded part. Already
extracted parts are skipped.

Archive is not held in whole in memory, archived files though are
(possible future enhancement?).

In case you want to recover broken zip, you may prefer to
use `zip -FF` instead. However, this script is designed to
be easily modifiable, so you can turn off some checks
and try to use is for recovery too.

