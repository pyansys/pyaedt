from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import PolyStep


class Path(object):
    def __init__(self):
        self.location_x = 0.0
        self.location_y = 0.0
        self._polyline = []
        self.line_width = ""
        self.width_ref_id = ""

    @property
    def polyline(self):
        return self._polyline

    @polyline.setter
    def polyline(self, value):
        if isinstance(value, list):
            if len([stp for stp in value if isinstance(stp, PolyStep)]) == len(value):
                self._polyline = value

    def add_poly_step_to_polyline(self, poly_step=None):
        if isinstance(poly_step, PolyStep):
            self._polyline.append(poly_step)