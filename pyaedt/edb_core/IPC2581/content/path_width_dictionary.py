from pyaedt.edb_core.IPC2581.ipc2581 import IPC2581


class PathWidthDictionary(object):
    def __init__(self):
        self.units = IPC2581.units
        self.path_width_dict = {}

    def write_xml(self):
        pass
