class PadstackPadDef(object):
    def __init__(self):
        self.layer_ref = ""
        self.pad_use = PadUse().Regular
        self.x = 0.0
        self.y = 0.0
        self.primitive_ref = "CIRCLE_DEFAULT"

    def write_xml(self):
        pass


class PadUse(object):
    (Regular, Antipad, Thermal) = range(1, 3)
