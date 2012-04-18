# encoding: utf-8
"""This file contains private read/write functions for the bplistlib module."""

from .classes import ObjectHandler, TableHandler
from .classes import TrailerHandler
from .functions import get_byte_width


def read(file_object):
    """
    Read a binary plist from an open file object that supports seeking.
    Return the root object.
    """
    trailer = read_trailer(file_object)
    offset_size, reference_size, length, root, table_offset = trailer
    offsets = read_table(file_object, offset_size, length, table_offset)
    root_object = read_objects(file_object, offsets, reference_size, root)
    return root_object


def read_trailer(file_object):
    """Read and return the final, "trailer", section of an open file object."""
    trailer_handler = TrailerHandler()
    trailer = trailer_handler.decode(file_object)
    return trailer


def read_table(file_object, offset_size, length, table_offset):
    """
    Read an offset table from an open file object and return the decoded
    offsets.
    """
    table_handler = TableHandler()
    offsets = table_handler.decode(file_object, offset_size,
                                   length, table_offset)
    return offsets


def read_objects(file_object, offsets, reference_size, root):
    """Read from an open file_object and return the decoded root object."""
    object_handler = ObjectHandler()
    object_handler.set_reference_size(reference_size)
    objects = []
    for offset in offsets:
        file_object.seek(offset)
        object_ = object_handler.decode(file_object)
        objects.append(object_)
    root_object = objects[root]
    return object_handler.unflatten(root_object, objects)


def write(root_object, file_object):
    """Write the root_object to file_object."""
    file_object.write('bplist00')
    offsets = write_objects(file_object, root_object)
    table_offset = write_table(file_object, offsets)
    write_trailer(file_object, offsets, table_offset)


def write_objects(file_object, root_object):
    """
    Flatten all objects, encode, and write the encoded objects to file_object.
    """
    objects = []
    object_handler = ObjectHandler()
    object_handler.collect_objects(root_object, objects)
    object_handler.flatten_objects(objects)
    reference_size = get_byte_width(len(objects), 2)
    object_handler.set_reference_size(reference_size)
    offsets = []
    for object_ in objects:
        offsets.append(file_object.tell())
        encoded_object = object_handler.encode(object_)
        file_object.write(encoded_object)
    return offsets


def write_table(file_object, offsets):
    """Encode the offsets and write to file_object."""
    table_handler = TableHandler()
    table_offset = file_object.tell()
    table = table_handler.encode(offsets, table_offset)
    file_object.write(table)
    return table_offset


def write_trailer(file_object, offsets, table_offset):
    """Encode the trailer section and write to file_object."""
    trailer_handler = TrailerHandler()
    trailer = trailer_handler.encode(offsets, table_offset)
    file_object.write(trailer)
