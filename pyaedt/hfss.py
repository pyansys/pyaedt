"""
Hfss Class
----------------------------------------------------------------

This class contains all HFSS functionalities. It inherits all objects that belong to HFSS.


Examples
----------------------------------------------------------------

>>> hfss = Hfss()     Create an ``Hfss`` object and connect to an existing HFSS design or create a new HFSS design if one does not exist.


>>> hfss = Hfss(projectname)     Create an ``Hfss`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.


>>> hfss = Hfss(projectname,designame)     Create an ``Hfss`` object and link to a design named ``designname`` in a project named ``projectname``.


>>> hfss = Hfss("myfile.aedt")     Create an ``Hfss`` object and open the specified project.


========================================================

"""
from __future__ import absolute_import
import os
from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .modeler.GeometryOperators import GeometryOperators
from .modules.Boundary import BoundaryObject
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from collections import OrderedDict
from .application.DataHandlers import random_string


class Hfss(FieldAnalysis3D, object):
    """HFSS object"""
    def __repr__(self):
        try:
            return "HFSS {} {}. ProjectName:{} DesignName:{} ".format(self._aedt_version, self.solution_type, self.project_name, self.design_name)
        except:
            return "HFSS Module"

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        """HFSS Object

            Parameters
            ----------
            projectname :
                Name of the project to select or the full path to the project or AEDTZ archive to open. If ``None``, try to get an active project and, if none are present, create an empty project.
            designname :
                Name of the design to select. If ``None``, try to get an active design and, if none are present, create an empty design.
            solution_type :
                Solution type to apply to design. If ``None`, the default type is applied.
            setup_name :
                ``setup_name`` to use as the nominal. If ``None``, the active setup is used or nothing is used.

            Returns
            -------

        """
        FieldAnalysis3D.__init__(self, "HFSS", projectname, designname, solution_type, setup_name)
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to the parent object ``Design``. """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    class BoundaryType(object):
        """ """
        (PerfectE, PerfectH, Aperture, Radiation, Impedance, LayeredImp, LumpedRLC, FiniteCond) = range(0, 8)

    @aedt_exception_handler
    def _create_lumped_driven(self, objectname, int_line_start, int_line_stop, impedance, portname,renorm, deemb):
        start = [str(i)+self.modeler.primitives.model_units for i in int_line_start]
        stop = [str(i)+self.modeler.primitives.model_units for i in int_line_stop]
        props = OrderedDict({"Objects": [objectname], "DoDeembed": deemb, "RenormalizeAllTerminals": renorm,
                             "Modes": OrderedDict({"Mode1": OrderedDict({"ModeNum": 1, "UseIntLine": True,
                                                                         "IntLine": OrderedDict(
                                                                             {"Start": start, "End": stop}),
                                                                         "AlignmentGroup": 0, "CharImp": "Zpi",
                                                                         "RenormImp": str(impedance) + "ohm"})}),
                             "ShowReporterFilter": False,
                             "ReporterFilter": [True],
                             "Impedance"	:  str(impedance)+"ohm"})
        bound = BoundaryObject(self, portname,props, "LumpedPort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _create_port_terminal(self, objectname, int_line_stop, portname, iswaveport=False):
        ref_conductors=self.modeler.convert_to_selections(int_line_stop,False)
        props = OrderedDict({})
        props["Faces"]=int(objectname)
        props["IsWavePort"]=iswaveport
        props["ReferenceConductors"]=ref_conductors
        props["RenormalizeModes"]=True
        bound = BoundaryObject(self, portname, props, "AutoIdentify")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return True

    @aedt_exception_handler
    def _create_circuit_port(self, edgelist, impedance, name, renorm, deemb, renorm_impedance=""):
        edgelist = self.modeler._convert_list_to_ids(edgelist,False)
        props = OrderedDict({"Edges": edgelist, "Impedance": str(impedance) + "ohm", "DoDeembed": deemb,
                             "RenormalizeAllTerminals": renorm})

        if self.solution_type == "DrivenModal":

            if renorm:
                if type(renorm_impedance) is int or type(renorm_impedance) is float or 'i' not in renorm_impedance:
                    renorm_imp = str(renorm_impedance) + 'ohm'
                else:
                    renorm_imp = '(' + renorm_impedance + ') ohm'
            else:
                renorm_imp = '0ohm'
            props["RenormImp"] = renorm_imp
        else:
            props["TerminalIDList"] = []
        bound = BoundaryObject(self,name,props, "CircuitPort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _create_waveport_driven(self, objectname, int_line_start=None, int_line_stop=None, impedance=50, portname="",
                                renorm=True, nummodes=1, deemb_distance=0):
        start = None
        stop = None
        if int_line_start and int_line_stop:
            start = [str(i)+self.modeler.primitives.model_units for i in int_line_start]
            stop = [str(i)+self.modeler.primitives.model_units for i in int_line_stop]
            useintline = True
        else:
            useintline=False

        props = OrderedDict({})
        props["Objects"] = [objectname]
        props["NumModes"] = nummodes
        props["UseLineModeAlignment"] = False

        if deemb_distance!=0:
            props["DoDeembed"] = True
            props["DeembedDist"] = str(deemb_distance)+self.modeler.model_units

        else:
            props["DoDeembed"] = False
        props["RenormalizeAllTerminals"] = renorm
        modes = OrderedDict({})
        arg2 = []
        arg2.append("NAME:Modes")
        i=1
        report_filter=[]
        while i<=nummodes:
            if i == 1:
                mode = OrderedDict({})
                mode["ModeNum"] = i
                mode["UseIntLine"] = useintline
                if useintline:
                    mode["IntLine"] = OrderedDict({"Start": start, "End": stop})
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance)+"ohm"
                modes["Mode1"] = mode
            else:
                mode = OrderedDict({})

                mode["ModeNum"] = i
                mode["UseIntLine"] = False
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance)+"ohm"
                modes["Mode"+str(i)] = mode
            report_filter.append(True)
            i += 1
        props["Modes"] = modes
        props["ShowReporterFilter"] = False
        props["ReporterFilter"] = report_filter
        props["UseAnalyticAlignment"] = False
        bound = BoundaryObject(self, portname, props, "WavePort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assigncoating(self, obj, mat=None,
                      cond=58000000, perm=1, usethickness=False, thickness="0.1mm", roughness="0um",
                      isinfgnd=False, istwoside=False, isInternal=True, issheelElement=False, usehuray=False,
                      radius="0.5um", ratio="2.9"):
        """This function assigns finite conductivity to object ``obj`` with material mat.

        Parameters
        ----------
        obj : list or str
            Object list.
        mat : str
            Optional. Material name to use. The default is ``None``.
        cond : float
            If no material is provided, a conductivity value must be supplied. The default is ``58000000``.
        perm : float
            If no material is provided, a permittivity value must be supplied. The default is ``1``.
        usethickness : bool
            Boolean. The default is ``False``.
        thickness : str
            Thickness value to use if ``usethickness=True``. The default is ``0.1mm``.
        roughness : str
            Optional. Roughness value. The default is ``0um``.
        isinfgnd : bool
            Boolean. The default is ``False``.
        istwoside : bool
            Boolean. The default is ``False``.
        isInternal : bool
            Boolean. The default is ``True``.
        issheelElement : bool
            Boolean. The default is ``False``.
        usehuray : bool
            Boolean. The default is ``False``. 
        radius : str
            Huray coefficient. The default is ``0.5um``.
        ratio : str
            Huray coefficient. The default is ``2.9``.

        Returns
        -------
        :class: BoundaryObject
            Boundary object

        Examples
        --------
        >>> id1 = aedtapp.modeler.primitives.get_obj_id("inner")
        >>> coat = aedtapp.assigncoating([id1], "copper",usethickness=True, thickness="0.2mm")
        """

        mat = mat.lower()
        listobj = self.modeler.convert_to_selections(obj, True)
        listobjname = "_".join(listobj)
        props = {"Objects" : listobj}
        if mat:
            if mat in self.materials.material_keys:
                Mat = self.materials.material_keys[mat]
                Mat.update()
                props['UseMaterial'] = True
                props['Material'] = mat
                self.materials._aedmattolibrary(mat)
            elif self.materials.checkifmaterialexists(mat):
                props['UseMaterial'] = True
                props['Material'] = mat
            else:
                return False
        else:
            props['UseMaterial'] = False
            props['Conductivity'] = str(cond)
            props['Permeability'] = str(str(perm))
        props['UseThickness'] = usethickness
        if usethickness:
            props['Thickness'] = thickness
        if usehuray:
            props['Radius'] = str(radius)
            props['Ratio'] = str(ratio)
            props['InfGroundPlane'] = False
        else:
            props['Roughness'] = roughness
            props['InfGroundPlane'] = isinfgnd
        props['IsTwoSided'] = istwoside

        if istwoside:
            props['IsShellElement'] = issheelElement
        else:
            props['IsInternal'] = isInternal
        bound = BoundaryObject(self, "Coating_" + listobjname[:32], props, "FiniteCond")
        if bound.create():
            self._messenger.add_debug_message('Assigned Coating ' + mat + ' to object ' + listobjname)
            self.boundaries.append(bound)
            return bound
        return True

    @aedt_exception_handler
    def create_frequency_sweep(self, setupname, unit="GHz", freqstart=1e-3, freqstop=10, sweepname=None,
                               num_of_freq_points=451, sweeptype="Interpolating",
                               interpolation_tol=0.5, interpolation_max_solutions=250):
        """Create a frequency sweep.

        Parameters
        ----------
        setupname : str
            Name of the setup which is attached the sweep.
        unit :
            Units ("MHz", "GHz"...). The default is ``GHz``.
        freqstart :
            Starting frequency of the sweep. The default is ``1e-3``.
        freqstop :
            Stopping frequency of the sweep. The default is ``10``.
        sweepname :
            Name of the sweep. The default value is ``None``.
        num_of_freq_points :
            Number of frequency points in the range. The default value is ``451``.
        sweeptype :
            The type of sweep. Choices are ``Fast``, ``"Interpolating``, and ``Discrete``. The default is ``Discrete.``
        interpolation_max_solutions :
            Maximum number of solutions evaluated for the interpolation process. The default is ``250``.
        interpolation_tol :
            Error tolerance threshold for the interpolation process. The default is ``0.5``.

        Returns
        -------
        type
            ``True`` if the operation succeeds.

        """

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} is already present. Rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, sweeptype)
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeCount"] = num_of_freq_points
                sweepdata.props["Type"] = sweeptype
                if sweeptype == "Interpolating":
                    sweepdata.props["InterpTolerance"] = interpolation_tol
                    sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1

                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.update()
                return sweepname


    @aedt_exception_handler
    def create_linear_count_sweep(self, setupname, unit, freqstart, freqstop, num_of_freq_points,
                                  sweepname=None, save_fields=True, save_rad_fields=False):
        """Create a discrete sweep with the specified number of points.

        Parameters
        ----------
        setupname : str
            Setup name.
        freqstart : float
            Starting grequency of sweep,  such as ``1``.
        freqstop : float
            Stopping frequency of the sweep.
        sweepname : str
            Name of the sweep. The default is ``None``.
        unit : str
            Units ("MHz", "GHz"...).
        num_of_freq_points : int
            Number of frequency points in the range.
        save_fields : bool
            Boolean. The default is ``True``.
        save_rad_fields :
            Boolean. The default is ``False``.

        Returns
        -------
        :class: SweepHFSS
            Sweep name

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} is already present. Rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + unit,
                sweepdata.props["RangeEnd"] = str(freqstop) + unit,
                sweepdata.props["RangeCount"] = num_of_freq_points,
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearCount"
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.update()
                return sweepname

    @aedt_exception_handler
    def create_linear_step_sweep(self, setupname, unit, freqstart, freqstop, step_size,
                                 sweepname=None, save_fields=True, save_rad_fields=False):
        """Create a discrete sweep with the specified number of points.

        Parameters
        ----------
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        sweepname : str
            Name of the sweep. The default is ``None``.
        unit : str
            Units ("MHz", "GHz"...).
        step_size : float
            Frequency size of the step.
        setupname : str
            Name of the setup.
        save_fields : bool
            Boolean. The default is ``True``.
        save_rad_fields : bool
            Boolean. The default is ``False``.

        Returns
        -------
        :class: SweepHFSS
            Sweep name

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepname


    @aedt_exception_handler
    def create_discrete_sweep(self, setupname, sweepname="SinglePoint", freq="1GHz", save_field=True, save_radiating_field=False):
        """Create a discrete sweep with a single frequency value.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        freq : str
            Sweep frequency (including ``Units``) as string. The default is ``1GHz``.
        sweepname : str
            Name of the sweep. The default is ``SinglePoint``.
        save_field : bool
            Boolean. The default is ``True``.
        save_radiating_field : bool
            Boolean. The default is ``False``.

        Returns
        -------
        :class: SweepHFSS
            Sweep name

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = freq
                sweepdata.props["RangeEnd"] = freq
                sweepdata.props["SaveSingleField"] = save_field
                sweepdata.props["SaveFields"] = save_field
                sweepdata.props["SaveRadFields"] = save_radiating_field
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "SinglePoints"
                sweepdata.update()
                self._messenger.add_info_message("Sweep Created Correctly")
                return sweepname


    @aedt_exception_handler
    def create_circuit_port_between_objects(self, startobj, endobject, axisdir="XYNeg", impedance=50, portname=None,
                                            renorm=True, renorm_impedance=50, deemb=False):
        """Create a circuit port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``XYNeg``.
        impedance :
            Port impedance. The default is ``50``.
        portname :
            Name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The default is ``True``.
        renorm_impedance :
            Float or string. Renormalize impedance. The default is ``50``.
        deemb :
            Boolean. DEembed port. The default is ``False``.

        Returns
        -------
        type
            Port name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            out, parallel = self.modeler.primitives.find_closest_edges(startobj, endobject, axisdir)
            port_edges = []
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self._create_circuit_port(out, impedance,portname, renorm, deemb,renorm_impedance=renorm_impedance):
                return portname
        return False

    @aedt_exception_handler
    def create_lumped_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, portname=None,
                                           renorm=True, deemb=False,port_on_plane=True):
        """Create a lumped taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``XYNeg``.
        impedance :
            Port impedance. The default is ``50``.
        portname :
            Name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The value is ``True``.
        deemb :
            Boolean. DEembed port. The value is ``False``.
        port_on_plane :
            Boolean. If ``True``, the source is to be created on the plane ortogonal to ``AxisDir``. 
            The default is ``True``.

        Returns
        -------
        type
            Port name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, port_on_plane)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1, impedance, portname,renorm, deemb)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(faces[0], endobject, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def create_voltage_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Creates a voltage source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default value is ``XYNeg``.
            The default value is ``XYNeg``.
        sourcename :
            Optional. Name of the source. The default is ``None``.
        source_on_plane :
            Boolean. If ``True``, the source is to be created on the plane ortogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        type
           Source name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_current_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Create a voltage source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the VS. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Optional. Name of the source. The default is ``None``.
        source_on_plane :
            Boolean. If ``True``, the source is to created on the plane ortogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        type
            Source name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_source_excitation(self, sheet_name, point1, point2, sourcename, sourcetype="Voltage"):
        """

        Parameters
        ----------
        sheet_name :
            The name of the sheet.
        point1 :
            
        point2 :
            
        sourcename :
            
        sourcetype :
             The default is ``Voltage``.

        Returns
        -------

        """

        props = OrderedDict({"Objects": [sheet_name],
               "Direction":OrderedDict({"Start": point1, "End": point2})})

        bound = BoundaryObject(self, sourcename, props, sourcetype)
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def create_wave_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1, portname=None,
                                         renorm=True, deembed_dist=0, port_on_plane=True, add_pec_cap=False):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        impedance :
            Port impedance. The default is ``50``.
        nummodes :
            Number of modes. The default is ``1``.
        portname :
            Name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The default is ``True``
        deembed_dist :
            Deembed distance. Float in model units. The default for model units is ``mm``. If ``0``, deembed is disabled.
        port_on_plane :
            Boolean. If ``True``, the port is to be created on the plane ortogonal to ``AxisDir``. The default is ``True``.
        add_pec_cap :
             The default is ``False``.

        Returns
        -------
        :class: BoundaryObject
            Port name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, port_on_plane)
            if add_pec_cap:
                dist = GeometryOperators.points_distance(point0, point1)
                self._create_pec_cap(sheet_name, axisdir, dist/10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def _create_pec_cap(self, sheet_name, axisdir, pecthick):
        vector = [0, 0, 0]
        if axisdir < 3:
            vector[divmod(axisdir, 3)[1]] = -pecthick / 2
        else:
            vector[divmod(axisdir, 3)[1]] = pecthick / 2

        status, pecobj = self.modeler.duplicate_along_line(sheet_name, vector)
        self.modeler.thicken_sheet(pecobj[0], pecthick, True)
        self.assignmaterial(pecobj[0], "pec")
        return True

    @aedt_exception_handler
    def create_wave_port_microstrip_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1, portname=None,
                                         renorm=True, deembed_dist=0, vfactor=3, hfactor=5):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        impedance :
            Port impedance. The default is ``50``.
        nummodes :
            Number of modes. The default is ``1``.
        portname :
            Name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The default is ``True``.
        deembed_dist :
            Deembed distance. Float in model units (default mm). If ``0`` Deembed is disabled.
        vfactor :
            Port vertical factor. The default is ``3``.
        hfactor :
            Port horizontal factor. The default is ``5``.

        Returns
        -------
        :class: BoundaryObject
            Port name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_microstrip_sheet_from_object_closest_edge(startobj,endobject,axisdir, vfactor, hfactor)
            dist = GeometryOperators.points_distance(point0, point1)
            self._create_pec_cap(sheet_name, axisdir,dist/10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def create_perfecte_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, is_infinite_gnd=False, bound_on_plane=True ):
        """Creates a Perfect E  taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Perfect E name. The default is ``None``.
        bound_on_plane :
            Boolean. If ``True``, the perfect E is to be created on the plane ortogonal to ``AxisDir``. The default is ``True``.
        is_infinite_gnd :
             The default is ``False``.

        Returns
        -------
        :class: BoundaryObject
            Boundary object

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_name, sourcename, is_infinite_gnd)
        return False

    @aedt_exception_handler
    def create_perfecth_from_objects(self, startobj, endobject, axisdir=0, sourcename=None,bound_on_plane=True):
        """Create a Perfect H taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Perfect H name. The default is ``None``.
        bound_on_plane :
            Boolean. If ``True``, perfect H is to created on the plane ortogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class: BoundaryObject
            Boundary object

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_name, sourcename)
        return None

    @aedt_exception_handler
    def SARSetup(self,Tissue_object_List_ID, TissueMass=1, MaterialDensity=1,  voxel_size=1, Average_SAR_method=0):
        """Set SAR settings.

        Parameters
        ----------
        Tissue_object_List_ID :
            33
        TissueMass :
            param MaterialDensity: The default is ``1``.
        voxel_size :
            param Average_SAR_method: The default is ``1``.
        MaterialDensity :
             The default is ``1``.
        Average_SAR_method :
             The default is ``0``.

        Returns
        -------
        Boolean
        """
        self.odesign.SARSetup(TissueMass, MaterialDensity, Tissue_object_List_ID, voxel_size, Average_SAR_method)
        return True

    @aedt_exception_handler
    def create_open_region(self, Frequency="1GHz", Boundary="Radiation", ApplyInfiniteGP=False, GPAXis="-z"):
        """Create an open region on the active editor.

        Parameters
        ----------
        Frequency :
            Frequency with units. The  default is ``1GHz``.
        Boundary :
            Boundary Type. The default is ``Radition``.
        ApplyInfiniteGP :
            Boolean to apply an infinite ground plane. The default is ``False``.
        GPAXis :
             The default is``-z``.

        Returns
        -------
        Boolean
        """
        vars= [
                "NAME:Settings",
                "OpFreq:="	, Frequency,
                "Boundary:="		, Boundary,
                "ApplyInfiniteGP:="	, ApplyInfiniteGP
            ]
        if ApplyInfiniteGP:
            vars.append("Direction:=")
            vars.append(GPAXis)

        self.omodelsetup.CreateOpenRegion(vars)
        return True

    @aedt_exception_handler
    def create_lumped_rlc_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, rlctype="Parallel",
                                          Rvalue=None, Lvalue=None, Cvalue=None, bound_on_plane=True):
        """Creates a Perfect H taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Perfect H name. The default is ``None``.
        Cvalue :
            Capacitance value in F. None to disable. The default is ``None``.
        Lvalue :
            Inductance value in H. None to disable. The default is ``None``.
        rlctype :
            The RLC type. Choices are ``Parallel" or "Series". The default is ``Parallel``.
        Rvalue :
            Resistance value in Ohm. None to disable. The default is ``None``.
        bound_on_plane :
            Boolean. If ``True``, the boundary is to be created on the plane ortogonal to ``AxisDir``.
            The default is ``True``.

        Returns
        -------
        :class: BoundaryObject
            Boundary name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (Rvalue or Lvalue or Cvalue):
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]

            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start":start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue)+"ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue)+"H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue)+"F"
            bound = BoundaryObject(self, sourcename, props, "LumpedRLC")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def create_impedance_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, resistance=50, reactance=0, is_infground=False, bound_on_plane=True):
        """Create an impedance taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the impedance. It should be one of the values for ``Application.AxisDir``, which are:
            ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``. The default is ``0``.
        sourcename :
            Name of the impedance. The default is ``None``.
        resistance :
            Resistance value in Ohm. None to disable. The default is ``50``.
        reactance :
            Reactance value in Ohm. None to disable. The default is ``0``.
        bound_on_plane :
            Boolean. If ``True``, the impedance is to be created on the plane ortogonal to ``AxisDir``. The default is ``True``.
        is_infground :
             The default is ``False``.

        Returns
        -------
        :class: BoundaryObject
            Boundary name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] :
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject, axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            bound = BoundaryObject(self, sourcename, props, 'Impedance')
            if bound.create():
                self.boundaries.append(bound)
                return bound

        return False

    @aedt_exception_handler
    def create_boundary(self, boundary_type=BoundaryType.PerfectE, sheet_name=None, boundary_name="", is_infinite_gnd=False):
        """Create a boundary given specific inputs.

        Parameters
        ----------
        boundary_type :
            Boundary type object. Choices are ``PerfectE``, ``PerfectH``, ``Aperture``, and ``Radiation``. The default is ``BoundaryType.PerfectE``.
        sheet_name :
            Name  of the sheet. It can be an integer (facesID), a string (sheet), or a list of previous. The default is ``None``.
        boundary_name :
            Name of the boundary. The default is `` ``.
        is_infinite_gnd :
            Boolean, The default is ``False``.

        Returns
        -------
        :class: BoundaryObject
            Boundary object if successful

        """

        props = {}
        sheet_name = self.modeler._convert_list_to_ids(sheet_name)
        if type(sheet_name) is list:
            if type(sheet_name[0]) is str:
                props["Objects"] = sheet_name
            else:
                props["Faces"] = sheet_name

        if boundary_type == self.BoundaryType.PerfectE:
            props['InfGroundPlane'] = is_infinite_gnd
            bound = BoundaryObject(self, boundary_name, props, 'PerfectE')
        elif boundary_type == self.BoundaryType.PerfectH:
            bound = BoundaryObject(self, boundary_name, props, 'PerfectH')
        elif boundary_type == self.BoundaryType.Aperture:
            bound = BoundaryObject(self, boundary_name, props, 'Aperture')
        elif boundary_type == self.BoundaryType.Radiation:
            props['IsFssReference'] = False
            props['IsForPML'] = False
            bound = BoundaryObject(self, boundary_name, props, 'Radiation')
        else:
            return None
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _get_reference_and_integration_points(self, sheet, axisdir):
        objID = self.modeler.oeditor.GetFaceIDs(sheet)
        face_edges = self.modeler.primitives.get_face_edges(objID[0])
        mid_points = [self.modeler.primitives.get_edge_midpoint(i) for i in face_edges]
        if axisdir < 3:
            min_point = [1e6, 1e6, 1e6]
            max_point = [-1e6, -1e6, -1e6]
            for el in mid_points:
                if el[axisdir] < min_point[axisdir]:
                    min_point = el
                if el[axisdir] > max_point[axisdir]:
                    max_point = el
        else:
            min_point = [-1e6, -1e6, -1e6]
            max_point = [1e6, 1e6, 1e6]
            for el in mid_points:
                if el[axisdir - 3] > min_point[axisdir - 3]:
                    min_point = el
                if el[axisdir-3] < max_point[axisdir-3]:
                    max_point = el

        refid = self.modeler.primitives.get_bodynames_from_position(min_point)
        refid.remove(sheet)
        diels = self.get_all_dielectrics_names()
        for el in refid:
            if el in diels:
                refid.remove(el)

        int_start=None
        int_stop = None
        if min_point != max_point:
            int_start = min_point
            int_stop = max_point
        return refid, int_start, int_stop

    @aedt_exception_handler
    def create_wave_port_from_sheets(self, sheet, deemb=0, axisdir=0, impedance=50, nummodes=1, portname=None,
                                     renorm=True):
        """Create waveport on sheet objects created starting from sheets.

        Parameters
        ----------
        sheet :
            List of input sheets from which to create ports.
        deemb :
            Deembedding value distance. Float in model units. The default is ``0``.
        axisdir :
            Position of the reference object. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        impedance :
            Port impedance. The default is ``50``.
        nummodes :
            Number of modes. The default is ``1``.
        portname :
            The name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The default is ``True``.
        deembed_dist :
            Deembed distance. Float in model units (default mm). If ``0`` deembed is disabled.

        Returns
        -------
        list
            List of objects created.
        """
        sheet = self.modeler.convert_to_selections(sheet, True)
        portnames = []
        for obj in sheet:
            refid, int_start, int_stop = self._get_reference_and_integration_points(obj, axisdir)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                b = self._create_waveport_driven(obj, int_start, int_stop, impedance, portname, renorm, nummodes, deemb)
                if b:
                    portnames.append(b)
            else:
                faces = self.modeler.primitives.get_object_faces(obj)
                if len(refid)>0:
                    b = self._create_port_terminal(faces[0], refid, portname, iswaveport=True)
                    if b:
                        portnames.append(b)

                else:
                    return False
        return portnames

    @aedt_exception_handler
    def assign_lumped_port_to_sheet(self, sheet_name, axisdir=0, impedance=50, portname=None,
                                    renorm=True, deemb=False, reference_object_list=[]):
        """Create a Lumped taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of sheet object.
        axisdir :
            Direction of port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        impedance :
            Port impedance. The default is ``50``.
        portname :
            Name of the port. The default is ``None``.
        renorm :
            Boolean. Renormalize mode. The default is ``True``.
        deemb :
            bool) Deembed port. The default is ``False``.
        reference_object_list :
            For a Driven Terminal Solutions only. List of reference conductors. The default is ``[]``.

        Returns
        -------
        type
            Object name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            cond = self.get_all_conductors_names()
            touching = self.modeler.primitives.get_bodynames_from_position(point0)
            listcond = []
            for el in touching:
                if el in cond:
                    listcond.append(el)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1, impedance, portname, renorm, deemb)
            else:
                if not reference_object_list:
                    cond = self.get_all_conductors_names()
                    touching = self.modeler.primitives.get_bodynames_from_position(point0)
                    reference_object_list = []
                    for el in touching:
                        if el in cond:
                            reference_object_list.append(el)
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(faces[0], reference_object_list, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def assig_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a voltage source taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of sheet on which to apply the boundary.
        axisdir :
            Position of the VS. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Optional. Name of the source. The default is ``None``.

        Returns
        -------
        type
            Object name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def assign_current_source_to_sheet(self, sheet_name,  axisdir=0, sourcename=None):
        """Creates a voltage source taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of the sheet on which to apply the boundary.
        axisdir :
            Position of VS. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
           Optional. Name of the source. The default is ``None``.

        Returns
        -------
        type
            Object name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def assign_perfecte_to_sheets(self, sheet_list, sourcename=None, is_infinite_gnd=False ):
        """Creates a pPerfect E  taking one sheet.

        Parameters
        ----------
        sheet_list :
            Name of the sheet or list on which to apply the boundary.
        sourcename :
            Perfect E name. The default is ``None``.
        is_infinite_gnd :
            Boolean to determine if Perfect E is an infinite ground. The default is ``False``.

        Returns
        -------
        type
            Boundary object

        """
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_list, sourcename, is_infinite_gnd)
        return None

    @aedt_exception_handler
    def assign_perfecth_to_sheets(self, sheet_list, sourcename=None):
        """Create a Perfect H taking one sheet.

        Parameters
        ----------
        sheet_list :
            List of sheets on which to apply the boundary.
        sourcename :
            Perfect H name. The default is ``None``.

        Returns
        -------
        type
            Boundary object

        """
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_list, sourcename)
        return None

    @aedt_exception_handler
    def assign_lumped_rlc_to_sheet(self, sheet_name, axisdir=0, sourcename=None, rlctype="Parallel",
                                          Rvalue=None, Lvalue=None, Cvalue=None):
        """Create a Perfect H taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of the sheet on which to apply the boundary.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``. The default is ``0``.
        sourcename :
            Perfect H name. The default is ``None``.
        Cvalue :
            Capacitance value in F. None to disable. The default is ``None``.
        Lvalue :
            Inductance value in H. None to disable. The default is ``None``.
        rlctype :
            The RLC type. Choices are ``Parallel`` or ``Series``. The default is ``Parallel``.
        Rvalue :
            Resistance value in Ohm. None to disable. The default is ``None``.

        Returns
        -------
        type
            Object name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (Rvalue or Lvalue or Cvalue):
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]
            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start":start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue)+"ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue)+"H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue)+"F"
            bound = BoundaryObject(self, sourcename, props, "LumpedRLC")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def assign_impedance_to_sheet(self, sheet_name, sourcename=None, resistance=50, reactance=0, is_infground=False):
        """Create an impedance taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of the sheet on which to apply the boundary.
        sourcename :
            Impedance name. The default is ``None``.
        resistance :
            Resistance value in Ohm. None to disable. The default is ``50``.
        reactance :
            Reactance value in Ohm. None to disable. The default is ``0``.
        is_infground :
             The default is ``False``.

        Returns
        -------
        type
            Object name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] :

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            bound = BoundaryObject(self, sourcename, props, "Impedance")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def create_circuit_port_from_edges(self, edge_signal, edge_gnd, port_name="",
                                       port_impedance="50",
                                       renormalize=False, renorm_impedance="50",
                                       deembed=False):
        """Create circuit port. Integration line is from edge2 to edge1.
        
        Renormalize impedance is ignored in driven terminal.
        impedance format: - int, float, str:"50", str: "50+1i*55"

        Parameters
        ----------
        edge_signal :
            Edge identifier.
        edge_gnd :
            Edge identifier.
        port_name :
            Name of the port. The default is ``""``.
        port_impedance :
            str impedance. The default is ``50``.
        renormalize :
            Boolean. The default is ``False``.
        renorm_impedance :
            str impedance. The default is ``50``
        deembed :
            Boolean. The default is ``50``

        Returns
        -------
        type
            Boolean

        """
        edge_list = [edge_signal, edge_gnd]
        if not port_name:
            port_name = generate_unique_name("Port")
        elif port_name + ":1" in self.modeler.get_excitations_name():
            port_name = generate_unique_name(port_name)

        result = self._create_circuit_port(edge_list, port_impedance, port_name, renormalize,
                                           deembed, renorm_impedance=renorm_impedance)
        if result:
            return port_name
        else:
            return False

    @aedt_exception_handler
    def edit_source(self, portandmode, powerin, phase="0deg"):
        """Set up the power loaded to the filter. This is needed for thermal analysis.

        Parameters
        ----------
        powerin :
            Power (in Watts) or the project variable to be put as stored energy in the the project.
        portandmode :
            Portname and mode. Example Port1:1
        phase :
             The default is ``0deg``.

        Returns
        -------

        """
        self._messenger.add_info_message("Setting Up Power to Eigemode " + powerin + "Watt")
        if self.solution_type != "Eigenmode":
            self.osolution.EditSources([["IncludePortPostProcessing:=", True, "SpecifySystemPower:=", False],
                                        ["Name:=", portandmode, "Magnitude:=", powerin, "Phase:=", phase]])
        else:
            self.osolution.EditSources(
                [["FieldType:=", "EigenStoredEnergy"], ["Name:=", "Modes", "Magnitudes:=", [powerin]]])
        return True

    @aedt_exception_handler
    def thicken_port_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """thicken_port_sheets: Create thicken sheets of value "mm" over the full list of input port faces inputlist
        inputlist: List of faces to thicken.
        value: Value in mm to thicken.
        internalExtr: Define if the sheet must also be extruded internally.
        internalvalue: Define the value in mm to thicken internally the sheet (vgoing into the model).

        Parameters
        ----------
        inputlist :
            
        value :
            
        internalExtr :
             (Default value = True)
        internalvalue :
             (Default value = 1)

        Returns
        -------

        """
        tol = 1e-6
        ports_ID={}
        aedt_bounding_box = self.modeler.primitives.get_model_bounding_box()
        directions = {}
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            faceCenter = self.modeler.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()

                self._odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            maxarea = 0
            for f in objID:
                faceArea = self.modeler.primitives.get_face_area(int(f))
                if faceArea > maxarea:
                    maxarea = faceArea
                    faceCenter = self.modeler.oeditor.GetFaceCenter(int(f))
            if directions[el] == "Internal":
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(value) + "mm",
                        "BothSides:=", False
                    ])
            else:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(value) + "mm",
                        "BothSides:=", False
                    ])
            if "Vacuum" in el:
                newfaces = self.modeler.oeditor.GetFaceIDs(el)
                for f in newfaces:
                    try:
                        fc2 = self.modeler.oeditor.GetFaceCenter(f)
                        fc2 = [float(i) for i in fc2]
                        fa2 = self.modeler.primitives.get_face_area(int(f))
                        faceoriginal = [float(i) for i in faceCenter]
                        #dist = mat.sqrt(sum([(a*a-b*b) for a,b in zip(faceCenter, fc2)]))
                        if abs(fa2 - maxarea) < tol**2 and (abs(faceoriginal[2] - fc2[2]) > tol or abs(
                                faceoriginal[1] - fc2[1]) > tol or abs(faceoriginal[0] - fc2[0]) > tol):
                            ports_ID[el] = int(f)

                        # if (abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) > tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) > tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) > tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol):
                        #     ports_ID[el] = int(f)
                    except:
                        pass
            if internalExtr:
                objID2 = self.modeler.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.modeler.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.modeler.oeditor.MoveFaces(
                                [
                                    "NAME:Selections",
                                    "Selections:=", el,
                                    "NewPartsModelFlag:=", "Model"
                                ],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=", True,
                                        "OffsetDistance:=", str(internalvalue) + "mm",
                                        "MoveVectorX:=", "0mm",
                                        "MoveVectorY:=", "0mm",
                                        "MoveVectorZ:=", "0mm",
                                        "FacesToMove:=", [int(fid)]
                                    ]
                                ])
                    except:
                        self.messenger.add_debug_message("done")
                        # self.modeler_oproject.ClearMessages()
        return ports_ID

    @aedt_exception_handler
    def validate_full_design(self, dname=None, outputdir=None, ports=None):
        """Validate the design based on the expected value and save information in log file
        and also return the validation information in a list.

        Parameters
        ----------
        dname :
            Optional. Name of the design to validate. The default is ``None``.
        outputdir :
            Optional. The output directory to which to save the log file. The default is ``None``.
        ports :
            Number of excitations (sum of modes) that is expected. The default is ``None``.

        Returns
        -------
        type
            All the information in a list for later use.

        """
        self._messenger.add_debug_message("Design Validation Checks")
        validation_ok = True
        val_list = []
        if not dname:
            dname = self.design_name
        if not outputdir:
            outputdir = self.project_path
        pname = self.project_name
        validation_log_file = os.path.join(outputdir, pname + "_" + dname + "_validation.log")

        # Desktop Messages
        msg = "Desktop Messages:"
        val_list.append(msg)
        temp_msg = list(self._desktop.GetMessages(pname, dname, 0))
        if temp_msg:
            temp2_msg = [i.strip('Project: ' + pname + ', Design: ' + dname + ', ').strip('\r\n') for i in temp_msg]
            val_list.extend(temp2_msg)

        # Run design validation and write out the lines to the log.
        temp_val_file = os.path.join(os.environ['TEMP'], "\\val_temp.log")
        simple_val_return = self.validate_simple(temp_val_file)
        if simple_val_return == 1:
            msg = "Design validation check PASSED."
        elif simple_val_return == 0:
            msg = "Design validation check ERROR."
            validation_ok = False
        val_list.append(msg)
        msg = "Design Validation Messages:"
        val_list.append(msg)
        if os.path.isfile(temp_val_file):
            with open(temp_val_file, 'r') as df:
                temp = df.read().splitlines()
                val_list.extend(temp)
            os.remove(temp_val_file)
        else:
            msg = "** No design validation file isfound. **"
            self._messenger.add_debug_message(msg)
            val_list.append(msg)
        msg = "** End of design validation messages. **"
        val_list.append(msg)

        # Find the excitations and check or list them out
        msg = "Excitations Check:"
        val_list.append(msg)
        if self.solution_type != 'Eigenmode':
            detected_excitations = self.modeler.get_excitations_name()
            if ports:
                if self.solution_type == 'DrivenTerminal':
                    ports_t = ports * 2  # For each port, there is terminal and reference excitations.
                else:
                    ports_t = ports
                if ports_t != len(detected_excitations):
                    msg = "** Port Number Error. Check the model. **"
                    self._messenger.add_error_message(msg)
                    val_list.append(msg)
                    validation_ok = False
                else:
                    msg1 = "Solution type: " + str(self.solution_type)
                    msg2 = "Ports Requested: " + str(ports)
                    msg3 = "Defined excitations number: " + str(len(detected_excitations))
                    msg4 = "Defined excitations names: " + str(detected_excitations)
                    val_list.append(msg1)
                    val_list.append(msg2)
                    val_list.append(msg3)
                    val_list.append(msg4)
        else:
            msg = "Eigen model is detected. No excitatons are defined."
            self._messenger.add_debug_message(msg)
            val_list.append(msg)

        # Find the number of analysis setups and output the info.
        msg = "Analysis Setup Messages:"
        val_list.append(msg)
        setups = list(self.oanalysis.GetSetups())
        if setups:
            msg = "Detected setup and sweep: "
            val_list.append(msg)
            for setup in setups:
                msg = str(setup)
                val_list.append(msg)
                if self.solution_type != 'EigenMode':
                    sweepsname = self.oanalysis.GetSweeps(setup)
                    if sweepsname:
                        for sw in sweepsname:
                            msg = ' |__ ' + sw
                            val_list.append(msg)
        else:
            msg = 'No setup is detected.'
            val_list.append(msg)

        with open(validation_log_file, "w") as f:
            for item in val_list:
                f.write("%s\n" % item)
        return val_list, validation_ok  # Return all the information in a list for later use.


    @aedt_exception_handler
    def create_scattering(self, PlotName="S Parameter Plot Nominal", sweep_name=None, PortNames=None, PortExcited=None, variations=None ):
        """Create scattering report.
        
        
        sweeps = design eXploration variations (list of str)
        PortNames = (list of str)
        PortExcited = (str)
        :return:

        Parameters
        ----------
        PlotName :
             The name of the plot. The default is ``Parameter Plot Nominal``.
        sweep_name :
             The name of the sweep. The default is ``None``.
        PortNames :
             The name of the port. The default is ``None``.
        PortExcited :
             The default is ``None``.
        variations :
             The default is ``None``.

        Returns
        -------

        """
        # Set plot name
        # Setup arguments list for CreateReport function
        Families = ["Freq:=", ["All"]]
        if variations:
            Families += variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        elif sweep_name not in self.existing_analysis_sweeps:
            self.messenger.add_error_message("Setup {} doesn't exist in Setup list".format(sweep_name))
            return False
        if not PortNames:
            PortNames = self.modeler.get_excitations_name()
        full_matrix = False
        if not PortExcited:
            PortExcited = PortNames
            full_matrix = True
        if type(PortNames) is str:
            PortNames = [PortNames]
        if type(PortExcited) is str:
            PortExcited = [PortExcited]
        list_y = []
        for p in list(PortNames):
            for q in list(PortExcited):
                if not full_matrix:
                    list_y.append("dB(S(" + p + "," + q + "))")
                elif PortExcited.index(q) >= PortNames.index(p):
                    list_y.append("dB(S(" + p + "," + q + "))")

        Trace = ["X Component:=", "Freq", "Y Component:=", list_y]
        solution_data = ""
        if self.solution_type == "DrivenModal":
            solution_data = "Modal Solution Data"
        elif self.solution_type == "DrivenTerminal":
            solution_data = "Terminal Solution Data"
        if solution_data != "":
            # run CreateReport function

            self.post.oreportsetup.CreateReport(
                PlotName,
                solution_data,
                "Rectangular Plot",
                sweep_name,
                ["Domain:=", "Sweep"],
                Families,
                Trace,
                [])
            return True
        return False

        # export the image

    @aedt_exception_handler
    def create_qfactor_report(self, project_dir, outputlist, setupname, plotname, Xaxis="X"):
        """Export a CSV file of the EigenQ plot

        Parameters
        ----------
        project_dir :
            Output directory.
        outputlist :
            Output quantity. In this case, the Q-factor.
        setupname :
            Name of the setup from which to generate the report.
        plotname :
            Name of the plot.
        Xaxis :
            X-axis value. The default is ``"X"``.

        Returns
        -------

        """
        npath = os.path.normpath(project_dir)

        # Setup arguments list for createReport function
        args = [Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", Xaxis, "Y Component:=", outputlist]

        self.post.post_oreport_setup.CreateReport(plotname, "Eigenmode Parameters", "Rectangular Plot",
                                                  setupname + " : LastAdaptive", [], args, args2, [])
        return True

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename=None, variation=[], variations_value=[]):
        """Synopsis: Export Touchston file to a local folder.
              
        Parameters
        ----------
        solutionname :
             Name of the solution that has been solved.
        sweepname :
             Name of the sweep that has been solved.
        filename :
             Full path to the output file. The default is ``None``.
        variation :
             List of all parameter variations, such as ``["$AmbientTemp", "$PowerIn"]``. The default is ``[]``.
        variations_value :
             List of all parameter variation values), such as ``["22cel", "100"]``. The default is ``[]``.

        Returns
        -------

        """

        # Normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation,variations_value):
                appendix += "_"+ v + vv.replace("\'","")
            ext = ".S" + str(self.oboundary.GetNumExcitations())+"p"
            filename = os.path.join(self.project_path, solutionname +"_"+ sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
        DesignVariations = ""
        i=0
        for el in variation:
            DesignVariations += str(variation[i]) + "=\'" + str(variations_value[i].replace("\'", "")) + "\' "
            i+=1
            # DesignVariations = "$AmbientTemp=\'22cel\' $PowerIn=\'100\'"
        # array containing "SetupName:SolutionName" pairs (note that setup and solution are separated by a colon)
        SolutionSelectionArray = [solutionname + ":" + sweepname]
        # 2=tab delimited spreadsheet (.tab), 3= touchstone (.sNp), 4= CitiFile (.cit),
        # 7=Matlab (.m), 8=Terminal Z0 spreadsheet
        FileFormat = 3
        OutFile = filename  # full path of output file
        FreqsArray = ["all"]  # array containin the frequencies to export, use ["all"] for all frequencies
        DoRenorm = True  # perform renormalization before export
        RenormImped = 50  # Real impedance value in ohm, for renormalization
        DataType = "S"  # Type: "S", "Y", or "Z" matrix to export
        Pass = -1  # The pass to export. -1 = export all passes.
        ComplexFormat = 0  # 0=Magnitude/Phase, 1=Real/Immaginary, 2=dB/Phase
        DigitsPrecision = 15  # Touchstone number of digits precision
        IncludeGammaImpedance = True  # Include Gamma and Impedance in comments
        NonStandardExtensions = False  # Support for non-standard Touchstone extensions

        self.osolution.ExportNetworkData(DesignVariations, SolutionSelectionArray, FileFormat,
                                         OutFile, FreqsArray, DoRenorm, RenormImped, DataType, Pass,
                                         ComplexFormat, DigitsPrecision, False, IncludeGammaImpedance,
                                         NonStandardExtensions)
        return True


    @aedt_exception_handler
    def set_export_touchstone(self, activate):
        """Set automatic export of Touchstone file after simulation set to ``True``

        Parameters
        ----------
        activate : bool
            Export after simulation.

        Returns
        -------
        type
            ``True`` if operation succeeded.

        """

        settings = []
        if activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(True)
            settings.append("Export Dir:=")
            settings.append("")
        elif not activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(False)
        self.odesign.SetDesignSettings(settings)
        return True

    @aedt_exception_handler
    def assign_radiation_boundary_to_objects(self, obj_names, boundary_name=""):
        """

        Parameters
        ----------
        obj_names :
             Names of the objects.       
        boundary_name :
             Name of the boundary. The default is ``""``.

        Returns
        -------

        """
        #TODO: to be tested

        """
        Assign radiation boundary to one or more objects (usually airbox objects).

        :param obj_names: Object name or ID to which the boundary condition is assigned.
        :param boundary_name: Optional. Name of the boundary.
        :return: ``True`` if correctly assigned.
        """
        object_list = self.modeler.convert_to_selections(obj_names, return_list=True)
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, object_list,rad_name)

    @aedt_exception_handler
    def assign_radiation_boundary_to_faces(self, faces_id, boundary_name=""):
        """Assign radiation boundary to one or more objects (usually airbox objects).

        Parameters
        ----------
        faces_id :
            Face ID to which the boundary condition is assigned.
        boundary_name :
            Optional. Name of the boundary. The default is ``""``.

        Returns
        -------
        Type
            ``True`` if correctly assigned.

        """
        if type(faces_id) is not list:
            faces_list = [int(faces_id)]
        else:
            faces_list = [int(i) for i in faces_id]
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, faces_list, rad_name)
