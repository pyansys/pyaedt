from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.polygon import Polygon
from pyaedt.edb_core.IPC2581.ecad.cad_data.primitives.path import Path
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_def import PadstackDef
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.padstack_instance import PadstackInstance
from pyaedt.edb_core.IPC2581.ecad.cad_data.padstack_def.drill import Drill


class LayerFeature(object):
    def __init__(self):
        self.name = ""
        self.color = ""
        self._features = []

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        if isinstance(value, list):
            if len([feat for feat in value if isinstance(feat, Feature)]) == len(value):
                self._features = value

    def add_feature(self, feature=None):
        if isinstance(feature, Feature):
            self._features.append(feature)
            return True
        return False

    def write_xml(self):
        pass

class Feature(object):
    def __init__(self):
        self.feature_type = self.FeatureType().Polygon
        self.net = ""
        self.x = 0.0
        self.y = 0.0
        self.polygon = Polygon()
        self._cutouts = []
        self.path = Path()
        self.pad = PadstackDef()
        self.padstack_instance = PadstackInstance()
        self.drill = Drill()

    @property
    def cutouts(self):
        return self._cutouts

    @cutouts.setter
    def cutouts(self, value):
        if isinstance(value, list):
            if len([poly for poly in value if isinstance(poly, Polygon)]) == len(value):
                self._cutouts = value

    def add_cutout(self, cutout=None):
        if isinstance(cutout, Polygon):
            self._cutouts.append(cutout)

    class FeatureType:
        (Polygon, Paths, Padstack, Via, Drill) = range(1, 5)
