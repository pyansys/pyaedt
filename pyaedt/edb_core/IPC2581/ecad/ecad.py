from pyaedt.edb_core.IPC2581.ecad.cad_header.spec import Spec
from pyaedt.edb_core.IPC2581.ecad.cad_header.cad_header import CadHeader
from pyaedt.edb_core.IPC2581.ecad.cad_data.cad_data import CadData


class Ecad(object):
    def __init__(self):
        self.design_name = "Design"
        self.cad_header = CadHeader()
        self.cad_data = CadData()

    def write_xml(self):
        pass
