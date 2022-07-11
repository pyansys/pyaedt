class PhyNet(object):
    def __init__(self):
        self._name = ""
        self._phy_net_points = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value

    @property
    def phy_net_points(self):
        return self._phy_net_points

    @phy_net_points.setter
    def phy_net_points(self, value):
        if isinstance(value, list):
            if len([net for net in value if isinstance(net, PhyNetPoint)]) == len(value):
                self._phy_net_points = value

    def add_phy_net_point(self, point=None):
        if isinstance(point, PhyNetPoint):
            self._phy_net_points.append(point)

    def write_xml(self):
        pass


class PhyNetPoint(object):
    def __init__(self):
        self._x = 0.0
        self._y = 0.0
        self._layer_ref = ""
        self._net_node_type = NetNodeType().Middle
        self._exposure = ExposureType().Exposed
        self._via = False
        self._standard_primitive_id = ""

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if isinstance(value, float):
            self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if isinstance(value, float):
            self._y = value

    @property
    def layer_ref(self):
        return self._layer_ref

    @layer_ref.setter
    def layer_ref(self, value):
        if isinstance(value, str):
            self._layer_ref = value

    @property
    def net_node_type(self):
        return self._net_node_type

    @net_node_type.setter
    def net_node_type(self, value):
        if isinstance(value, int):
            self._net_node_type = value

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        if isinstance(value, int):
            self._exposure = value

    @property
    def via(self):
        return self._via

    @via.setter
    def via(self, value):
        if isinstance(value, bool):
            self._via = value

    @property
    def standard_primitive_id(self):
        return self._standard_primitive_id

    @standard_primitive_id.setter
    def standard_primitive_id(self, value):
        if isinstance(value, str):
            self._standard_primitive_id = value

    def write_xml(self):
        pass


class NetNodeType(object):
    (Middle, End) = range(1, 2)


class ExposureType(object):
    (CoveredPrimary, CoveredSecondary, Exposed) = range(1, 3)
