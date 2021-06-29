"""
This module contains these classes: ``FieldPlot``, ``PostProcessor``, and ``SolutionData``.

These classes provide all functionalities for creating and editing plots in the 3D tools.

.. note::
   Some functionalities are available only in graphical mode.
"""
from __future__ import absolute_import
import os
import shutil
import random
import string
import time
import math
import itertools
from collections import OrderedDict
from ..modeler.Modeler import CoordinateSystem
from ..generic.general_methods import aedt_exception_handler, generate_unique_name, retry_ntimes
from ..application.Variables import AEDT_units

report_type = {"DrivenModal": "Modal Solution Data", "DrivenTerminal": "Terminal Solution Data",
               "Eigenmode": "EigenMode Parameters",
               "Transient Network": "Terminal Solution Data", "SBR+": "Modal Solution Data", "Transient": "Transient",
               "EddyCurrent": "EddyCurrent",
               "SteadyTemperatureAndFlow": "Monitor", "SteadyTemperatureOnly": "Monitor", "SteadyFlowOnly": "Monitor",
               "SteadyState": "Monitor", "NexximLNA": "Standard", "NexximDC": "Standard",
               "Magnetostatic": "Magnetostatic", "Electrostatic": "Electrostatic",
               "NexximTransient": "Standard", "HFSS3DLayout": "Terminal Solution Data", "Matrix": "Matrix",
               "HFSS 3D Layout Design": "Standard", "Q3D Extractor": "Matrix", "2D Extractor": "Matrix"}


class SolutionData(object):
    """SolutionData class.
    
    This class contains information from a  call to the ``GetSolutionfromVariation`` function.
    """
    @property
    def sweeps(self):
        """ """
        return self._sweeps

    @property
    def sweeps_siunits(self):
        """ """
        data = {}
        for el in self._sweeps:
            data[el] = self._convert_list_to_SI(self._sweeps[el], self._quantity(self.units_sweeps[el]), self.units_sweeps[el])
        return data

    @property
    def variations_value(self):
        """ """
        vars = self.nominal_variation.GetDesignVariableNames()
        variationvals = {}
        for v in vars:
            variationvals[v] = self.nominal_variation.GetDesignVariableValue(v)
        return variationvals

    @property
    def nominal_variation(self):
        """ """
        return self._nominal_variation

    @nominal_variation.setter
    def nominal_variation(self, val):
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

        """
        if 0 <= val <= self.number_of_variations:
            self._nominal_variation = self._original_data[val]
        else:
            print(str(val) + " not in Variations")

    @property
    def primary_sweep(self):
        """ """
        return self._primary_sweep

    @primary_sweep.setter
    def primary_sweep(self, ps):
        """Set the primary sweep to the source perimter.

        Parameters
        ----------
        ps : float
            Perimeter of the source.
            

        Returns
        -------

        """
        if ps in self.sweeps.keys():
            self._primary_sweep = ps

    @property
    def expressions(self):
        """ """
        mydata = [i for i in self._nominal_variation.GetDataExpressions()]
        return list(dict.fromkeys(mydata))

    def __init__(self, Data):
        self._original_data = Data
        self.number_of_variations = len(Data)
        self._nominal_variation = None
        self.nominal_variation = 0
        self._sweeps = None
        self._sweeps_names = list(self.nominal_variation.GetSweepNames())
        self.update_sweeps()

        self._primary_sweep = self._sweeps_names[0]
        self.nominal_sweeps = {}
        self.units_sweeps = {}
        for e in self.sweeps.keys():
            try:
                self.nominal_sweeps[e] = self.sweeps[e][0]
                self.units_sweeps[e] = self.nominal_variation.GetSweepUnits(e)
            except:
                self.nominal_sweeps[e] = None
        self.solutions_data_real = self._solution_data_real()
        self.solutions_data_imag = self._solution_data_imag()
        self.solutions_data_mag = {}
        self.units_data = {}
        for expr in self.expressions:
            self.solutions_data_mag[expr] = {}
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            for i in self.solutions_data_real[expr]:
                self.solutions_data_mag[expr][i] = abs(
                    complex(self.solutions_data_real[expr][i], self.solutions_data_imag[expr][i]))

    @aedt_exception_handler
    def update_sweeps(self):
        """:return:"""
        self._sweeps = OrderedDict({})
        for el in self._sweeps_names:
            self._sweeps[el] = [i for i in self.nominal_variation.GetSweepValues(el, False)]
            self._sweeps[el] = list(dict.fromkeys(self._sweeps[el]))
        return self._sweeps

    @aedt_exception_handler
    def _quantity(self, unit):
        """

        Parameters
        ----------
        unit :
            

        Returns
        -------

        """
        for el in AEDT_units:
            keys_units = [i.lower() for i in list(AEDT_units[el].keys())]
            if unit.lower() in keys_units:
                return el
        return None

    @aedt_exception_handler
    def _solution_data_real(self):
        """ """
        sols_data = {}
        for expression in self.expressions:
            solution = list(self.nominal_variation.GetRealDataValues(expression,False))
            values = []
            for el in reversed(self._sweeps_names):
                values.append(self.sweeps[el])
            solution_Data = {}
            i = 0
            for t in itertools.product(*values):
                solution_Data[t] = solution[i]
                i += 1
            sols_data[expression] = solution_Data
        return sols_data

    def _solution_data_imag(self):
        """ """
        sols_data = {}
        for expression in self.expressions:
            try:
                solution = list(self.nominal_variation.GetImagDataValues(expression,False))
            except:
                solution = [0 for i in range(len(self.solutions_data_real[expression]))]
            values = []
            for el in reversed(self._sweeps_names):
                values.append(self.sweeps[el])
            solution_Data = {}
            i = 0
            for t in itertools.product(*values):
                solution_Data[t] = solution[i]
                i += 1
            sols_data[expression] = solution_Data
        return sols_data

    @aedt_exception_handler
    def to_degrees(self, input_list):
        """Convert input list to degrees from radians.

        Parameters
        ----------
        input_list : list
            List of inputs in radians.

        Returns
        -------
        type
            List of inputs in degrees.

        """
        return [i*2*math.pi/360 for i in input_list]

    @aedt_exception_handler
    def to_radians(self, input_list):
        """Convert input list to radians from degrees.

        Parameters
        ----------
        input_list : list
            List of inputs in degrees.

        Returns
        -------
        type
            List of inputs in radians.

        """
        return [i*360/(2*math.pi) for i in input_list]

    def data_magnitude(self, expression=None, convert_to_SI=False):
        """Retrieve the data magnitude of a given expression. 
        
        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``, in which case the
            first expression is used.
        convert_to_SI : bool, optional
            Whether to convert data to the SI system. The default is ``False``.

        Returns
        -------
        list
            List of data.

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_mag[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol

    @aedt_exception_handler
    def _convert_list_to_SI(self,datalist, dataunits, units):
        """Convert a data list to the SI sysstem.

        Parameters
        ----------
        datalist : list
           List of data to convert.
        dataunits : 
           
        units :
            

        Returns
        -------
        list
           List of converted data.

        """
        sol = datalist
        if dataunits in AEDT_units and units in AEDT_units[dataunits]:
            sol = [i * AEDT_units[dataunits][units] for i in datalist]
        return sol

    @aedt_exception_handler
    def data_db(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None,`` in which case the first expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI system. The default is ``False``.

        Returns
        -------
        List
            List of data in the database.

        """
        if not expression:
            expression = self.expressions[0]

        return [10*math.log10(i) for i in self.data_magnitude(expression,convert_to_SI)]


    def data_real(self, expression=None, convert_to_SI=False):
        """Retrieve the real part of the data for an expression.

        Parameters
        ----------
        expression :
            Name of the expression. The default is ``None,`` in which case the first expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI system. The default is ``False``.

        Returns
        -------
        type
            List of real data.

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_real[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol

    def data_imag(self, expression=None, convert_to_SI=False):
        """Retrieve the imaginary part of data for an expression.

        Parameters
        ----------
         expression :
            Name of the expression. The default is ``None,`` in which case the first expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI system. The default is ``False``.

        Returns
        -------
        type
            List of imaginary data.

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_imag[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol



class FieldPlot:
    """FieldPlot class.
    
    Parameters
    ----------
    ofield :
    
    objlist : list
        List of objects.
    solutionName : str
        Name of the solution.
    quantityName : str
        Name of the plot or the name of the object.
    intrinsicList: dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.
    """
    def __init__(self, oField, objlist, solutionName, quantityName, intrinsincList={}):
        self.oField = oField
        self.faceIndexes = objlist
        self.solutionName = solutionName
        self.quantityName = quantityName
        self.intrinsincList = intrinsincList
        self.objtype = "Surface"
        self.listtype = "FaceList"
        self.name = "Field_Plot"
        self.Filled = False
        self.IsoVal = "Fringe"
        self.SmoothShade = True
        self.AddGrid = False
        self.MapTransparency = True
        self.Refinement = 0
        self.Transparency = 0
        self.SmoothingLevel = 0
        self.ArrowUniform = True
        self.ArrowSpacing = 0
        self.MinArrowSpacing = 0
        self.MaxArrowSpacing = 0
        self.GridColor = [255, 255, 255]
        self.PlotIsoSurface = True
        self.PointSize = 1
        self.CloudSpacing = 0.5
        self.CloudMinSpacing = -1
        self.CloudMaxSpacing = -1

    @aedt_exception_handler
    def create(self):
        """ """

        self.oField.CreateFieldPlot(self.surfacePlotInstruction, "Field")
        return True


    @aedt_exception_handler
    def update(self):
        """ """
        self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstruction)



    @aedt_exception_handler
    def modify_folder(self):
        """ """
        self.oField.SetFieldPlotSettings(self.plotFolder,
                                         [
                                             "NAME:FieldsPlotItemSettings",
                                             self.plotsettings])
        return True

    @aedt_exception_handler
    def delete(self):
        """ """
        self.oField.DeleteFieldPlot([self.name])

    @property
    def plotFolder(self):
        """ """
        return self.name

    @property
    def plotGeomInfo(self):
        """ """
        info = [1, self.objtype, self.listtype, 0]
        for index in self.faceIndexes:
            info.append(str(index))
            info[3] += 1
        return info

    @property
    def intrinsicVar(self):
        """
        
        Returns
        -------
        list or dict
        List or dictionary of the variables for the field plot.

        """
        var = ""
        if type(self.intrinsincList) is list:
            l = 0
            while l < len(self.intrinsincList):
                val = self.intrinsincList[l + 1]
                if ":=" in self.intrinsincList[l] and type(self.intrinsincList[l+1]) is list:
                    val = self.intrinsincList[l + 1][0]
                ll=self.intrinsincList[l].split(":=")
                var += ll[0] + "=\'" + str(val) + "\' "
                l += 2
        else:
            for a in self.intrinsincList:
                var += a + "=\'" + str(self.intrinsincList[a]) + "\' "
        return var

    @property
    def plotsettings(self):
        """ """
        if self.objtype == "Surface":
            arg = [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=", self.Filled,
                "IsoValType:=", self.IsoVal,
                "SmoothShade:=", self.SmoothShade,
                "AddGrid:=", self.AddGrid,
                "MapTransparency:=", self.MapTransparency,
                "Refinement:=", self.Refinement,
                "Transparency:=", self.Transparency,
                "SmoothingLevel:=", self.SmoothingLevel,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=", self.ArrowUniform,
                    "ArrowSpacing:=", self.ArrowSpacing,
                    "MinArrowSpacing:=", self.MinArrowSpacing,
                    "MaxArrowSpacing:=", self.MaxArrowSpacing
                ],
                "GridColor:=", self.GridColor
            ]
        else:
            arg = [
                "NAME:PlotOnVolumeSettings",
                "PlotIsoSurface:=", self.PlotIsoSurface,
                "PointSize:=", self.PointSize,
                "Refinement:=", self.Refinement,
                "CloudSpacing:=", self.CloudSpacing,
                "CloudMinSpacing:=", self.CloudMinSpacing,
                "CloudMaxSpacing:=", self.CloudMaxSpacing,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=", self.ArrowUniform,
                    "ArrowSpacing:=", self.ArrowSpacing,
                    "MinArrowSpacing:=", self.MinArrowSpacing,
                    "MaxArrowSpacing:=", self.MaxArrowSpacing
                ]
            ]
        return arg

    @property
    def surfacePlotInstruction(self):
        """ """
        return [
            "NAME:" + self.name,
            "SolutionName:=", self.solutionName,
            "QuantityName:=", self.quantityName,
            "PlotFolder:=", self.plotFolder,
            "UserSpecifyName:=", 0,
            "UserSpecifyFolder:=", 0,
            "StreamlinePlot:=", False,
            "AdjacentSidePlot:=", False,
            "FullModelPlot:=", False,
            "IntrinsicVar:=", self.intrinsicVar,
            "PlotGeomInfo:=", self.plotGeomInfo,
            "FilterBoxes:=", [0],
            self.plotsettings, "EnableGaussianSmoothing:=", False]


class PostProcessor(object):
    """PostProcessor class.
    
    This class contains all functionalities for managing main AEDT postprocess functions.
    The inherited ``AEDTConfig`` class contains all ``_desktop`` hierarchical calls 
    needed for the class inititialization data ``_desktop`` and the design types ``"HFSS"``,
    ``"Icepak"``, and ``"HFSS3DLayout"``.

    Parameters
    ----------
    parent: 
        Parent object, such as the AEDT application. The parent object must
        provide the members ``_modeler``, ``_desktop``, ``_odesign``, and ``_messenger``.
    """
    def __init__(self, parent):
        """ """"
        self._parent = parent
        self.FieldsPlot = {}

    @property
    def _primitives(self):
        """
        Returns
        -------
        str
           Model units, such as ``"mm"``.
        """
        return self._parent._modeler.primitives

    @property
    def model_units(self):
        """
        Returns
        -------
         str
           Model units, such as ``"mm"``.
        """
        return retry_ntimes(10, self.oeditor.GetModelUnits)

    @property
    def post_osolution(self):
        """
        Returns
        -------
        type
            Solutions module.
        """
        return self.odesign.GetModule("Solutions")

    @property
    def ofieldsreporter(self):
        """
        Returns
        -------
        type
        Fields Reporter module.
        """
        return self.odesign.GetModule("FieldsReporter")

    @property
    def oreportsetup(self):
        """
        Returns
        -------
        type
            Report Setup module.
        """
        return self.odesign.GetModule("ReportSetup")

    @property
    def post_solution_type(self):
        """
        Return
        ------
        type
            Design solution type.
            """
        try:
            return self.odesign.GetSolutionType()
        except:
            return self._parent._design_type


    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def desktop(self):
        """ """
        return self._parent._desktop

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def oproject(self):
        """ """
        return self._parent._oproject

    @property
    def modeler(self):
        """ """
        return self._parent._modeler

    @property
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def report_types(self):
        """ """
        return list(self.oreportsetup.GetAvailableReportTypes())

    @aedt_exception_handler
    def display_types(self, report_type):
        """

        Parameters
        ----------
        report_type :
            Type of the report.

        Returns
        -------
        type
            Report type.
        """
        return self.oreportsetup.GetAvailableDisplayTypes(report_type)

    # TODO: define a fields calculator module and make robust !!
    @aedt_exception_handler
    def volumetric_loss(self, object_name):
        """Create a new variable for volumetric losses using the field calculator.

        Parameters
        ----------
        object_name : str
            Name of the object on which to compute volumetric losses.

        Returns
        -------
        str
            Name of the variable created.

        """
        oModule = self.ofieldsreporter
        oModule.EnterQty("OhmicLoss")
        oModule.EnterVol(object_name)
        oModule.CalcOp("Integrate")
        name = "P_{}".format(object_name)  # Need to check for uniqueness !
        oModule.AddNamedExpression(name, "Fields")
        return name

    @aedt_exception_handler
    def change_field_property(self,plotname, propertyname, propertyval):
        """Edt a field property.

        Parameters
        ----------
        plotname : str
            Name of the plot.
        propertyname : str
            Name of the property to edit.   
        propertyval :
            New value for the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.odesign.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:FieldsPostProcessorTab",
                [
                    "NAME:PropServers",
                    "FieldsReporter:"+plotname
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:"+propertyname,
                        "Value:="	, propertyval
                    ]
                ]
            ]
        ])

    @aedt_exception_handler
    def export_field_file_on_grid(self, quantity_name, solution=None, variation_dict=None, filename=None,
                                  gridtype="Cartesian", grid_center=[0, 0, 0],
                                  grid_start=[0, 0, 0], grid_stop=[0, 0, 0], grid_step=[0, 0, 0], isvector = False, intrinsics=None, phase=None):
        """Create a new field file based on a specific solution and variation using the field calculator.

        Parameters
        ----------
        quantity_name : str
            Name of the quantity to export. For example, ``"Temp"``.
        solution : str, optional
            Name of the solution in the format ``solution : sweep``. The default is ``None``.
        variations_dict : dict, optional
            Dictionary of all variation variables with their values.
            The default is ``None``.
        filename : str, optional
            Full path and file name to which to save the file. 
            The default is ``None``.
        gridtype : str, optional
            Type of the grid to export. The default is ``"Cartesian"``.
        grid_center : list, optional
            Center of the grid. This parameter is disabled for the
            `"Cartesian"`` grid type. The default is a float list of three
            elements, ``[0, 0, 0]``.
        grid_start : list, optional
            Starting point of the grid. The default is a float list of three
            elements, ``[0, 0, 0]``.
        grid_stop : list, optional
            Stopping point of the grid. The default is a float list of three
            elements, ``[0, 0, 0]``.
        grid_step : list, optional
            Size of the step for the grid. The default is a float list of three
            elements, ``[0, 0, 0]``.
        isvector : bool, optional
            Whether the field is a vector. The  default is ``False``. 
        intrinsics : str, optional
            This parameter is mandatory for a frequency field 
            calculation. The default is ``None``.
        phase : str, optional
            Field phase. The default is ``None``.
   
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.messenger.add_info_message("Exporting {} Field. Be Patient".format(quantity_name))
        if not solution:
            solution = self._parent.existing_analysis_sweeps[0]
        if not filename:
            appendix = ""
            ext = ".fld"
            filename = os.path.join(self._parent.project_path, solution.replace(" : ", "_") + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.ofieldsreporter.CalcStack("clear")
        if isvector:
            self.ofieldsreporter.EnterQty(quantity_name)
            self.ofieldsreporter.CalcOp("Smooth")
            self.ofieldsreporter.EnterScalar(0)
            self.ofieldsreporter.CalcOp("AtPhase")
            self.ofieldsreporter.CalcOp("Mag")
        else:
            self.ofieldsreporter.EnterQty(quantity_name)
        obj_list = "AllObjects"
        self.ofieldsreporter.EnterVol(obj_list)
        self.ofieldsreporter.CalcOp("Mean")
        units=self.modeler.model_units
        ang_units="deg"
        if gridtype == "Cartesian":
            grid_center =["0mm", "0mm", "0mm"]
            grid_start_wu = [str(i)+units for i in grid_start]
            grid_stop_wu = [str(i)+units for i in grid_stop]
            grid_step_wu = [str(i)+units for i in grid_step]
        elif gridtype == "Cylinidrical":
            grid_center = [str(i)+units for i in grid_center]
            grid_start_wu = [str(grid_start[0])+units, str(grid_start[1])+ang_units, str(grid_start[2])+units]
            grid_stop_wu = [str(grid_stop[0])+units, str(grid_stop[1])+ang_units, str(grid_stop[2])+units]
            grid_step_wu = [str(grid_step[0])+units, str(grid_step[1])+ang_units, str(grid_step[2])+units]
        elif gridtype == "Spherical":
            grid_center = [str(i)+units for i in grid_center]
            grid_start_wu = [str(grid_start[0])+units, str(grid_start[1])+ang_units, str(grid_start[2])+ang_units]
            grid_stop_wu = [str(grid_stop[0])+units, str(grid_stop[1])+ang_units, str(grid_stop[2])+ang_units]
            grid_step_wu = [str(grid_step[0])+units, str(grid_step[1])+ang_units, str(grid_step[2])+ang_units]
        else:
            self._parent._messenger.add_error_message("Error in Type of Grid")
            return False
        if not variation_dict:
            variation_dict = self._parent.available_variations.nominal_w_values
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")


        self.ofieldsreporter.ExportOnGrid(filename, grid_start_wu,
                                          grid_stop_wu, grid_step_wu,
                                          solution,
                                          variation_dict, True, gridtype, grid_center, False)
        return os.path.exists(filename)


    @aedt_exception_handler
    def export_field_file(self, quantity_name, solution=None, variation_dict=None, filename=None,
                          obj_list="AllObjects", obj_type="Vol", intrinsics=None, phase=None,
                          sample_points_file=None, sample_points_lists=None, export_with_sample_points=True):
        """Create a new field file based on a specific solution and variation using the field calculator.

        Parameters
        ----------
        quantity_name :
            Name of the quantity to export. For example, ``"Temp"``.
        solution :
            Name of the solution  in the format ``solution: sweep``. The default is ``None``.
        variation_dict : dict, optional
            Dictionary of all variation variables with their values,
            The default is ``None``.
        filename : str, optional
            Full path and file name to which to save the file. 
            The default is ``None``.
        obj_list : list, optional
            List of objects to export. The default is ``"AllObjects"``.
        obj_type : str, optional
            Type of objects to export. Options are ``"Vol"`` for volume and 
            ``"Surf"`` for surface. The default is ``"Vol"``.
        intrinsics : str, optional
            This parameter is mandatory for a frequency or transient field 
            calculation. The default is ``None``.
        phase : str, optional
            Field phase. The default is ``None``.
        sample_points_file : str, optional
            Name of a file with sanmple points. The default is ``None``.
        sample_points_lists : list, optional
            List of sample  points. The default is ``None``.
        export_with_sample_points : bool, optional
            Whether to include sample points in the file to export.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.messenger.add_info_message("Exporting {} Field. Be Patient".format(quantity_name))
        if not solution:
            solution = self._parent.existing_analysis_sweeps[0]
        if not filename:
            appendix = ""
            ext = ".fld"
            filename = os.path.join(self._parent.project_path, solution.replace(" : ","_") + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.ofieldsreporter.CalcStack("clear")
        self.ofieldsreporter.EnterQty(quantity_name)


        if not variation_dict:
            if not sample_points_file and not sample_points_lists:
                if obj_type == "Vol":
                    self.ofieldsreporter.EnterVol(obj_list)
                elif obj_type == "Surf":
                    self.ofieldsreporter.EnterSurf(obj_list)
                else:
                    self.messenger.add_error_message("No correct choice")
                    return False
                self.ofieldsreporter.CalcOp("Value")
                variation_dict = self._parent.available_variations.nominal_w_values
            else:
                variations = self._parent.available_variations.nominal_w_values_dict
                variation_dict = []
                for el, value in variations.items():
                    variation_dict.append(el+":=")
                    variation_dict.append(value)
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")
        if not sample_points_file and not sample_points_lists:

            self.ofieldsreporter.CalculatorWrite(filename, ["Solution:="	, solution], variation_dict)
        elif sample_points_file:

            self.ofieldsreporter.ExportToFile(filename, sample_points_file, solution, variation_dict, export_with_sample_points)
        else:
            sample_points_file = os.path.join(self._parent.project_path, "temp_points.pts")
            with open(sample_points_file, "w") as f:
                for point in sample_points_lists:
                    f.write(" ".join([str(i) for i in point])+"\n")
            self.ofieldsreporter.ExportToFile(filename, sample_points_file, solution, variation_dict, export_with_sample_points)

        return os.path.exists(filename)


    @aedt_exception_handler
    def export_field_plot(self, plotname, filepath, filename=""):
        """Export a field plot.

        Parameters
        ----------
        plotname : str
            Name of the plot.
            
        filepath : str
            Path to the where the file is to be saved.
            
        filename : str, optional
            Name of the file. The default is ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not filename:
            filename = plotname
        self.ofieldsreporter.ExportFieldPlot(plotname, False, os.path.join(filepath, filename + ".aedtplt"))
        return os.path.join(filepath, filename+".aedtplt")

    @aedt_exception_handler
    def _create_fieldplot(self, objlist, quantityName, setup_name, intrinsincList, objtype, listtype):
        """Internal function

        Parameters
        ----------
        objlist : list
            List of fields to plot.  
        quantityName : str
            Name of the field plot.
        setup_name :
            Name of the setup in the format ``"setupName : sweepName"``. 
        intrinsincList :
            
        objtype :
            
        listtype :
            

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not setup_name:
            setup_name = self._parent.existing_analysis_sweeps[0]
        self.desktop.CloseAllWindows()
        self.oproject.SetActiveDesign(self.odesign.GetName())
        self.oeditor.FitAll()
        char_set = string.ascii_uppercase + string.digits
        uName = quantityName + '_' + ''.join(random.sample(char_set, 6))
        plot = FieldPlot(self.ofieldsreporter, objlist, setup_name, quantityName, intrinsincList)
        plot.name = uName
        plot.objtype = objtype
        plot.listtype = listtype
        plt = plot.create()
        if plt:
            self.FieldsPlot[uName] = plot
            return plot
        else:
            return False

    @aedt_exception_handler
    def create_fieldplot_surface(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """Create a field plot of surfaces.

        Parameters
        ----------
        objlist : list
            List of surfaces to include in the plot.
        quantityName : str
            Name of the quantity to plot.
        setup_name :
            Name of the setup in the format ``"setupName : sweepName"``. The default 
            is ``None``.
        intrinsincDict :
            Dictionary containing all intrinsic variables. The default 
            is ``{}``.

        Returns
        -------
        type
            Plot object.

        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Surface", "FacesList")
        return plot

    @aedt_exception_handler
    def create_fieldplot_cutplane(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """Create a field plot of cut planes.

        Parameters
        ----------
        objlist : list
            List of cut planes to include in the plot.
        quantityName : str
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format ``"setupName : sweepName"``. The default 
            is ``None``, in which case ``nominal, lastadaptive`` is applied.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables. The default 
            is ``{}``.

        Returns
        -------
        type
            Plot object.

        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Surface", "CutPlane")
        return plot

    @aedt_exception_handler
    def create_fieldplot_volume(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """Create field plot of volumes.

        Parameters
        ----------
        objlist : list
            list of volumnes to include in the plot.
        quantityName :
            Name of the quantity to plot.
        setup_name : str, optional
            Name of the setup in the format ``"setupName : sweepName"``. The default 
            is ``None``, in which case ``nominal, lastadaptive`` is applied.
        intrinsincDict : dict, optional
            Dictionary containing all intrinsic variables. The default 
            is ``{}``.
        
        Returns
        -------
        type
            Plot object
        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Volume", "ObjList")
        return plot

    @aedt_exception_handler
    def export_field_jpg(self, fileName, plotName, coordinateSystemName):
        """Export the plot for a given plot name and coordinate system name to a JPG file.

        Parameters
        ----------
        fileName : str
            Full path and file name for the JPG file.
        plotName : str
            Name of the plot.
        coordinateSystemName :str
            Name of the coordinate system.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        time.sleep(2)

        self.ofieldsreporter.ExportPlotImageToFile(fileName, "", plotName, coordinateSystemName)
        return True

    @aedt_exception_handler
    def export_field_image_with_View(self, plotName, exportFilePath, view="iso", wireframe=True):
        """Export a field plot image with a view.
        
        ..note::
          For AEDT 2019.3, this function works only on the ISO view due to a bug in the API.
          The function works properly in 2021 R1.

        Parameters
        ----------
        plotName : str
            Name of the plot.
        exportFilePath :
            Path to where to export the image file.
        view : str, optional
            View to export. Options are``"iso"``, ``"XZ"``, ``"XY"``, and ``"YZ"``. 
            The default is ``"iso"``.
        wireframe : bool, optional
            Whether objects must be put in the wireframe mode. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        bound = self.modeler.get_model_bounding_box()
        center = [(float(bound[0]) + float(bound[3])) / 2,
                  (float(bound[1]) + float(bound[4])) / 2,
                  (float(bound[2]) + float(bound[5])) / 2]
        coordinateSystemForExportPlot = self.modeler.create_coordinate_system(origin=center, mode='view', view=view)
        wireframes = []
        if wireframe:
            names = self._primitives.get_all_objects_names()
            for el in names:
                if not self._primitives[el].wireframe:
                    wireframes.append(el)
                    self._primitives[el].display_wireframe = True
        status = self.export_field_jpg(exportFilePath, plotName, coordinateSystemForExportPlot.name)
        for solid in wireframes:
            self._primitives[solid].display_wireframe = False
        coordinateSystemForExportPlot.delete()
        return status

    @aedt_exception_handler
    def delete_field_plot(self, name):
        """Delete a field plot.

        Parameters
        ----------
        name : str
            The name of the field plot to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.oreportsetup.DeleteFieldPlot([name])
        self.FieldsPlot.pop(name, None)
        return True

    @aedt_exception_handler
    def export_model_picture(self, dir, name, picturename="Model", ShowAxis=True, ShowGrid=True, ShowRuler=True):
        """Export a snapshot of the model to a JPG file. 
        
        ..note::
        The function works only in graphical mode.
        
        Parameters
        ----------
        dir : str
            Path to where the JPG file is to be exported.
        name : str
            Name of the project, which is used to compose the directory path.
        picturename : str, optional
            Name of the JPG file. The default is ``"Model"``. The extension
            ``".jpg"`` is automatically added.
        ShowAxis : bool, optional
            Whether to show the axes. The default is ``True``.
        ShowGrid : bool, optional
            Whether to show the grid. The default is ``True``.
        ShowRuler : bool, optional
            Whether to show the ruler. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        # Setup arguments list for createReport function
        if not os.path.exists(dir + "//" + name):
            os.mkdir(dir + "//" + name)
        if not os.path.exists(dir + "//" + name + "//Pictures"):
            os.mkdir(dir + "//" + name + "//Pictures")

        # open the 3D modeler and remove the selection on other objects
        self.oeditor.ShowWindow()
        self.steal_focus_oneditor()
        self.oeditor.FitAll()
        # export the image
        arg = ["NAME:SaveImageParams", "ShowAxis:=", ShowAxis, "ShowGrid:=", ShowGrid, "ShowRuler:=", ShowRuler,
               "ShowRegion:=", "Default", "Selections:=", ""]
        self.oeditor.ExportModelImageToFile(dir + "//" + name + "//Pictures//" + picturename + ".jpg", 0, 0,
                                             arg)
        return True

    @aedt_exception_handler
    def copy_report_data(self, PlotName):
        """Copy report data as static data.

        Parameters
        ----------
        PlotName :
            Name of the report.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oreportsetup.CopyReportsData([PlotName])
        self.oreportsetup.PasteReports()
        return True

    @aedt_exception_handler
    def delete_report(self, PlotName):
        """Delete a report.

        Parameters
        ----------
        PlotName : str
            Name of the report.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        self.oreportsetup.DeleteReports([PlotName])
        return True

    @aedt_exception_handler
    def rename_report(self, PlotName, newname):
        """Rename a report

        Parameters
        ----------
        PlotName : str
            Name of the report.
        newname : str
            New name of the report.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        self.oreportsetup.RenameReport(PlotName, newname)
        return True


    @aedt_exception_handler
    def export_report_to_csv(self, ProjectDir, PlotName):
        """Export the SParameter plot data to a CSV file.
        
        This function leaves the data in the plot (as data) as a reference 
        for the Sparameters plot after the loops.

        Parameters
        ----------
        ProjectDir : str
            Path to the project directory.
        PlotName : str
            Name of the plot to export.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.)
        """
        # path
        npath = os.path.normpath(ProjectDir)
        # set name for the csv file

        csvFileName = os.path.join(npath, PlotName+".csv")
        # export the csv
        self.oreportsetup.ExportToFile(PlotName, csvFileName)
        return True

    @aedt_exception_handler
    def export_report_to_jpg(self, ProjectDir, PlotName):
        """Export the SParameter plot as an image

        Parameters
        ----------
        ProjectDir : str
            Path to the project directory.
        PlotName : str
            Name of the plot to export.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        # path
        npath = os.path.normpath(ProjectDir)
        # set name for the plot image file
        jpgFileName = os.path.join(npath, PlotName+".jpg")

        self.oreportsetup.ExportImageToFile(PlotName, jpgFileName, 0, 0)
        return True

    @aedt_exception_handler
    def get_far_field_data(self, expression="GainTotal", setup_sweep_name='', domain="Infinite Sphere1", families_dict=None):
        """Generate far field data using the ``GetSolutionDataPerVariation`` function. 
        
        This function returns the data ``solData``, ``ThetaVals``, ``PhiVals``, ``ScanPhiVals,`` 
        ``ScanThetaVals,`` and ``FreqVals``.

        Parameters
        ----------
        expression : str or list, optional
            One or more formulas to add to the report. The default is ``"GainTotal"``.
        setup_sweep_name : str, optional
            Name of the setup to use to compute the report. The default is ``""``, 
            which means that the nominal sweep is to be applied. 
        domain : str, optional
            Context type (sweep or time). The default is ``"Infinite Sphere1"``.
        families_dict : dict, optional
            Dictionary of variables and values. The default is``None``.  {"Freq": ["All"]}
        
        Returns
        -------
        type
            SolutionData object if successful.

        """
        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_adaptive
        if families_dict is None:
            families_dict = {"Theta": ["All"], "Phi": ["All"], "Freq": ["All"]}
        solution_data = self.get_solution_data_per_variation("Far Fields", setup_sweep_name, ['Context:=', domain], families_dict, expression)
        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @aedt_exception_handler
    def get_report_data(self, expression="dB(S(1,1))", setup_sweep_name='', domain='Sweep', families_dict=None, report_input_type=None):
        """Generate report data using the ``GetSolutionDataPerVariation`` function.
        
        This function returns the data object and the arrays ``solData`` and
        ``FreqVals``.
               
        Parameters
        ----------
        expression : str or list
            One or more formulas to add to the report. The default is ``dB(S(1,1))"``.
        setup_sweep_name : str
            Name of setup to use to compute the report. The default is ``""``, which means that the
            nominal sweep is to be applied.
        domain : str or list, optional
            Context type. The options are ``"Sweep"`` or ``"Time"``. The default is ``"Sweep".``
        families_dict : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}`.
        report_input_type :  optional
             Type of data :

        Returns
        -------
        SolutionData
            SolutionData object if successful

       Examples
       --------
            >>>hfss Sparameters
            >>>hfss = HFSS()
            >>>hfss.post.get_report_data("S(1,1)")   # it will take default sweep and default variation
        
        
            >>>m3d = Maxwell3D()
            >>>m3d.post.get_report_data("SurfaceLoss")   #Eddy Current examples
            >>>m3d.post.get_report_data("Wind(LoadA,LaodA)")    #TransientAnalsysis

        """
        if self.post_solution_type == "3DLayout" or self.post_solution_type == "NexximLNA" or self.post_solution_type == "NexximTransient":
            if domain == "Sweep":
                did = 3
            else:
                did = 1
            ctxt = ["NAME:Context", "SimValueContext:=",
                    [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]]
        elif type(domain) is list:
            ctxt = domain
        else:
            ctxt = ["Domain:=", domain]

        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep


        if not report_input_type:
            report_input_type = report_type[self.post_solution_type]


        if families_dict is None:
            families_dict = {"Freq": ["All"]}

        solution_data = self.get_solution_data_per_variation(report_input_type, setup_sweep_name, ctxt, families_dict, expression)

        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @aedt_exception_handler
    def create_rectangular_plot(self, expression="dB(S(1,1))", setup_sweep_name='', families_dict={"Freq": ["All"]},
                                primary_sweep_variable="Freq", context=None, plotname=None,plottype=None):
        """Create a 2D rectangular plot in AEDT.

        Parameters
        ----------
        expression : str or list, optional
            One or more formulas to add to the report. The default is value = ``"dB(S(1,1))"``.
        setup_sweep_name :
            setup name with sweep (Default value = '')
        families_dict : dict, optional
            Dictionary of all families including the primary sweep. The default is ``{"Freq": ["All"]}`.
        primary_sweep_variable : str, optional
            Name of the primary sweep. The default is ``"Freq"``.
        context : str, optional
            The default is ``None``.
        plotname : str, optional
            Name of the plot. The The default is ``None``. 

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        ctxt=[]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep
        if self.post_solution_type == "HFSS 3D Layout Design" or self.post_solution_type == "NexximLNA" or self.post_solution_type == "NexximTransient":
            if "Freq" == primary_sweep_variable or "Freq" in list(families_dict.keys()):
                did = 3
            else:
                did = 1
            ctxt = ["NAME:Context", "SimValueContext:=",
                    [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]]
        elif context:
            if type(context) is  list:
                ctxt = context
            else:
                ctxt = ["Context:=", context]

        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep
        if self.post_solution_type not in report_type:
            print("Solution not supported")
            return False
        if not plottype:
            modal_data = report_type[self.post_solution_type]
        else:
            modal_data = plottype
        if not plotname:
            plotname = generate_unique_name("Plot")
        families_input = []
        families_input.append(primary_sweep_variable+":=")
        if not primary_sweep_variable in list(families_dict.keys()):
            families_input.append(["All"])
        elif type(families_dict[primary_sweep_variable]) is list:
            families_input.append(families_dict[primary_sweep_variable])
        else:
            families_input.append([families_dict[primary_sweep_variable]])
        for el in families_dict:
            if el == primary_sweep_variable:
                continue
            families_input.append(el+":=")
            if type(families_dict[el]) is list:
                families_input.append(families_dict[el])
            else:
                families_input.append([families_dict[el]])



        self.oreportsetup.CreateReport(plotname, modal_data, "Rectangular Plot", setup_sweep_name, ctxt, families_input,
                                                       ["X Component:=", primary_sweep_variable, "Y Component:=",
                                                   expression])

        return True

    @aedt_exception_handler
    def get_solution_data_per_variation(self, soltype='Far Fields', setup_sweep_name='', ctxt=None,
                                        sweeps=None, expression=''):
        """Retrieve solution data for each variation.

        Parameters
        ----------
        soltype : str, optional
            Type of the solution. For example, ``"Far Fields"`` or ``"Modal Solution Data"``. The default
            is ``"Far Fields"``.
        setup_sweep_name : str, optional
            Name of setup to use to compute the report. The default is ``''``, in which case nominal 
            adaptive is applied.
        ctxt : list, optional
            List of context variables. The default is ``None``.
        sweeps : dict, optional
            Dictionary of variables and values. The default is ``None``, in which case this list is used: 
            ``{'Theta': 'All', 'Phi': 'All', 'Freq': 'All'}``
        expression : str or list, optional
            One or more traces to include. The default is ``''``.

        Returns
        -------
        type
            Solution data.

        """
        if sweeps is None:
            sweeps = {'Theta': 'All', 'Phi': 'All', 'Freq': 'All'}
        if not ctxt:
            ctxt = []
        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_adaptive
        sweep_list=[]
        for el in sweeps:
            sweep_list.append(el+":=")
            if type(sweeps[el]) is list:
                sweep_list.append(sweeps[el])
            else:
                sweep_list.append([sweeps[el]])



        data = self.oreportsetup.GetSolutionDataPerVariation(soltype, setup_sweep_name, ctxt, sweep_list, expression)
        return SolutionData(data)

    @aedt_exception_handler
    def steal_focus_oneditor(self):
        """Remove the selection of an object that would prevent the image from exporting correctly.

        Parameters
        ----------

        Returns
        -------

        """
        self.desktop.RestoreWindow()
        param = ["NAME:SphereParameters", "XCenter:=", "0mm", "YCenter:=", "0mm", "ZCenter:=", "0mm", "Radius:=", "1mm"]
        attr = ["NAME:Attributes", "Name:=", "DUMMYSPHERE1", "Flags:=", "NonModel#"]
        self.oeditor.CreateSphere(param, attr)
        self.oeditor.Delete(["NAME:Selections", "Selections:=", "DUMMYSPHERE1"])
        return True
