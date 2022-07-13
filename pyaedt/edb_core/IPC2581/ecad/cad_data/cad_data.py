from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.layer import Layer
from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.stackup import Stackup
from pyaedt.edb_core.IPC2581.ecad.cad_data.step import Step



class CadData(object):
    def __init__(self):
        self._layers = []
        self.stackup = Stackup()
        self.cad_data_step = Step()

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, value):
        if isinstance(value, list):
            if len([lay for lay in value if isinstance(lay, Layer)]):
                self._layers = value

    def add_layer(self, obj):
        if isinstance(obj, Layer):
            self.layers.append(obj)
            return True
        return False

    def write_xml(self):
        pass
