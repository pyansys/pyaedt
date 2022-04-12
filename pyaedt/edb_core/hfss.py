"""
This module contains the ``EdbHfss`` class.
"""
import math

from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.edb_core.general import convert_pytuple_to_nettuple
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SweepType
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators


class EdbHfss(object):
    """Manages EDB functionalities for 3D layouts.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edb_hfss = edb_3dedbapp.core_hfss
    """

    def __init__(self, p_edb):
        self._pedb = p_edb

    @property
    def _hfss_terminals(self):
        return self._pedb.edblib.HFSS3DLayout.HFSSTerminalMethods

    @property
    def _hfss_ic_methods(self):
        return self._pedb.edblib.HFSS3DLayout.ICMethods

    @property
    def _hfss_setup(self):
        return self._pedb.edblib.HFSS3DLayout.HFSSSetup

    @property
    def _hfss_mesh_setup(self):
        return self._pedb.edblib.HFSS3DLayout.Meshing

    @property
    def _sweep_methods(self):
        return self._pedb.edblib.SimulationSetup.SweepMethods

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.db

    @property
    def _builder(self):
        return self._pedb.builder

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    @pyaedt_function_handler()
    def get_trace_width_for_traces_with_ports(self):
        """Retrieve the trace width for traces with ports.

        Returns
        -------
        dict
            Dictionary of trace width data.
        """
        mesh = self._hfss_mesh_setup.GetMeshOperation(self._active_layout)
        if mesh.Item1:
            return convert_netdict_to_pydict(mesh.Item2)
        else:
            return {}

    @pyaedt_function_handler()
    def create_circuit_port_on_pin(self, pos_pin, neg_pin, impedance=50, port_name=None):
        """Create Circuit Port on Pin.

        Parameters
        ----------
        pos_pin : Object
            Edb Pin
        neg_pin : Object
            Edb Pin
        impedance : float
            Port Impedance
        port_name : str, optional
            Port Name

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_circuit_port_on_pin(pins[0], pins[1],50,"port_name")

        Returns
        -------
        str
            Port Name.

        """
        return self._pedb.core_siwave.create_circuit_port_on_pin(pos_pin, neg_pin, impedance, port_name)

    @pyaedt_function_handler()
    def create_voltage_source_on_pin(self, pos_pin, neg_pin, voltage_value=3.3, phase_value=0, source_name=""):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_voltage_source_on_pin(pins[0], pins[1],50,"source_name")
        """
        return self._pedb.core_siwave.create_voltage_source_on_pin(
            pos_pin, neg_pin, voltage_value, phase_value, source_name
        )

    @pyaedt_function_handler()
    def create_current_source_on_pin(self, pos_pin, neg_pin, current_value=0.1, phase_value=0, source_name=""):
        """Create a current source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_current_source_on_pin(pins[0], pins[1],50,"source_name")
        """

        return self._pedb.core_siwave.create_current_source_on_pin(
            pos_pin, neg_pin, current_value, phase_value, source_name
        )

    @pyaedt_function_handler()
    def create_resistor_on_pin(self, pos_pin, neg_pin, rvalue=1, resistor_name=""):
        """Create a voltage source.

        Parameters
        ----------
        pos_pin : Object
            Positive Pin.
        neg_pin : Object
            Negative Pin.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Name of the Resistor.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> pins =edbapp.core_components.get_pin_from_component("U2A5")
        >>> edbapp.core_hfss.create_resistor_on_pin(pins[0], pins[1],50,"res_name")
        """
        return self._pedb.core_siwave.create_resistor_on_pin(pos_pin, neg_pin, rvalue, resistor_name)

    @pyaedt_function_handler()
    def create_circuit_port_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        impedance_value=50,
        port_name="",
    ):
        """Create a circuit port on a NET.
        It groups all pins belonging to the specified net and then applies the port on PinGroups.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net name. The default is ``"GND"``.
        impedance_value : float, optional
            Port impedance value. The default is ``50``.
        port_name : str, optional
            Name of the port. The default is ``""``.

        Returns
        -------
        str
            Port Name

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_hfss.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "port_name")
        """
        return self._pedb.core_siwave.create_circuit_port_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            impedance_value,
            port_name,
        )

    @pyaedt_function_handler()
    def create_voltage_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        voltage_value=3.3,
        phase_value=0,
        source_name="",
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        voltage_value : float, optional
            Value for the voltage. The default is ``3.3``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "source_name")
        """
        return self._pedb.core_siwave.create_voltage_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            voltage_value,
            phase_value,
            source_name,
        )

    @pyaedt_function_handler()
    def create_current_source_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        current_value=0.1,
        phase_value=0,
        source_name="",
    ):
        """Create a current source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        current_value : float, optional
            Value for the current. The default is ``0.1``.
        phase_value : optional
            Value for the phase. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``""``.

        Returns
        -------
        str
            Source Name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_current_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0, "source_name")
        """
        return self._pedb.core_siwave.create_current_source_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            current_value,
            phase_value,
            source_name,
        )

    @pyaedt_function_handler()
    def create_resistor_on_net(
        self,
        positive_component_name,
        positive_net_name,
        negative_component_name=None,
        negative_net_name="GND",
        rvalue=1,
        resistor_name="",
    ):
        """Create a voltage source.

        Parameters
        ----------
        positive_component_name : str
            Name of the positive component.
        positive_net_name : str
            Name of the positive net.
        negative_component_name : str, optional
            Name of the negative component. The default is ``None``, in which case the name of
            the positive net is assigned.
        negative_net_name : str, optional
            Name of the negative net. The default is ``"GND"``.
        rvalue : float, optional
            Resistance value. The default is ``1``.
        resistor_name : str, optional
            Name of the resistor. The default is ``""``.

        Returns
        -------
        str
            Resistor Name

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edb.core_hfss.create_resistor_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 1, "resistor_name")
        """
        return self._pedb.core_siwave.create_resistor_on_net(
            positive_component_name,
            positive_net_name,
            negative_component_name,
            negative_net_name,
            rvalue,
            resistor_name,
        )

    @pyaedt_function_handler()
    def create_coax_port_on_component(self, ref_des_list, net_list):
        """Create a coaxial port on a component or component list on a net or net list.

        .. note::
           The name of the new coaxial port is automatically assigned.

        Parameters
        ----------
        ref_des_list : list, str
            List of one or more reference designators.

        net_list : list, str
            List of one or more nets.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        coax = []
        if not isinstance(ref_des_list, list):
            ref_des_list = [ref_des_list]
        if not isinstance(net_list, list):
            net_list = [net_list]
        for ref in ref_des_list:
            for pinname, pin in self._pedb.core_components.components[ref].pins.items():
                if pin.net_name in net_list and pin.pin.IsLayoutPin():
                    port_name = "{}_{}_{}".format(ref, pin.net_name, pin.pin.GetName())
                    if is_ironpython:
                        (
                            res,
                            fromLayer_pos,
                            toLayer_pos,
                        ) = pin.pin.GetLayerRange()  # pragma: no cover
                    else:
                        res, fromLayer_pos, toLayer_pos = pin.pin.GetLayerRange(None, None)
                    if self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
                        self._active_layout,
                        pin.pin.GetNet(),
                        port_name,
                        pin.pin,
                        toLayer_pos,
                    ):
                        coax.append(port_name)
        return coax

    @pyaedt_function_handler()
    def create_hfss_ports_on_padstack(self, pinpos, portname=None):
        """Create a HFSS port on a padstack.

        Parameters
        ----------
        pinpos :
            Position of the pin.

        portname : str, optional
             Name of the port. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if is_ironpython:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange()
        else:
            res, fromLayer_pos, toLayer_pos = pinpos.GetLayerRange(None, None)
        if not portname:
            portname = generate_unique_name("Port_" + pinpos.GetNet().GetName())
        edbpointTerm_pos = self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
            self._active_layout, pinpos.GetNet(), portname, pinpos, toLayer_pos
        )
        if edbpointTerm_pos:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def create_lumped_port_on_trace(
        self,
        nets=None,
        reference_layer=None,
        return_points_only=False,
        polygon_trace_threshhold=300e-6,
        digit_resolution=6,
        point_list=None,
    ):
        """Create an edge port on traces.

        Parameters
        ----------
        nets : list, optional
            List of nets, str or Edb net.

        reference_layer : str, Edb layer.
             Name or Edb layer object.

        return_points_only : bool, optional
            Use this boolean when you want to return only the points from the edges and not creating ports. Default
            value is ``False``.

        polygon_trace_threshhold : float, optional
            Used only when selected nets are routed as polygon. The value gives the algorithm the threshold
            of the polygon width at the design border for considering placing an edge port. The default value is
            ``300-e6``.

        digit_resolution : int, optional
            The number of digits carried for the edge location accuracy. The default value is ``6``.

        point_list : list(tuples), optional
            The list of points where to define ports. The port evaluation is done for each net provided and if a point
            belongs to a center line points from a path or a polygon then the port will be created. If the point is not
            found the ports  will be skipped. If point_list is None, the algorithm will try to find the edges from
            traces or polygons touching the layout bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(nets, list):
            if isinstance(nets, str):
                nets = [self._edb.Cell.Net.FindByName(self._active_layout, nets)]
            elif isinstance(nets, self._edb.Cell.Net):
                nets = [nets]
        else:
            temp_nets = []
            for nn in nets:
                if isinstance(nn, str):
                    temp_nets.append(self._edb.Cell.Net.FindByName(self._active_layout, nn))
                elif isinstance(nn, self._edb.Cell.Net):
                    temp_nets.append(nn)
            nets = temp_nets
        if point_list:
            if isinstance(point_list, tuple):
                point_list = [point_list]
        edges_pts = []
        if nets:
            if isinstance(reference_layer, str):
                try:
                    reference_layer = self._pedb.core_stackup.signal_layers[reference_layer]._layer
                except:
                    raise Exception("Failed to get the layer {}".format(reference_layer))
            if not isinstance(reference_layer, self._edb.Cell.ILayerReadOnly):
                return False
            layout = nets[0].GetLayout()
            layout_bbox = self.get_layout_bounding_box(layout, digit_resolution)
            for net in nets:
                net_primitives = list(net.Primitives)
                net_paths = [
                    pp for pp in net_primitives if pp.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Path
                ]
                net_poly = [
                    pp
                    for pp in net_primitives
                    if pp.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Polygon
                ]
                for path in net_paths:
                    trace_path_pts = list(path.GetCenterLine().Points)
                    port_name = "{}_{}".format(net.GetName(), path.GetId())
                    if point_list:
                        for _pt in point_list:
                            if isinstance(_pt, tuple):
                                found_pt = [
                                    p
                                    for p in trace_path_pts
                                    if round(p.X.ToDouble(), 6) == round(_pt[0], 6)
                                    and round(p.Y.ToDouble(), 6) == round(_pt[1], 6)
                                ]
                                if found_pt:
                                    pt = self._edb.Geometry.PointData(
                                        self._get_edb_value(_pt[0]),
                                        self._get_edb_value(_pt[1]),
                                    )
                                    if not self._hfss_terminals.CreateEdgePort(path, pt, reference_layer, port_name):
                                        raise Exception(
                                            "edge port creation failed on point {}, {}".format(
                                                str(pt.X.ToDouble()),
                                                str(pt.Y.ToDouble()),
                                            )
                                        )
                    else:
                        for pt in trace_path_pts:
                            _pt = [
                                round(pt.X.ToDouble(), digit_resolution),
                                round(pt.Y.ToDouble(), digit_resolution),
                            ]
                            if bool(set(_pt) & set(layout_bbox)):
                                if return_points_only:
                                    edges_pts.append(_pt)
                                else:
                                    if not self._hfss_terminals.CreateEdgePort(
                                        path, pt, reference_layer, port_name
                                    ):  # pragma: no cover
                                        raise Exception(
                                            "edge port creation failed on point {}, {}".format(str(pt[0]), str(_pt[1]))
                                        )
                for poly in net_poly:
                    pt_list = list(poly.GetPolygonData().Points)
                    points_at_border = [
                        pt
                        for pt in pt_list
                        if round(pt.X.ToDouble(), digit_resolution) in layout_bbox
                        or round(pt.Y.ToDouble(), digit_resolution) in layout_bbox
                    ]
                    pt_at_left = [
                        pt for pt in points_at_border if round(pt.X.ToDouble(), digit_resolution) == layout_bbox[0]
                    ]
                    pt_at_left_values = [pt.Y.ToDouble() for pt in pt_at_left]
                    if pt_at_left_values:
                        left_edge_length = abs(max(pt_at_left_values) - min(pt_at_left_values))
                        if polygon_trace_threshhold >= left_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_left)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly,
                                    convert_py_list_to_net_list(pt_at_left),
                                    reference_layer,
                                    port_name,
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_bottom = [
                        pt for pt in points_at_border if round(pt.Y.ToDouble(), digit_resolution) == layout_bbox[1]
                    ]
                    pt_at_bottom_values = [pt.X.ToDouble() for pt in pt_at_bottom]
                    if pt_at_bottom_values:
                        bot_edge_length = abs(max(pt_at_bottom_values) - min(pt_at_bottom_values))
                        if polygon_trace_threshhold >= bot_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_bottom)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly,
                                    convert_py_list_to_net_list(pt_at_bottom),
                                    reference_layer,
                                    port_name,
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_right = [
                        pt for pt in points_at_border if round(pt.X.ToDouble(), digit_resolution) == layout_bbox[2]
                    ]
                    pt_at_right_values = [pt.Y.ToDouble() for pt in pt_at_right]
                    if pt_at_right_values:
                        right_edge_length = abs(max(pt_at_right_values) - min(pt_at_right_values))
                        if polygon_trace_threshhold >= right_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt_at_right)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly,
                                    convert_py_list_to_net_list(pt_at_right),
                                    reference_layer,
                                    port_name,
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))

                    pt_at_top = [
                        pt for pt in points_at_border if round(pt.Y.ToDouble(), digit_resolution) == layout_bbox[3]
                    ]
                    pt_at_top_values = [pt.X.ToDouble() for pt in pt_at_top]
                    if pt_at_top_values:
                        top_edge_length = abs(max(pt_at_top_values) - min(pt_at_top_values))
                        if polygon_trace_threshhold >= top_edge_length > 0:
                            if return_points_only:
                                edges_pts.append(pt - pt_at_top)
                            else:
                                port_name = generate_unique_name("port")
                                if not self._hfss_terminals.CreateEdgePortOnPolygon(
                                    poly,
                                    convert_py_list_to_net_list(pt_at_top),
                                    reference_layer,
                                    port_name,
                                ):  # pragma: no cover
                                    raise Exception("Failed to create port on polygon {}".format(poly.GetName()))
            if return_points_only:
                return edges_pts
        return True

    @pyaedt_function_handler()
    def get_layout_bounding_box(self, layout=None, digit_resolution=6):
        """Evaluate the layout bounding box.

        Parameters
        ----------
        layout :
            Edb layout.

        digit_resolution : int, optional
            Digit Resolution. The default value is ``6``.
        Returns
        -------
        list
            [lower left corner X, lower left corner, upper right corner X, upper right corner Y]
        """
        if layout == None:
            return False
        layout_obj_instances = layout.GetLayoutInstance().GetAllLayoutObjInstances()
        tuple_list = []
        for lobj in layout_obj_instances.Items:
            lobj_bbox = lobj.GetLayoutInstanceContext().GetBBox(False)
            tuple_list.append(lobj_bbox)
        _bbox = self._edb.Geometry.PolygonData.GetBBoxOfBoxes(convert_py_list_to_net_list(tuple_list))
        layout_bbox = [
            round(_bbox.Item1.X.ToDouble(), digit_resolution),
            round(_bbox.Item1.Y.ToDouble(), digit_resolution),
            round(_bbox.Item2.X.ToDouble(), digit_resolution),
            round(_bbox.Item2.Y.ToDouble(), digit_resolution),
        ]
        return layout_bbox

    @pyaedt_function_handler()
    def create_circuit_ports_on_components_no_pin_group(
        self,
        signal_nets=None,
        power_nets=None,
        simulation_setup=None,
        component_list=None,
    ):
        """Create circuit ports on given components.
        For each component, create a coplanar circuit port at each signalNet pin.
        Use the closest powerNet pin as a reference, regardless of component.

        Parameters
        ----------
        signal_nets : list, optional if simulation_setup provided.
            The list of signal net names. will be ignored if simulation_setup object is provided

        power_nets : list optional if simulatiom_setup provided.
            The list of power net names. will be ignored if simulation_setup object is provided

        component_list : list optional if simulatiom_setup provided.
            The list of component names. will be ignored if simulation_setup object is provided

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if simulation_setup:
            if not isinstance(simulation_setup, SimulationConfiguration):
                self._logger.error(
                    "simulation setup was provided but must be an instance of \
                    EDB_Data.SimulationConfiguration"
                )
                return False
            signal_nets = simulation_setup.signal_nets
            power_nets = simulation_setup.power_nets
            component_list = simulation_setup.coplanar_instances
        else:
            if not component_list:
                return False

        if not simulation_setup.coplanar_instances:
            return False

        layout = self._active_layout
        l_inst = layout.GetLayoutInstance()
        edb_power_nets = list(map(lambda net: self._pedb.core_nets.find_or_create_net(net), power_nets))
        for inst in component_list:
            comp = self._edb.Cell.Hierarchy.Component.FindByName(layout, inst)
            if comp.IsNull():
                self._logger.warning("SetupCoplanarInstances: could not find {0}".format(inst))
                continue
            # Get the portLayer based on the component's pin placement
            cmp_layer = self._edb.Cell.Hierarchy.Component.GetPlacementLayer(comp)
            # Get the bbox of the comp
            bb = self._edb.Geometry.PolygonData.CreateFromBBox(l_inst.GetLayoutObjInstance(comp, None).GetBBox())
            bb_c = bb.GetBoundingCircleCenter()
            # Expand x5 to create testing polygon...
            bb.Scale(5, bb_c)
            # Find the closest pin in the Ground/Power nets...
            hit = l_inst.FindLayoutObjInstance(bb, cmp_layer, convert_py_list_to_net_list(edb_power_nets))
            all_hits = [list(hit.Item1.Items) + list(hit.Item2.Items)]
            hit_pinsts = [
                obj
                for obj in all_hits
                if obj.GetLayoutObj().GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
            ]
            if not hit_pinsts:
                self._logger.error("SetupCoplanarInstances: could not find a pin in the vicinity of {0}".format(inst))
                continue
            # Iterate each pin in the component that's on the signal nets and create a CircuitPort
            pin_list = [
                obj
                for obj in list(comp.LayoutObjs)
                if obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
                and obj.GetNet().GetName() in signal_nets
            ]
            for ii, pin in enumerate(pin_list):
                pin_c = l_inst.GetLayoutObjInstance(pin, None).GetCenter()
                ref_pinst = None
                ref_pt = None
                ref_dist = None
                for hhLoi in hit_pinsts:
                    this_c = hhLoi.GetCenter()
                    this_dist = this_c.Distance(pin_c)
                    if ref_pt is None or this_dist < ref_dist:
                        ref_pinst = hhLoi.GetLayoutObj()
                        ref_pt = this_c
                        ref_dist = this_dist

                port_nm = "PORT_{0}_{1}@{2}".format(comp.GetName(), ii, pin.GetNet().GetName())
                ## TO complete and check for embefing in create_port_on_component
                ###########################
                ###########################
                self._edbutils.HfssUtilities.CreateCircuitPortFromPoints(
                    port_nm,
                    layout,
                    pin_c,
                    cmp_layer,
                    pin.GetNet(),
                    ref_pt,
                    cmp_layer,
                    ref_pinst.GetNet(),
                )
        return True

    @pyaedt_function_handler()
    def configure_hfss_extents(self, simulation_setup=None):
        """Configure HFSS extent box.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error("Configure HFSS extent requires EDB_Data.SimulationConfiguration object")
            return False
        hfss_extent = self._edb.Utility.HFSSExtentInfo()
        if simulation_setup.radiation_box == RadiationBoxType.BoundingBox:
            hfss_extent.ExtentType = self._edb.Utility.HFSSExtentInfoType.BoundingBox
        elif simulation_setup.radiation_box == RadiationBoxType.Conformal:
            hfss_extent.ExtentType = self._edb.Utility.HFSSExtentInfoType.Conforming
        else:
            hfss_extent.ExtentType = self._edb.Utility.HFSSExtentInfoType.ConvexHull
        hfss_extent.DielectricExtentSize = convert_pytuple_to_nettuple((simulation_setup.dielectric_extent, True))
        hfss_extent.AirBoxHorizontalExtent = convert_pytuple_to_nettuple(
            (simulation_setup.airbox_horizontal_extent, True)
        )
        hfss_extent.AirBoxNegativeVerticalExtent = convert_pytuple_to_nettuple(
            (simulation_setup.airbox_negative_vertical_extent, True)
        )
        hfss_extent.AirBoxPositiveVerticalExtent = convert_pytuple_to_nettuple(
            (simulation_setup.airbox_positive_vertical_extent, True)
        )
        hfss_extent.HonorUserDielectric = simulation_setup.honor_user_dielectric
        hfss_extent.TruncateAirBoxAtGround = simulation_setup.truncate_airbox_at_ground
        hfss_extent.UseOpenRegion = simulation_setup.use_radiation_boundary
        return self._active_layout.GetCell().SetHFSSExtentInfo(hfss_extent)

    @pyaedt_function_handler()
    def configure_hfss_analysis_setup(self, simulation_setup=None):
        """
        Configure HFSS analysis setup.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Configure HFSS analysis requires and EDB_Data.SimulationConfiguration object as \
                               argument"
            )
            return False
        adapt = self._pedb.simsetupdata.AdaptiveFrequencyData()
        adapt.AdaptiveFrequency = simulation_setup.mesh_freq
        adapt.MaxPasses = int(simulation_setup.max_num_passes)
        adapt.MaxDelta = str(simulation_setup.max_mag_delta_s)
        simsetup_info = self._pedb.simsetupdata.SimSetupInfo[self._pedb.simsetupdata.HFSSSimulationSettings]()
        simsetup_info.Name = simulation_setup.setup_name

        simsetup_info.SimulationSettings.CurveApproxSettings.ArcAngle = simulation_setup.arc_angle
        simsetup_info.SimulationSettings.CurveApproxSettings.UseArcToChordError = (
            simulation_setup.use_arc_to_chord_error
        )
        simsetup_info.SimulationSettings.CurveApproxSettings.ArcToChordError = simulation_setup.arc_to_chord_error
        if is_ironpython:
            simsetup_info.SimulationSettings.AdaptiveSettings.AdaptiveFrequencyDataList.Clear()
            simsetup_info.SimulationSettings.AdaptiveSettings.AdaptiveFrequencyDataList.Add(adapt)
        else:
            list(simsetup_info.SimulationSettings.AdaptiveSettings.AdaptiveFrequencyDataList).clear()
            list(simsetup_info.SimulationSettings.AdaptiveSettings.AdaptiveFrequencyDataList).append(adapt)
        simsetup_info.SimulationSettings.InitialMeshSettings.LambdaRefine = simulation_setup.do_lambda_refinement
        simsetup_info.SimulationSettings.InitialMeshSettings.UseDefaultLambda = True
        simsetup_info.SimulationSettings.AdaptiveSettings.MaxRefinePerPass = 30
        simsetup_info.SimulationSettings.AdaptiveSettings.MinPasses = simulation_setup.min_num_passes  # 1
        simsetup_info.SimulationSettings.AdaptiveSettings.MinConvergedPasses = 1
        simsetup_info.SimulationSettings.HFSSSolverSettings.OrderBasis = (
            simulation_setup.basis_order
        )  # -1  # e.g. mixed
        simsetup_info.SimulationSettings.HFSSSolverSettings.UseHFSSIterativeSolver = False
        simsetup_info.SimulationSettings.DefeatureSettings.UseDefeature = False  # set True when using defeature ratio
        simsetup_info.SimulationSettings.DefeatureSettings.UseDefeatureAbsLength = (
            simulation_setup.defeature_layout
        )  # True
        simsetup_info.SimulationSettings.DefeatureSettings.DefeatureAbsLength = simulation_setup.defeature_abs_length

        try:
            sweep = self._pedb.simsetupdata.SweepData(simulation_setup.sweep_name)
            sweep.IsDiscrete = False
            sweep.UseQ3DForDC = simulation_setup.use_q3d_for_dc
            sweep.RelativeSError = simulation_setup.relative_error
            sweep.InterpUsePortImpedance = False
            sweep.EnforceCausality = simulation_setup.start_frequency
            # sweep.EnforceCausality = False
            sweep.EnforcePassivity = simulation_setup.enforce_passivity
            sweep.PassivityTolerance = simulation_setup.passivity_tolerance
            if is_ironpython:
                sweep.Frequencies.Clear()
            else:
                list(sweep.Frequencies).clear()
            if simulation_setup.sweep_type == SweepType.LogCount:  # setup_info.SweepType == 'DecadeCount'
                self._setup_decade_count_sweep(
                    sweep,
                    simulation_setup.start_frequency,
                    simulation_setup.stop_freq,
                    simulation_setup.decade_count,
                )  # Added DecadeCount as a new attribute

            else:
                if is_ironpython:
                    sweep.Frequencies = self._pedb.simsetupdata.SweepData.SetFrequencies(
                        simulation_setup.start_frequency,
                        simulation_setup.stop_freq,
                        simulation_setup.step_freq,
                    )
                else:
                    sweep.Frequencies = convert_py_list_to_net_list(
                        self._pedb.simsetupdata.SweepData.SetFrequencies(
                            simulation_setup.start_frequency,
                            simulation_setup.stop_freq,
                            simulation_setup.step_freq,
                        )
                    )
            if is_ironpython:
                simsetup_info.SweepDataList.Add(sweep)
            else:
                simsetup_info.SweepDataList = convert_py_list_to_net_list([sweep])
        except Exception as err:
            self._logger.error("Exception in Sweep configuration: {0}".format(err))

        sim_setup = self._edb.Utility.HFSSSimulationSetup(simsetup_info)

        return self._active_layout.GetCell().AddSimulationSetup(sim_setup)

    def _setup_decade_count_sweep(self, sweep, start_freq="1", stop_freq="1MHz", decade_count="10"):
        start_f = GeometryOperators.parse_dim_arg(start_freq)
        if start_f == 0.0:
            start_f = 10
            self._logger.warning("Decade Count sweep does not support DC value, defaulting starting frequency to 10Hz")

        stop_f = GeometryOperators.parse_dim_arg(stop_freq)
        decade_cnt = GeometryOperators.parse_dim_arg(decade_count)
        freq = start_f
        sweep.Frequencies.Add(str(freq))

        while freq < stop_f:
            freq = freq * math.pow(10, 1.0 / decade_cnt)
            sweep.Frequencies.Add(str(freq))

    @pyaedt_function_handler()
    def trim_component_reference_size(self, simulation_setup=None, trim_to_terminals=False):
        """Trim the common component reference to the minimally acceptable size.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object

        trim_to_terminals :
            bool.
                True, reduce the reference to a box covering only the active terminals (i.e. those with
        ports).
                False, reduce the reference to the minimal size needed to cover all pins

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Trim component reference size requires an EDB_Data.SimulationConfiguration object \
                               as argument"
            )
            return False

        if not simulation_setup.coax_instances:
            return

        layout = self._cell.GetLayout()
        l_inst = layout.GetLayoutInstance()

        for inst in simulation_setup.coax_instances:
            comp = self._edb.Cell.Hierarchy.Component.FindByName(layout, inst)
            if comp.IsNull():
                continue

            terms_bbox_pts = self._get_terminals_bbox(comp, l_inst, trim_to_terminals)
            if not terms_bbox_pts:
                continue

            terms_bbox = self._edb.Geometry.PolygonData.CreateFromBBox(terms_bbox_pts)

            if trim_to_terminals:
                # Remove any pins that aren't interior to the Terminals bbox
                pin_list = [
                    obj
                    for obj in list(comp.LayoutObjs)
                    if obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
                ]
                for pin in pin_list:
                    loi = l_inst.GetLayoutObjInstance(pin, None)
                    bb_c = loi.GetCenter()
                    if not terms_bbox.PointInPolygon(bb_c):
                        comp.RemoveMember(pin)

            # Set the port property reference size
            cmp_prop = comp.GetComponentProperty().Clone()
            port_prop = cmp_prop.GetPortProperty().Clone()
            port_prop.SetReferenceSizeAuto(False)
            port_prop.SetReferenceSize(
                terms_bbox_pts.Item2.X.ToDouble() - terms_bbox_pts.Item1.X.ToDouble(),
                terms_bbox_pts.Item2.Y.ToDouble() - terms_bbox_pts.Item1.Y.ToDouble(),
            )
            cmp_prop.SetPortProperty(port_prop)
            comp.SetComponentProperty(cmp_prop)
            return True

    @pyaedt_function_handler()
    def set_coax_port_attributes(self, simulation_setup=None):
        """Set coaxial port attribute with forcing default impedance to 50 Ohms and adjusting the coaxial extent radius.

        Parameters
        ----------
        simulation_setup :
            Edb_DATA.SimulationConfiguration object.

        Returns
        -------
        bool
            True when succeeded, False when failed.
        """

        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error(
                "Set coax port attribute requires an EDB_Data.SimulationConfiguration object \
            as argument."
            )
            return False
        net_names = [net.GetName() for net in list(self._active_layout.Nets) if not net.IsPowerGround()]
        cmp_names = (
            simulation_setup.components
            if simulation_setup.components
            else [gg.GetName() for gg in self._active_layout.Groups]
        )
        ii = 0
        for cc in cmp_names:
            cmp = self._edb.Cell.Hierarchy.Component.FindByName(self._active_layout, cc)
            if cmp.IsNull():
                self._logger.warning("RenamePorts: could not find component {0}".format(cc))
                continue
            terms = [obj for obj in list(cmp.LayoutObjs) if obj.GetObjType() == self._edb.Cell.LayoutObjType.Terminal]
            for nn in net_names:
                for tt in [term for term in terms if term.GetNet().GetName() == nn]:
                    if not tt.SetImpedance(self._pedb.edb_value("50ohm")):
                        self._logger.warning("Could not set terminal {0} impedance as 50ohm".format(tt.GetName()))
                        continue
                    ii += 1

            if not simulation_setup.use_default_coax_port_radial_extension:
                radial_factor_multiplier = 0.125
                # Set the Radial Extent Factor
                typ = cmp.GetComponentType()
                if typ in [
                    self._edb.Definition.ComponentType.Other,
                    self._edb.Definition.ComponentType.IC,
                    self._edb.Definition.ComponentType.IO,
                ]:
                    cmp_prop = cmp.GetComponentProperty().Clone()
                    (
                        success,
                        diam1,
                        diam2,
                    ) = cmp_prop.GetSolderBallProperty().GetDiameter()
                    if success and diam1 > 0:
                        radial_factor = "{0}meter".format(radial_factor_multiplier * diam1)
                        for tt in terms:
                            self._builder.SetHfssSolverOption(tt, "Radial Extent Factor", radial_factor)
                            self._builder.SetHfssSolverOption(tt, "Layer Alignment", "Upper")  # ensure this is also set
        return True

    @pyaedt_function_handler()
    def _get_terminals_bbox(self, comp, l_inst, terminals_only):
        terms_loi = []
        if terminals_only:
            term_list = [
                obj for obj in list(comp.LayoutObjs) if obj.GetObjType() == self._edb.Cell.LayoutObjType.Terminal
            ]
            for tt in term_list:
                success, p_inst, lyr = tt.GetParameters()
                if success:
                    loi = l_inst.GetLayoutObjInstance(p_inst, None)
                    terms_loi.append(loi)
        else:
            pin_list = [
                obj
                for obj in list(comp.LayoutObjs)
                if obj.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance
            ]
            for pi in pin_list:
                loi = l_inst.GetLayoutObjInstance(pi, None)
                terms_loi.append(loi)

        if len(terms_loi) == 0:
            return None

        terms_bbox = []
        for loi in terms_loi:
            # Need to account for the coax port dimension
            bb = loi.GetBBox()
            ll = [bb.Item1.X.ToDouble(), bb.Item1.Y.ToDouble()]
            ur = [bb.Item2.X.ToDouble(), bb.Item2.Y.ToDouble()]
            # dim = 0.26 * max(abs(UR[0]-LL[0]), abs(UR[1]-LL[1]))  # 0.25 corresponds to the default 0.5
            # Radial Extent Factor, so set slightly larger to avoid validation errors
            dim = 0.30 * max(abs(ur[0] - ll[0]), abs(ur[1] - ll[1]))  # 0.25 corresponds to the default 0.5
            terms_bbox.append(self._edb.Geometry.PolygonData(ll[0] - dim, ll[1] - dim, ur[0] + dim, ur[1] + dim))
        return self._edb.Geometry.PolygonData.GetBBoxOfPolygons(convert_py_list_to_net_list(terms_bbox))

    @pyaedt_function_handler()
    def get_ports_number(self):
        """Return the total number of excitation ports in a layout.

        Parameters
        ----------
        None

        Returns
        -------
        int
           Number of ports.

        """
        port_list = []
        for term in self._active_layout.Terminals:
            if str(term.GetBoundaryType()) == "PortBoundary":
                if "ref" not in term.GetName():
                    port_list.append(term)
        return len(port_list)

    @pyaedt_function_handler()
    def layout_defeaturing(self, simulation_setup=None):
        """Defeature the layout by reducing the number of points for polygons based on surface deviation criteria.

        Parameters
        ----------
        simulation_setup : Edb_DATA.SimulationConfiguration object

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            self._logger.error("Layout defeaturing requires an EDB_Data.SimulationConfiguration object as argument.")
            return False
        self._logger.info("Starting Layout Defeaturing")
        polygon_list = self._pedb.core_primitives.polygons
        # polygon_with_voids = self._pedb.core_layout.get_poly_with_voids(polygon_list)
        self._logger.info("Number of polygons with voids found: {0}".format(str(polygon_with_voids.Count)))
        for _poly in polygon_list:
            voids_from_current_poly = _poly.Voids
            new_poly_data = self._pedb.core_layout.defeature_polygon(setup_info=simulation_setup, poly=_poly)
            _poly.SetPolygonData(new_poly_data)
            if len(voids_from_current_poly) > 0:
                for void in voids_from_current_poly:
                    void_data = void.GetPolygonData()
                    if void_data.Area() < float(simulation_setup.minimum_void_surface):
                        void.Delete()
                        self._logger.warning(
                            "Defeaturing Polygon {0}: Deleting Void {1} area is lower than the minimum criteria".format(
                                str(_poly.GetId()), str(void.GetId())
                            )
                        )
                    else:
                        self._logger.info(
                            "Defeaturing polygon {0}: void {1}".format(str(_poly.GetId()), str(void.GetId()))
                        )
                        new_void_data = self._pedb.core_layout.defeature_polygon(
                            setup_info=simulation_setup, poly=void_data
                        )
                        void.SetPolygonData(new_void_data)

        return True
