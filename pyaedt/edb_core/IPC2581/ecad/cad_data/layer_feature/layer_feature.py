from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.path import P


class LayerFeature(object):
    def __init__(self):
        self.name = ""
        self.color = ""
        self.features = []


class Feature(object):
    def __init__(self):
        self.feature_type = self.FeatureType().Polygon
        self.net = ""
        self.x = 0.0
        self.y = 0.0
        self.polygon = Polygon()
        self.cutouts = []


    class FeatureType:
        (Polygon, Paths, Padstack, Via, Drill) = range(1, 5)
