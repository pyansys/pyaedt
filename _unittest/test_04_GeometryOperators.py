import math

import clr
from pyaedt.modeler.GeometryOperators import GeometryOperators as go

clr.AddReference("System.Collections")
from pyaedt.generic.constants import AXIS, PLANE, SWEEPDRAFT, unit_converter
from System import Double
from System.Collections.Generic import List

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

tol = 1e-12


def is_vector_equal(v, r):
    t = 0
    for a, b in zip(v, r):
        d = a - b
        t += d * d
    n = math.sqrt(t)
    return n < 1e-12


class TestClass:
    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    def test_List2list(self):
        List_str = List[str]()
        List_str.Add("one")
        List_str.Add("two")
        List_str.Add("three")
        ls = go.List2list(List_str)
        assert type(ls) is list
        assert len(ls) == 3
        List_float = List[Double]()
        List_float.Add(1.0)
        List_float.Add(2.0)
        List_float.Add(3.0)
        lf = go.List2list(List_float)
        assert isinstance(ls, list)
        assert len(lf) == 3

    def test_parse_dim_arg(self):
        assert go.parse_dim_arg("2mm") == 2e-3
        assert go.parse_dim_arg("1.123mm") == 1.123e-3
        assert go.parse_dim_arg("1.5MHz") == 1.5e6
        assert go.parse_dim_arg("2mm", "mm") == 2.0
        assert go.parse_dim_arg("-3.4e-2") == -3.4e-2
        assert abs(go.parse_dim_arg("180deg") - math.pi) < tol
        assert go.parse_dim_arg("1.57rad") == 1.57

    def test_cs_plane_str(self):
        assert go.cs_plane_to_axis_str(PLANE.XY) == "Z"
        assert go.cs_plane_to_axis_str(PLANE.YZ) == "X"
        assert go.cs_plane_to_axis_str(PLANE.ZX) == "Y"
        assert go.cs_plane_to_plane_str(PLANE.XY) == "XY"
        assert go.cs_plane_to_plane_str(PLANE.YZ) == "YZ"
        assert go.cs_plane_to_plane_str(PLANE.ZX) == "ZX"

    def test_cs_axis_str(self):
        assert go.cs_axis_str(AXIS.X) == "X"
        assert go.cs_axis_str(AXIS.Y) == "Y"
        assert go.cs_axis_str(AXIS.Z) == "Z"

    def test_draft_type_str(self):
        assert go.draft_type_str(SWEEPDRAFT.Extended) == "Extended"
        assert go.draft_type_str(SWEEPDRAFT.Round) == "Round"
        assert go.draft_type_str(SWEEPDRAFT.Natural) == "Natural"
        assert go.draft_type_str(SWEEPDRAFT.Mixed) == "Natural"

    def test_get_mid_point(self):
        p1 = [0.0, 0.0, 0.0]
        p2 = [10.0, 10.0, 10.0]
        m = go.get_mid_point(p1, p2)
        assert is_vector_equal(m, [5.0, 5.0, 5.0])

    def test_get_triangle_area(self):
        p1 = [0.0, 0.0, 0.0]
        p2 = [10.0, 10.0, 10.0]
        p3 = [20.0, 20.0, 20.0]
        p4 = [-1.0, 5.0, 13.0]
        assert go.get_triangle_area(p1, p2, p3) < tol
        assert abs(go.get_triangle_area(p1, p2, p4) - 86.02325267042629) < tol

    def test_v_cross(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        v3 = [2.0, 0.0, 0.0]
        assert is_vector_equal(go.v_cross(v1, v2), [0.0, 0.0, 1.0])
        assert is_vector_equal(go.v_cross(v2, v1), [0.0, 0.0, -1.0])
        assert is_vector_equal(go.v_cross(v1, v3), [0.0, 0.0, 0.0])

    def test_v_dot(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        v3 = [2.0, 0.0, 0.0]
        v4 = [-1.0, -1.0, 0.0]
        assert go.v_dot(v1, v2) == 0.0
        assert go.v_dot(v1, v3) == 2.0
        assert go.v_dot(v1, v4) == -1.0

    def test_v_prod(self):
        v1 = [1, 2, 3]
        c = 0.5
        assert is_vector_equal(go.v_prod(c, v1), [0.5, 1, 1.5])

    def test_v_sub(self):
        v1 = [1.0, 0.0, 1.0]
        v2 = [0.0, 1.0, 1.0]
        assert is_vector_equal(go.v_sub(v1, v2), [1.0, -1.0, 0.0])
        assert is_vector_equal(go.v_sub(v2, v1), [-1.0, 1.0, 0.0])

    def test_v_sum(self):
        v1 = [1.0, 0.0, 1.0]
        v2 = [0.0, 1.0, 1.0]
        assert is_vector_equal(go.v_sum(v1, v2), [1.0, 1.0, 2.0])
        assert is_vector_equal(go.v_sum(v2, v1), [1.0, 1.0, 2.0])

    def test_v_norm(self):
        v1 = [1, 1, 1]
        v2 = [0, 0, 0]
        assert abs(go.v_norm(v1) - math.sqrt(3)) < tol
        assert abs(go.v_norm(v2) - 0) < tol

    def test_normalize_vector(self):
        v1 = [1, 1, 1]
        v2 = [0, 0.1, 0]
        s3 = 1 / math.sqrt(3)
        assert is_vector_equal(go.normalize_vector(v1), [s3, s3, s3])
        assert is_vector_equal(go.normalize_vector(v2), [0, 1, 0])

    def test_v_points(self):
        p1 = [1.0, 0.0, 1.0]
        p2 = [0.0, 1.0, 1.0]
        assert is_vector_equal(go.v_points(p1, p2), [-1.0, 1.0, 0.0])

    def test_points_distance(self):
        p1 = [1.0, 0.0, 1.0]
        p2 = [0.0, 1.0, 1.0]
        assert abs(go.points_distance(p1, p2) - math.sqrt(2)) < tol

    def test_find_point_on_plane(self):
        assert go.find_point_on_plane([[1, 0, 0]], 0) == 1

    def test_distance_vector(self):
        a = [1, 0, 0]
        b = [2, 0, 0]
        p1 = [0, 1, 0]
        p2 = [0, 0, 1]
        assert is_vector_equal(go.distance_vector(p1, a, b), [0, -1, 0])
        assert is_vector_equal(go.distance_vector(p2, a, b), [0, 0, -1])

    def test_is_between_points(self):
        a = [1, 0, 0]
        b = [3, 0, 0]
        p1 = [2, 0, 0]
        p2 = [0, 1, 0]
        assert go.is_between_points(p1, a, b) is True
        assert go.is_between_points(p2, a, b) is False
        a = [1, 1, 1]
        b = [3, 3, 3]
        p = [2, 2, 2]
        assert go.is_between_points(p, a, b) is True

    def test_is_parallel(self):
        a1 = [1, 0, 0]
        a2 = [3, 0, 0]
        b1 = [2, 1.1, 0]
        b2 = [12, 1.1, 0]
        b3 = [12, 1.01, 0]
        assert go.is_parallel(a1, a2, b1, b2) is True
        assert go.is_parallel(a1, a2, b1, b3) is False

    def test_parallel_coeff(self):
        a1 = [1, 0, 0]
        a2 = [3, 0, 0]
        b1 = [1, 1, 0]
        b2 = [3, 1, 0]
        assert abs(go.parallel_coeff(a1, a2, b1, b2) - 1) < tol

    def test_is_projection_inside(self):
        a1 = [10, 0, 2]
        a2 = [20, 0, 2]
        b1 = [1, 1, 0]
        b2 = [30, 1, 0]
        assert go.is_projection_inside(a1, a2, b1, b2) is True
        assert go.is_projection_inside(a1, a2, b1, a2) is False

    def test_arrays_positions_sum(self):
        vl1 = [[1, 0, 0], [2, 0, 0]]
        vl2 = [[1, 1, 0], [2, 1, 0]]
        d = (2 + 2 * math.sqrt(2)) / 4.0
        assert abs(go.arrays_positions_sum(vl1, vl2) - d) < tol

    def test_v_angle(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        assert abs(go.v_angle(v1, v2) - math.pi / 2) < tol

    def test_pointing_to_axis(self):
        x, y, z = go.pointing_to_axis([1, 0.1, 1], [0.5, 1, 0])
        assert is_vector_equal(x, [0.7053456158585983, 0.07053456158585983, 0.7053456158585983])
        assert is_vector_equal(y, [0.19470872568244801, 0.9374864569895649, -0.28845737138140465])
        assert is_vector_equal(z, [-0.681598176590997, 0.3407990882954985, 0.6475182677614472])

    def test_axis_to_euler_zxz(self):
        x, y, z = go.pointing_to_axis([1, 0.1, 1], [0.5, 1, 0])
        phi, theta, psi = go.axis_to_euler_zxz(x, y, z)
        assert abs(phi - (-2.0344439357957027)) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - 1.9590019609437583) < tol

    def test_axis_to_euler_zyz(self):
        x, y, z = go.pointing_to_axis([1, 0.1, 1], [0.5, 1, 0])
        phi, theta, psi = go.axis_to_euler_zyz(x, y, z)
        assert abs(phi - 2.677945044588987) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - (-2.7533870194409316)) < tol

    def test_quaternion_to_axis(self):
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        x, y, z = go.quaternion_to_axis(q)
        assert is_vector_equal(x, [0.7053456158585982, 0.07053456158585963, 0.7053456158585982])
        assert is_vector_equal(y, [0.19470872568244832, 0.937486456989565, -0.2884573713814046])
        assert is_vector_equal(z, [-0.681598176590997, 0.34079908829549865, 0.6475182677614472])

    def test_quaternion_to_axis_angle(self):
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        u, th = go.quaternion_to_axis_angle(q)
        assert is_vector_equal(u, [-0.41179835953227295, -0.9076445218972716, -0.0812621249808417])
        assert abs(th - 0.8695437956599169) < tol

    def test_axis_angle_to_quaternion(self):
        u = [-0.41179835953227295, -0.9076445218972716, -0.0812621249808417]
        th = 0.8695437956599169
        q = go.axis_angle_to_quaternion(u, th)
        assert is_vector_equal(q, [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274])
        assert abs(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2 - 1.0) < tol

    def test_quaternion_to_euler_zxz(self):
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        phi, theta, psi = go.quaternion_to_euler_zxz(q)
        assert abs(phi - (-2.0344439357957027)) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - 1.9590019609437583) < tol

    def test_euler_zxz_to_quaternion(self):
        phi = -2.0344439357957027
        theta = 0.8664730673456006
        psi = 1.9590019609437583
        q = go.euler_zxz_to_quaternion(phi, theta, psi)
        assert is_vector_equal(
            q, [0.9069661433330367, -0.17345092325178468, -0.38230307786150497, -0.03422789400943264]
        )
        assert abs(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2 - 1.0) < tol

    def test_quaternion_to_euler_zyz(self):
        q = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        phi, theta, psi = go.quaternion_to_euler_zyz(q)
        assert abs(phi - 2.677945044588987) < tol
        assert abs(theta - 0.8664730673456006) < tol
        assert abs(psi - (-2.7533870194409316)) < tol

    def test_euler_zyz_to_quaternion(self):
        phi = 2.677945044588987
        theta = 0.8664730673456006
        psi = -2.7533870194409316
        q = go.euler_zyz_to_quaternion(phi, theta, psi)
        assert is_vector_equal(q, [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274])
        assert abs(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2 - 1.0) < tol

    def test_deg2rad(self):
        assert abs(go.deg2rad(180.0) - math.pi) < tol
        assert abs(go.deg2rad(180) - math.pi) < tol

    def test_rad2deg(self):
        assert abs(go.rad2deg(math.pi) - 180.0) < tol

    def test_atan2(self):
        assert go.atan2(0.0, 0.0) == 0.0
        assert go.atan2(-0.0, 0.0) == 0.0
        assert go.atan2(0.0, -0.0) == 0.0
        assert go.atan2(-0.0, -0.0) == 0.0
        assert go.atan2(1, 2) == math.atan2(1, 2)

    def test_q_prod(self):
        q1 = [0.9069661433330367, -0.17345092325178477, -0.3823030778615049, -0.03422789400943274]
        q2 = [0.9238795325112867, 0.0, -0.3826834323650898, 0.0]
        q = go.q_prod(q1, q2)
        assert is_vector_equal(q, [0.6916264024663118, -0.1733462058496682, -0.7002829056219277, 0.03475434394060616])
        assert abs(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2 - 1.0) < tol

    def test_q_rotation(self):
        q2 = [0.9238795325112867, 0.0, -0.3826834323650898, 0.0]
        v = go.q_rotation([1, 0, 0], q2)
        assert is_vector_equal(v, [0.7071067811865475, 0.0, 0.7071067811865476])

    def test_q_rotation_inv(self):
        q2 = [0.9238795325112867, 0.0, -0.3826834323650898, 0.0]
        v = go.q_rotation_inv([1, 0, 0], q2)
        assert is_vector_equal(v, [0.7071067811865475, 0.0, -0.7071067811865476])

    def test_get_polygon_centroid(self):
        p1 = [1, 1, 1]
        p2 = [1, -1, 1]
        p3 = [-1, 1, -1]
        p4 = [-1, -1, -1]
        c = go.get_polygon_centroid([p1, p2, p3, p4])
        assert is_vector_equal(c, [0, 0, 0])

    def test_orient_polygon(self):
        x = [3, 3, 2.5, 1, 1]
        y = [1, 2, 1.5, 2, 1]
        xo, yo = go.orient_polygon(x, y, clockwise=False)
        assert x == xo
        assert y == yo
        xo, yo = go.orient_polygon(x, y, clockwise=True)
        xo.reverse()
        yo.reverse()
        assert x == xo
        assert y == yo

    def test_is_collinear(self):
        assert go.is_collinear([1, 0, 0], [1, 0, 0])
        assert go.is_collinear([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0])
        assert not go.is_collinear([1, 0, 0], [0, 1, 0])
        assert go.is_collinear([1, 1, 1], [-2, -2, -2])
        assert not go.is_collinear([1, 2, 3], [3.0, 2.0, 1.0])

    def test_unit_converter(self):
        assert unit_converter(10) == 10000
        assert unit_converter(10, "Lenghts") == 10
        assert unit_converter(10, "Lenght", "meters") == 10
