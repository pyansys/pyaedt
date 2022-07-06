class Content(object):
    def __init__(self):
        self._mode = self.Mode().Stackup
        self._design_units = IPC2581.units
        self._role_ref = "Owner"
        self._function_mode = self.Mode().Stackup
        self._step_ref = "Ansys_IPC2581"
        self._layer_ref = self.LayerRef()
        self._dict_colors = self.DictionaryColor()
        self._dict_path_width = self.PathWidthDictionary()
        self._standard_geometries_dict =

    class Mode(object):
        (Stackup) = range(1)