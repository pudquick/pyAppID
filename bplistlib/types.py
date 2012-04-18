"""
Some classes that can be encoded in a binary plist but don't map into
python's type hierarchy.
"""

class UID(int):
    """A class for integer UID values."""
    def __init__(self, value):
        int.__init__(self, value)
    
    def __repr__(self):
        return 'UID(%i)' % self
    

class FillType(object):
    """A class for 'Fill', whatever that means."""
    def __repr__(self):
        return 'Fill'
    


Fill = FillType()