from pyaedt.edb_core.IPC2581.ecad.cad_data.package.assembly_drawing import AssemblyDrawing
from pyaedt.edb_core.IPC2581.ecad.cad_data.package.pin import Pin


class Package(object):
    def __init__(self):
        self.name = ""
        self.type = "OTHER"
        self.pin_one = "1"
        self.pin_orientation = "OTHER"
        self.height = 0.1
        self.assembly_drawing = AssemblyDrawing()
        self._pins = []

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, value):
        if isinstance(value, list):
            if len([pin for pin in value if isinstance(pin, Pin)]) == len(value):
                self._pins = value

    def add_pin(self, pin=None):
        if isinstance(pin, Pin):
            self._pins.append(pin)

    def write_xml(self):
        pass
