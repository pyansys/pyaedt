from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_hole_def import PadstackHoleDef
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_pad_def import PadstackPadDef


class PadstackDef(object):
    def __init__(self):
        self.name = ""
        self.padstack_hole_def = PadstackHoleDef()
        self._padstack_pad_def = []

    @property
    def padstack_pad_def(self):
        return self._padstack_pad_def

    @padstack_pad_def.setter
    def padstack_pad_def(self, value):
        if isinstance(value, list):
            if len([pad for pad in value if isinstance(pad, PadstackPadDef)]) == len(value):
                self._padstack_pad_def = value

    def add_padstack_pad_def(self, pad):
        if isinstance(pad, PadstackPadDef):
            self._padstack_pad_def.append(pad)

    def write_xml(self):
        pass
