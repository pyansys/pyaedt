class Layer(object):
    def __init__(self):
        self.name = ""
        self._layer_function = Function().Conductor
        self._layer_side = LayerSide().Top
        self._layer_polarity = LayerPolarity().Positive

    @property
    def layer_function(self):
        return self._layer_function

    @layer_function.setter
    def layer_function(self, value):
        if isinstance(value, int):
            self._layer_function = value

    @property
    def layer_side(self):
        return self._layer_side

    @layer_side.setter
    def layer_side(self, value):
        if isinstance(value, int):
            self._layer_side = value

    @property
    def layer_polarity(self):
        return self._layer_polarity

    @layer_polarity.setter
    def layer_polarity(self, value):
        if isinstance(value, int):
            self._layer_polarity = value

    def write_xml(self):
        pass


class Function(object):
    (Conductor, Dielpreg, Plane, Drill) = range(1, 4)


class LayerSide(object):
    (Top, Internal, Bottom, All) = range(1, 4)


class LayerPolarity(object):
    (Positive, Negative) = range(1, 2)
