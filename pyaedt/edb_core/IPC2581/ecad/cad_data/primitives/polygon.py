import math


class Polygon(object):
    def __init__(self):
        self.is_void = False
        self.poly_steps = []
        self.solid_fill_id = ""

    def add_poly_step(self, poly_step=None):
        if not isinstance(poly_step, PolyStep):
            return False
        self.poly_steps.append(poly_step)


class PathStep(object):
    def __init__(self):
        self.x = 0.0
        self.y = 0.0


class Cutout(Polygon):
    def __init__(self):
        Polygon.__init__(self)


class PolyStep(object):
    def __init__(self):
        self.poly_type = PolyType().Segment
        self.x = 0.0
        self.y = 0.0
        self.center_X = 0.0
        self.center_y = 0.0
        self.clock_wise = False


class PolyType(object):
    (Segment, Curve) = range(1, 2)


class Curve(object):
    def __init__(self):
        self.center_X = 0.0
        self.center_y = 0.0
        self.clock_wise = False


class Arc(object):

    @staticmethod
    def get_arc_radius_angle(h, c):
        if not isinstance(h, float) and isinstance(c, float):
            return False
        r = h / 2 + math.pow(c, 2) / (8 * h)
        theta = 2 * math.asin(c / (2 * r))
        return r, theta
