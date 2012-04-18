# encoding: utf-8
"""
bplistlib: Read and write binary .plist files.

This module is a drop-in enhancement of the plistlib module in the
standard libary. It provides four functions, which each have the same
call signature as a function with the same name in plistlib, with the
addition of anoptional keyword argument, binary.

To write a plist use one of:

    writePlist(root_object, path_or_file)
    writePlistToString(root_object)

Called like this, these functions will write an xml plist using
plistlib. To write a binary plist, use one of:

    writePlist(root_object, path_or_file, binary=True)
    writePlistToString(root_object, binary=True)

To read a plist use one of:

    readPlist(path_or_file)
    readPlistFromString(data)

Like this, these functions will attempt to determine whether the plist
is binary or xml. If you know you have a binary plist, you can use one
of:

    readPlist(path_or_file, binary=True)
    readPlistFromString(data, binary=True)

If you know you have an xml plist, you can use:

    readPlist(path_or_file, binary=False)
    readPlistFromString(data, binary=False)


Known issues:
The actual plist format is more restrictive than is enforced here. In
particular, key values in a plist dictionary must be strings, which is
not enforced. There may be other unenforced restrictions, be reasonable.
"""

# TODO: update docstrings
# TODO: reorganize for fewer files
# TODO: autodetect byte length for strings by characters used, not python type
# TODO: set type, id is 0xc
# TODO: only data, string, array, set, and dict support extended int count
# TODO: date is always 8 byte float, len=3
# deduplicating booleans is unnessesary, skip it


from .public import readPlist, readPlistFromString
from .public import writePlist, writePlistToString
from .public import dump, dumps, load, loads
from .types import UID, Fill


__all__ = ['readPlist', 'readPlistFromString',
           'writePlist', 'writePlistToString',
           'UID', 'Fill',
           'dump', 'dumps', 'load', 'loads']

__packages__ = ['bplistlib']
__version__ = '0.2pre'
__author__ = 'Stephen Morton'
__author_email__ = 'tungolcraft@gmail.com'
__description__ = 'Read and write binary .plist files.'
__license__ = 'BSD'
__platforms__ = 'any'
__url__ = 'https://github.com/tungolcraft/bplistlib'
__classifiers__ = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: BSD License',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Software Development :: Libraries :: Python Modules',
]
