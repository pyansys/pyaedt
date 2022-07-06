from pyaedt.edb_core.IPC2581.ipc2581 import IPC2581


class Type(object):
    (Circle, Rectangle) = range(1, 2)


class StandardGeometriesDictionary(object):
    def __init__(self):
        self.units = IPC2581.units
        self.standard_circ_dict = {}
        self.standard_rect_dict = {}
        self.standard_oval_dict = {}
        self.user_defined_dict = {}

    def write_xml(self):
        pass
