from pyaedt.edb_core.IPC2581.content.content import Content
from pyaedt.edb_core.IPC2581.ecad.ecad import Ecad


class IPC2581(object):
    def __init__(self):
        self.revision = "C"
        self._units = self.Units().Inch
        self.content = Content()

    @property
    def units(self):
        return self.units

    @units.setter
    def units(self, value):
        if isinstance(value, int):
            self._units = value

    class Units(object):
        (Inch, MM) = range(1, 2)
