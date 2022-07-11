from pyaedt.edb_core.IPC2581.ecad.cad_data.stackup.stackup_group import StackupGroup


class Stackup(object):
    def __init__(self):
        self.name = "PRIMARY"
        self._total_thickness = 0.0
        self._tol_plus = 0.0
        self._tol_min = 0.0
        self.where_measured = "METAL"
        self._stackup_group = []

    @property
    def stackup_group(self):
        return self._stackup_group

    @stackup_group.setter
    def stackup_group(self, value):
        if isinstance(value, list):
            if len([stack_grp for stack_grp in value if isinstance(stack_grp, StackupGroup)]):
                self._stackup_group = value

    def add_stackup_group(self, stackup_group=None):
        if isinstance(stackup_group, StackupGroup):
            self.stackup_group.append(stackup_group)

    def write_xml(self):
        pass
