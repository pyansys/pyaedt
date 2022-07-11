class LogicalNets(object):
    def __init__(self):
        self._logical_nets = []

    @property
    def logical_nets(self):
        return self._logical_nets

    @logical_nets.setter
    def logical_nets(self, value):
        if isinstance(value, list):
            if len([net for net in value if isinstance(net, LogicalNet)]) == len(value):
                self._logical_nets = value

    def add_net(self, net=None):
        if isinstance(net, LogicalNet):
            self._logical_nets.append(net)

    def write_xml(self):
        pass


class LogicalNet(object):
    def __init__(self):
        self.name = ""
        self._pin_ref = []

    def write_xml(self):
        pass


class PinRef(object):
    def __init__(self):
        self.pin = ""
        self.component_ref = ""

    def write_xml(self):
        pass
