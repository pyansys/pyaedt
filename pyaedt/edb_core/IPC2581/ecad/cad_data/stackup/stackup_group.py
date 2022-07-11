from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.layer import Layer


class StackupGroup(object):
    def __init__(self):
        self.name = "GROUP_PRIMARY"
        self.thickness = 0.0
        self.tol_plus = 0.0
        self.tol_minus = 0.0
        self._stackup_layers = []

    @property
    def stackup_layers(self):
        return self._stackup_layers

    @stackup_layers.setter
    def stackup_layers(self, value):
        if isinstance(value, list):
            if len([lay for lay in value if isinstance(lay, Layer)]):
                self._stackup_layers = value

    def write_xml(self):
        pass

    def add_layer(self, layer=None):
        if isinstance(layer, Layer):
            self._stackup_layers.append(layer)
