# Setup paths for module imports
from _unittest.conftest import BasisTest

# Import required modules


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, "Test_20")
        self.st = self.aedtapp.add_stackup_3d()

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_stackup(self):
        self.st.dielectic_x_postion = "10mm"
        gnd = self.st.add_ground_layer("gnd1")
        self.st.add_dielectric_layer("diel1", thickness=1)
        lay1 = self.st.add_signal_layer("lay1", thickness=0.07)
        self.st.add_dielectric_layer("diel2", thickness=1.2)
        top = self.st.add_signal_layer("top")
        self.st.add_dielectric_layer("diel3", thickness=1.2)
        p1 = self.st.add_signal_layer("p1", thickness=0)
        gnd2 = self.st.add_ground_layer("gnd2", thickness=0)
        assert gnd
        assert lay1
        assert top
        assert p1
        assert gnd2
        assert len(self.st.dielectrics) == 3
        assert len(self.st.grounds) == 2
        assert len(self.st.signals) == 3
        assert self.st.start_position.value == 0.0

    def test_02_line(self):
        top = self.st.stackup_layers["top"]
        line1 = top.line(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
        assert line1
        line2 = top.line(
            line_length=90,
            is_electrical_length=True,
            line_width=50,
            is_impedance=True,
            line_position_x=20,
            line_position_y=20,
            frequency=1e9,
        )
        assert line1.create_lumped_port("gnd1", change_side=True)
        assert line2
        assert line2._added_length_calcul
        assert line2.frequency.numeric_value == 1e9
        assert line2.substrate_thickness.numeric_value == 1.2
        assert line1.width.numeric_value == 3.0
        assert line2.permittivity.numeric_value == 4.4
        assert line2._permittivity_calcul

    def test_03_padstackline(self):

        p1 = self.st.add_padstack("Massimo", material="aluminum")
        p1.plating_ratio = 0.7
        p1.set_start_layer("lay1")
        p1.set_stop_layer("top")
        p1.set_all_pad_value(1)
        p1.set_all_antipad_value(3)
        p1.num_sides = 8
        assert p1.num_sides == 8
        via = p1.insert(50, 50)
        assert via
        assert len(self.st.padstacks) == 1

    def test_04_patch(self):
        top = self.st.stackup_layers["top"]
        line1 = self.st.objects_by_layer["top"][0]
        top.patch(
            1e9,
            patch_width=22,
            patch_length=10,
            patch_position_x=line1.position_x.numeric_value + line1.length.numeric_value,
            patch_position_y=line1.position_y.numeric_value,
        )

    def test_05_polygon(self):
        lay1 = self.st.stackup_layers["top"]
        gnd = self.st.stackup_layers["gnd2"]

        poly = lay1.polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])
        poly2 = lay1.polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
        assert poly
        assert poly2
        poly3 = gnd.polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])

        poly4 = gnd.polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
        assert poly3
        assert poly4

    def test_05_resize(self):
        assert self.st.resize(20)
        assert self.st.dielectric_x_position
        self.st.dielectric_x_position = "10mm"
        assert self.st.dielectric_x_position.string_value == "10.0mm"
        assert self.st.dielectric_x_position.value == 0.01
        assert self.st.dielectric_x_position.numeric_value == 10.0
        assert self.st.dielectric_y_position
        assert self.st.dielectric_x_position.hide_variable()
        assert self.st.dielectric_x_position.read_only_variable()
        assert self.st.dielectric_x_position.hide_variable(False)
        assert self.st.dielectric_x_position.read_only_variable(False)
        self.st.dielectric_y_position = "10mm"
        assert self.st.dielectric_y_position.string_value == "10.0mm"
