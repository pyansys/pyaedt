class Pin(object):
    def __init__(self):
        self.number = ""
        self.electrical_type = ElectricalType().Electrical
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.primitive_def = ""
        self.is_via = False

    def write_xml(self):
        pass


class Type(object):
    (Thru, Surface) = range(1, 2)


class ElectricalType(object):
    (Electrical, Machanical) = range(1, 2)
