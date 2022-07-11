from pyaedt.edb_core.IPC2581.ipc2581 import IPC2581
from pyaedt.edb_core.IPC2581.ecad.cad_header.spec import Spec



class CadHeader(object):
    def __init__(self):
        self.units = IPC2581.units
        self._specs = []

    @property
    def specs(self):
        return self.units

    @specs.setter
    def specs(self, value):
        if isinstance(value, list):
            if len([spec for spec in value if isinstance(spec, Spec)]) == len(value):
                self._specs = value

    def add_spec(self, spec=None):
        if isinstance(spec, Spec):
            self._specs.append(spec)

    def write_xml(self):
        pass
