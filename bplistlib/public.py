# encoding: utf-8
"""This file contains the public functions for the module bplistlib."""


from cStringIO import StringIO
import plistlib
from .readwrite import read, write


#########
## API ##
#########


def dump(obj, fp, binary=False):
    if binary is True:
        write(obj, fp)
    else:
        plistlib.writePlist(obj, fp)


def dumps(obj, binary=False):
    fp = StringIO()
    dump(obj, fp, binary)
    return fp.getvalue()


def load(fp, binary=None):
    if binary is None:
        if fp.read(8) == 'bplist00':
            binary = True
        else:
            fp.seek(0)  # I'm not sure if this is necessary
            binary = False
    if binary is True:
        root_object = read(fp)
    elif binary is False:
        root_object = plistlib.readPlist(fp)    
    return root_object


def loads(s, binary=None):
    return load(StringIO(s), binary)


################
## Legacy API ##
################


def readPlist(path_or_file, binary=None):
    """
    Read a plist from path_or_file. If the named argument binary is set to
    True, then assume path_or_file is a binary plist. If it's set to false,
    then assume it's an xml plist. Otherwise, try to detect the type and act
    accordingly. Return the root object.
    """
    did_open = False
    if isinstance(path_or_file, (str, unicode)):
        path_or_file = open(path_or_file)
        did_open = True
    root_object = load(path_or_file, binary)
    if did_open:
        path_or_file.close()
    return root_object


def writePlist(root_object, path_or_file, binary=False):
    """
    Write root_object to path_or_file. If the named argument binary is set
    to True, write a binary plist, otherwise write an xml one.
    """
    did_open = False
    if isinstance(path_or_file, (str, unicode)):
        path_or_file = open(path_or_file, "w")
        did_open = True
    dump(root_object, path_or_file, binary)
    if did_open:
        path_or_file.close()


writePlistToString = dumps
readPlistFromString = loads
