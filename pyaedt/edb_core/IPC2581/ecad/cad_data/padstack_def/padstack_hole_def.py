class PadstackHoleDef(object):
    def __init__(self):
        self.name = ""
        self.diameter = 0.0
        self.plating_status = PlatingStatus().PLATED
        self.plus_tol = 0.0
        self.minus_tol = 0.0
        self.x = 0.0
        self.y = 0.0

    def write_xml(self):
        pass

class PlatingStatus(object):
    (PLATED) = range(1)