class Component(object):
    def __init__(self):
        self.refdes = ""
        self.package_ref = ""
        self.layer_ref = ""
        self.part = ""
        self.mount_type = MountType().SMT
        self.stand_off = 0.0
        self.height = 0.0
        self.location = [0.0, 0.0]
        self.rotation = 0.0
        self.type = Type().Rlc
        self.value = ""

    def write_xml(self):
        pass

class MountType(object):
    (SMT, THMT) = range(1, 2)

class Type(object):
    (Rlc, Discrete) = range(1,2)