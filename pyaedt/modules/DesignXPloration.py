from collections import OrderedDict
from pyaedt.generic.general_methods import pyaedt_function_handler, generate_unique_name
from pyaedt.generic.DataHandlers import _dict2arg, _arg2dict
import copy

defaultparametricSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "Sweeps": OrderedDict(
            {"SweepDefinition": OrderedDict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}
        ),
        "Sweep Operations": OrderedDict(),
        "Goals": OrderedDict(),
    }
)


defaultdxSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "Sweeps": OrderedDict(
            {"SweepDefinition": OrderedDict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}
        ),
        "Sweep Operations": OrderedDict(),
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": OrderedDict(),
        "EmbeddedParamSetup": -1,
        "Goals": OrderedDict(),
    }
)

defaultoptiSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Optimizer": "Quasi Newton",
        "AnalysisStopOptions": OrderedDict(
            {
                "StopForNumIteration": True,
                "StopForElapsTime": False,
                "StopForSlowImprovement": False,
                "StopForGrdTolerance": False,
                "MaxNumIteration": 1000,
                "MaxSolTimeInSec": 3600,
                "RelGradientTolerance": 0,
                "MinNumIteration": 10,
            }
        ),
        "CostFuncNormType": "L2",
        "PriorPSetup": "",
        "PreSolvePSetup": True,
        "Variables": OrderedDict(),
        "LCS": OrderedDict(),
        "Goals": OrderedDict(),
        "Acceptable_Cost": 0,
        "Noise": 0.0001,
        "UpdateDesign": False,
        "UpdateIteration": 5,
        "KeepReportAxis": True,
        "UpdateDesignWhenDone": True,
    }
)

defaultsensitivitySetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "MaxIterations": 10,
        "PriorPSetup": "",
        "PreSolvePSetup": True,
        "Variables": OrderedDict(),
        "LCS": OrderedDict(),
        "Goals": OrderedDict(),
        "Primary Goal": 0,
        "PrimaryError": 0.0001,
        "Perform Worst Case Analysis": False,
    }
)

defaultstatisticalSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "MaxIterations": 50,
        "SeedValue": 0,
        "PriorPSetup": "",
        "Variables": OrderedDict(),
        "Goals": OrderedDict(),
    }
)

defaultdoeSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": OrderedDict(),
        "Variables": OrderedDict(),
        "Goals": OrderedDict(),
        "DesignExprData": OrderedDict(
            {
                "Type": "kOSF",
                "CCDDeignType": "kFaceCentered",
                "CCDTemplateType": "kStandard",
                "LHSSampleType": "kCCDSample",
                "RamdomSeed": 0,
                "NumofSamples": 10,
                "OSFDeignType": "kOSFD_MAXIMINDIST",
                "MaxCydes": 10,
            }
        ),
        "RespSurfaceSetupData": OrderedDict({"Type": "kGenAggr", "RefineType": "kManual"}),
        "ResponsePoints": OrderedDict({"NumOfStrs": 0}),
        "ManualRefinePoints": OrderedDict({"NumOfStrs": 0}),
        "CustomVerifyPoints": OrderedDict({"NumOfStrs": 0}),
        "Tolerances": [],
    }
)


class CommonOptimetrics(object):
    """Creates and sets up optimizations.

    Parameters
    ----------
    p_app :

    name :

    dictinputs

    optimtype : str
        Type of the optimization.

    """

    def __init__(self, p_app, name, dictinputs, optimtype):
        self._app = p_app
        self.omodule = self._app.ooptimetrics
        self.name = name
        self.soltype = optimtype

        inputd = copy.deepcopy(dictinputs)

        if optimtype == "OptiParametric":
            self.props = inputd or copy.deepcopy(defaultparametricSetup)
        if optimtype == "OptiDesignExplorer":
            self.props = inputd or copy.deepcopy(defaultdxSetup)
        if optimtype == "OptiOptimization":
            self.props = inputd or copy.deepcopy(defaultoptiSetup)
        if optimtype == "OptiSensitivity":
            self.props = inputd or copy.deepcopy(defaultsensitivitySetup)
        if optimtype == "OptiStatistical":
            self.props = inputd or copy.deepcopy(defaultstatisticalSetup)
        if optimtype == "OptiDXDOE":
            self.props = inputd or copy.deepcopy(defaultdoeSetup)

        if inputd:
            self.props.pop("ID", None)
            self.props.pop("NextUniqueID", None)
            self.props.pop("MoveBackwards", None)
            self.props.pop("GoalSetupVersion", None)
            self.props.pop("Version", None)
            self.props.pop("SetupType", None)
            if inputd.get("Sim. Setups"):
                setups = inputd["Sim. Setups"]
                for el in setups:
                    if type(self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]) is list:
                        for setup in self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]:
                            if setup["I"] == el:
                                setups[setups.index(el)] = setup["I"]
                                break
                    else:
                        if self._app.design_properties["SolutionManager"]["ID Map"]["Setup"]["I"] == el:
                            setups[setups.index(el)] = self._app.design_properties["SolutionManager"]["ID Map"][
                                "Setup"
                            ]["N"]
                            break
            if inputd.get("Goals", None):
                if self._app._is_object_oriented_enabled():
                    oparams = self.omodule.GetChildObject(self.name).GetCalculationInfo()
                    oparam = [i for i in oparams[0]]
                    calculation = ["NAME:Goal"]
                    calculation.extend(oparam)
                    arg1 = OrderedDict()
                    _arg2dict(calculation, arg1)
                    self.props["Goals"] = arg1

    @pyaedt_function_handler()
    def update(self, update_dictionary=None):
        """Update the setup based on stored properties.

        Parameters
        ----------
        update_dictionary : dict, optional
            Dictionary to use. The  default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditSetup
        """
        if update_dictionary:
            for el in update_dictionary:
                self.props[el] = update_dictionary[el]

        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)

        self.omodule.EditSetup(self.name, arg)
        return True

    @pyaedt_function_handler()
    def create(self):
        """Create a setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.InsertSetup
        """
        arg = ["NAME:" + self.name]
        _dict2arg(self.props, arg)
        self.omodule.InsertSetup(self.soltype, arg)
        return True

    @pyaedt_function_handler()
    def _add_calculation(
        self,
        reporttype,
        solution=None,
        domain="Sweep",
        calculation="",
        calculation_type="d",
        calculation_value="",
        calculation_name=None,
    ):
        """Add a calculation to the setup.

        Parameters
        ----------
        reporttype : str
            Type of report.
        solution : str, optional
            Type of the solution. The default is ``None``.
        domain : str, optional
             Type of the domain. The default is ``"Sweep"``.
        calculation : str, optional
             The default is ``""``.
        calculation_type : str, optional
             Type of the calculaton. The default is ``"d"``.
        calculation_value : str, optional
             The default is ``""``.
        calculation_name : str, optional
             Name of the the calculation. The default is ``None``.

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        if calculation_name:
            sweepdefinition["Name"] = calculation_name
        else:
            sweepdefinition["Name"] = generate_unique_name(calculation)
        if domain == "Sweep":
            var = "Freq"
        else:
            var = "Time"
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", var, "Type:=", calculation_type, "DiscreteValues:=", calculation_value]}
        )
        if "Goal" in self.props["Goals"]:
            if type(self.props["Goals"]["Goal"]) is not list:
                self.props["Goals"]["Goal"] = [self.props["Goals"]["Goal"], sweepdefinition]
            else:
                self.props["Goals"]["Goal"].append(sweepdefinition)
        else:
            self.props["Goals"]["Goal"] = sweepdefinition

        return self.update()

    @pyaedt_function_handler()
    def _add_goal(
        self,
        optigoalname,
        reporttype,
        solution=None,
        domain="Sweep",
        calculation="",
        calculation_type="discrete",
        calc_val1="",
        calc_val2="",
        condition="==",
        goal_value=1,
        goal_weight=1,
        goal_name=None,
    ):
        """Add an optimization goal to the setup.

        Parameters
        ----------
        optigoalname : str
            Name of the optimization goal.
        reporttype : str, optional
            Type of the report.
        solution : str, optional
            Type of the solution. The default is ``None``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"''.
        calculation : str, optional
            Name of the calculation. The default is ``""``.
        calculation_type : str, optional
            Type of the calculation. The default is ``"discrete"``.
        calc_val1 : str, optional
            First value for the calculation. The default is ``""``.
        calc_val2 : str, optional
            Second value for the calculation. The default is ``""``.
        condition : str, optional
            The condition for the calculation. The default is ``"=="``.
        goal_value : optional
            Value for the optimization goal. The default is ``1``.
        goal_weight : optional
            Weight for the optimzation goal. The default is ``1``.
        goal_name : str, optional
            Name of the goal. The default is ``None``.

        Returns
        -------

        """
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        if goal_name:
            sweepdefinition["Name"] = goal_name
        else:
            sweepdefinition["Name"] = generate_unique_name(calculation)
        if domain == "Sweep":
            var = "Freq"
        else:
            var = "Time"
        if calculation_type == "discrete":
            if type(calc_val1) is list:
                dr = ",".join(calc_val1)
            else:
                dr = calc_val1
            sweepdefinition["Ranges"] = OrderedDict({"Range": ["Var:=", var, "Type:=", "d", "DiscreteValues:=", dr]})
        else:
            sweepdefinition["Ranges"] = OrderedDict(
                {
                    "Range": [
                        "Var:=",
                        var,
                        "Type:=",
                        calculation_type,
                        "Start:=",
                        calc_val1,
                        "Stop:=",
                        calc_val2,
                        "DiscreteValues:=",
                        "",
                    ]
                }
            )
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]}
        )
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        if "Goal" in self.props[optigoalname]:
            if type(self.props[optigoalname]["Goal"]) is not list:
                self.props[optigoalname]["Goal"] = [self.props[optigoalname]["Goal"], sweepdefinition]
            else:
                self.props[optigoalname]["Goal"].append(sweepdefinition)
        else:
            self.props[optigoalname]["Goal"] = sweepdefinition
        return self.update()


class DXSetups(object):
    """Sets up DesignXplorer optimizations.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> dx_setup = app.opti_designxplorer
    """

    class Setup(CommonOptimetrics, object):
        """Sets up a DesignXplorer optimization in optiSLang.

        Parameters
        ----------
        app :
        name :
        dictinputs :
            The default is ``None``.
        optimtype : str, optional
            Type of the optimization. The default is ``"OptiDesignExplorer"``.

        """

        def __init__(self, app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, app, name, dictinputs=dictinputs, optimtype="OptiDesignExplorer")

        @pyaedt_function_handler()
        def add_calculation(
            self,
            calculation="",
            calculation_value="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            calculation_name=None,
        ):
            """Add a calculation to the setup.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            calculation_name : str, optional
                 Name of the calculation. The default is ``None``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_calculation(
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type="d",
                calculation=calculation,
                calculation_value=calculation_value,
                calculation_name=calculation_name,
            )

        @pyaedt_function_handler()
        def add_goal(
            self,
            calculation="",
            calculation_value="",
            calculation_type="discrete",
            calculation_stop="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            goal_name=None,
            goal_value=1,
            goal_weight=1,
            condition="==",
        ):
            """Add a goal to the setup.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
                If ``calculation_type="discrete"``, the value is discrete or is a list. If the
                value is a range, it is the starting value.
            calculation_type : str, optional
                Type of the calculation. Options are ``"discrete"`` or ``"range"``.
                The default is ``"discrete"``.
            calculation_stop : str, optional
                Stopping value for the calculation if ``calculation_type="range"``.
                The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            goal_name : str, optional
                 Name of the goal. The default is ``None``.
            goal_value : optional
                 Value for the goal. The default is ``1``.
            goal_weight : optional
                 Value for the goal weight. The default is ``1``.
            condition : string, optional
                 The default is ``"=="``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_goal(
                optigoalname="CostFunctionGoals",
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type=calculation_type,
                calculation=calculation,
                calc_val1=calculation_value,
                calc_val2=calculation_stop,
                goal_name=goal_name,
                goal_weight=goal_weight,
                goal_value=goal_value,
                condition=condition,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        type(setups_data[data]) is OrderedDict
                        and setups_data[data]["SetupType"] == "OptiDesignExplorer"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_dx_setup(self, variables_to_include, defaults_var_values=None, setupname=None, parametricname=None):
        """Add a basic parametric setup in DesignXplorer.

        You can customize all DesignXplorer options after the setup is added.

        Parameters
        ----------
        variables_to_include : list
            List of variables to include in DesignXplorer.
        defaults_var_values : list, optional
            List of default variable values.
        setupname : str, optional
            Name of the setup. The default is ``None``, in which case the default
            analysis setup is used.
        parametricname : str, optional
            Name of the parametric setup. The default is ``None``.

        Returns
        -------
        :class:`Optimetrics`

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not setupname:
            setupname = [self._app.analysis_setup]
        elif type(setupname) is not list:
            setupname = [setupname]
        if not parametricname:
            parametricname = generate_unique_name("DesignXplorer")
        setup = self.Setup(self._app, parametricname)
        setup.props["Sim. Setups"] = setupname
        setup.props["Sweeps"] = []
        if not defaults_var_values:
            for v in variables_to_include:
                sweepdefinition = OrderedDict()
                sweepdefinition["Variable"] = v
                if "$" in v:
                    sweepdefinition["Data"] = self._app.oproject.GetVariableValue(v)
                else:
                    sweepdefinition["Data"] = self._app._odesign.GetVariableValue(v)
                sweepdefinition["OffsetF1"] = False
                sweepdefinition["Synchronize"] = 0
        else:
            for v, vv in zip(variables_to_include, defaults_var_values):
                sweepdefinition = OrderedDict()
                sweepdefinition["Variable"] = v
                sweepdefinition["Data"] = vv
                sweepdefinition["OffsetF1"] = False
                sweepdefinition["Synchronize"] = 0
                setup.props["Sweeps"].append(sweepdefinition)
                setup.props["StartingPoint"][v] = vv
        setup.create()
        self.setups.append(setup)
        return setup


class ParametericsSetups(object):
    """Sets up parametric analyses.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> parametric_setup = app.opti_parametric
    """

    class Setup(CommonOptimetrics, object):

        """Sets up a parametric analysis in optiSLang.

        Parameters
        ----------
        p_app : str
            Inherited AEDT object.

        name :

        dictinputs : optional
            The default is ``None``.
        otimtype : str, optional
            Type of the optimization. The default is ``"OptiParametric"``.

        """

        def __init__(self, p_app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype="OptiParametric")
            pass

        @pyaedt_function_handler()
        def add_variation(self, sweep_var, datarange):
            """Add a variation to an existing parametric setup.

            Parameters
            ----------
            sweep_var : str
                Name of the variable.
            datarange :
                Range of the data.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            if type(self.props["Sweeps"]["SweepDefinition"]) is not list:
                self.props["Sweeps"]["SweepDefinition"] = [self.props["Sweeps"]["SweepDefinition"]]
            sweepdefinition = OrderedDict()
            sweepdefinition["Variable"] = sweep_var
            sweepdefinition["Data"] = datarange
            sweepdefinition["OffsetF1"] = False
            sweepdefinition["Synchronize"] = 0
            self.props["Sweeps"]["SweepDefinition"].append(sweepdefinition)
            self.update()
            return True

        @pyaedt_function_handler()
        def add_calculation(
            self,
            calculation="",
            calculation_value="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            calculation_name=None,
        ):
            """Add a calculation to the parametric setup.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            calculation_name : str, optional
                Name of the calculation. The default is ``None``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_calculation(
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type="d",
                calculation=calculation,
                calculation_value=calculation_value,
                calculation_name=calculation_name,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]

                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiParametric"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_parametric_setup(self, sweep_var, datarange, setupname=None, parametricname=None):
        """Add a basic parametric setup.

        You can customize all options after the parametric setup is added.

        Parameters
        ----------
        sweep_var : str
            Name of the sweep.
        datarange :
            Range of the data.
        setupname : str, optional
            Name of the setup. The default is ``None``, in which case  the default
            parametric setup is used.
        parametricname : str, optional
            Name of the parametric setup. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.DesignXPloration.ParametericsSetups.Optimetrics`
            Optimetrics object.

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not setupname:
            setupname = [self._app.analysis_setup]
        elif type(setupname) is not list:
            setupname = [setupname]
        if not parametricname:
            parametricname = generate_unique_name("Parametric")
        setup = self.Setup(self._app, parametricname)
        setup.props["Sim. Setups"] = setupname
        sweepdefinition = OrderedDict()
        sweepdefinition["Variable"] = sweep_var
        sweepdefinition["Data"] = datarange
        sweepdefinition["OffsetF1"] = False
        sweepdefinition["Synchronize"] = 0
        setup.props["Sweeps"]["SweepDefinition"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class SensitivitySetups(object):
    """Sets up sensitivity analyses.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> sensitivity_setups = app.opti_sensitivity
    """

    class Setup(CommonOptimetrics, object):
        """Sets up a sensitivity analysis in optiSLang.

        Parameters
        ----------
        p_app :

        name :

        dictinputs : optional
            The default is ``None``.
        otimtype : str, optional
            Type of the optimization. The default is ``"OptiSensitivity"``.

        """

        def __init__(self, p_app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype="OptiSensitivity")

        @pyaedt_function_handler()
        def add_calculation(
            self,
            calculation="",
            calculation_value="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            calculation_name=None,
        ):
            """Add a calculation to the sensitivity analysis.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            calculation_name : str, optional
                Name of the calculation. The default is ``None``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_calculation(
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type="d",
                calculation=calculation,
                calculation_value=calculation_value,
                calculation_name=calculation_name,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiSensitivity"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_sensitivity(
        self,
        calculation,
        calculation_value,
        calculation_type="Freq",
        reporttype="Modal Solution Data",
        domain="Sweep",
        solution=None,
        parametricname=None,
    ):
        """Add a basic sensitivity analysis.

        You can customize all options after the analysis is added.

        Parameters
        ----------
        calculation : str, optional
            Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
        calculation_value : str, optional
            Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
        calculation_type : str, optional
            Type of variation. The default is ``"Freq"``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        parametricname : str, optional
            Name of the sensitivity analysis. The default is ``None``, in which case
            a default name is assigned.

        Returns
        -------
        :class:`Sensitivity`

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not parametricname:
            parametricname = generate_unique_name("Sensitivity")
        setup = self.Setup(self._app, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calculation_value]}
        )
        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class StatisticalSetups(object):
    """Sets up statistical analyses.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> statistical_setups = app.opti_statistical
    """

    class Setup(CommonOptimetrics, object):
        """Sets up a statistical analysis in optiSLang.

        Parameters
        ----------
        p_app :

        name :

        dictinputs : optional
            The default is ``None``.
        otimtype : str, optional
            Type of the optimization. The default is ``"OptiStatistical"``.

        """

        def __init__(self, p_app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype="OptiStatistical")
            pass

        @pyaedt_function_handler()
        def add_calculation(
            self,
            calculation="",
            calculation_value="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            calculation_name=None,
        ):
            """Add a calculation to the statistical analysis.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            calculation_name : str, optional
                Name of the calculation. The default is ``None``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_calculation(
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type="d",
                calculation=calculation,
                calculation_value=calculation_value,
                calculation_name=calculation_name,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiStatistical"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_statistical(
        self,
        calculation_name,
        calc_variation_value,
        calculation_type="Freq",
        reporttype="Modal Solution Data",
        domain="Sweep",
        solution=None,
        parametricname=None,
    ):
        """Add a basic statistical analysis.

        You can customize all options after the analysis is added.

        Parameters
        ----------
        calculation_name : str, optional
            Name of the calculation.
        calc_variation_value : str, optional
            Variation value, such as ``"1GHz"``.
        calculation_type : str, optional
            Variation type. The default is ``"Freq"``.
        reporttype : str, optional
            Type of report to add the calculation to. The default is
            ``"Modal Solution Data"``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``.
        solution : str, optional
            Name of the solution. The default is ``None``, in which case the
            nominal sweep is used.
        parametricname : str, optional
            Name of the analysis. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        :class:`Statistical`

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not parametricname:
            parametricname = generate_unique_name("Statistical")
        setup = self.Setup(self._app, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation_name
        sweepdefinition["Name"] = calculation_name
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calc_variation_value]}
        )
        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class DOESetups(object):
    """Sets up DOEs (Designs of Experiments).

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> doe_setups = app.opti_doe
    """

    class Setup(CommonOptimetrics, object):
        """Sets up a DOE (Design of Experiments) in optiSLang.

        Parameters
        ----------
        p_app : str
            Inherited AEDT object.
        name :

        dictinputs : optional
            The default is ``None``.
        otimtype : str, optional
            Type of the optimization. The default is ``"OptiDXDOE"``.

        """

        def __init__(self, p_app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype="OptiDXDOE")
            pass

        @pyaedt_function_handler()
        def add_calculation(
            self,
            calculation="",
            calculation_value="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            calculation_name=None,
        ):
            """Add a calculation to the DOE (Design of Experiments).

            Parameters
            ----------
            calculation : str, optional
               Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            calculation_name : str, optional
                Name of the calculation. The default is ``None``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_calculation(
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type="d",
                calculation=calculation,
                calculation_value=calculation_value,
                calculation_name=calculation_name,
            )

        @pyaedt_function_handler()
        def add_goal(
            self,
            calculation="",
            calculation_value="",
            calculation_type="discrete",
            calculation_stop="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            goal_name=None,
            goal_value=1,
            goal_weight=1,
            condition="==",
        ):
            """Add a goal to the DOE (Design of Experiments).

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
                If ``calculation_type="discrete"``, the value is discrete or is a list. If the
                value is a range, it is the starting value.
            calculation_type : str, optional
                Type of the calculation. Options are ``"discrete"`` or ``"range"``.
                The default is ``"discrete"``.
            calculation_stop : str, optional
                Stopping value if ``calculation_type="range"``.  The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            goal_name : str, optional
                 Name of the goal. The default is ``None``.
            goal_value : optional
                 Value for the goal. The default is ``1``.
            goal_weight : optional
                 Value for the goal weight. The default is ``1``.
            condition : string, optional
                 The default is ``"=="``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_goal(
                optigoalname="CostFunctionGoals",
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type=calculation_type,
                calculation=calculation,
                calc_val1=calculation_value,
                calc_val2=calculation_stop,
                goal_name=goal_name,
                goal_weight=goal_weight,
                goal_value=goal_value,
                condition=condition,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiDXDOE"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_doe(
        self,
        calculation,
        calculation_value,
        calculation_type="Freq",
        reporttype="Modal Solution Data",
        domain="Sweep",
        condition="<=",
        goal_value=1,
        goal_weight=1,
        solution=None,
        parametricname=None,
    ):
        """Add a basic DesignXplorer DOE (Design of Experiments).

        You can customize all options after the DOE is added.

        Parameters
        ----------
        calculation : str, optional
            Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
        calculation_value : str, optional
            Variation value, such as ``"1GHz"``.
        calculation_type : str, optional
            Type of the calculation. The default is ``"Freq"``.
        calculation_stop : str, optional
            Stopping value if ``calculation_type="range"``.  The default is ``""``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        condition : string, optional
            The default is ``"<="``.
        goal_value : optional
            Value for the goal. The default is ``1``.
        goal_weight : optional
            Value for the goal weight. The default is ``1``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        parametricname : str, optional
            Name of the analysis. The default is ``None``, in which case a
            default name is assigned.

        Returns
        -------
        type
            DOE object.

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not solution:
            solution = self._app.nominal_sweep
        setupname = [solution.split(" ")[0]]
        if not parametricname:
            parametricname = generate_unique_name("DesignOfExp")
        setup = self.Setup(self._app, parametricname)
        setup.props["Sim. Setups"] = setupname
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype

        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calculation_value]}
        )
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]}
        )
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)
        setup.props["CostFunctionGoals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup


class OptimizationSetups(object):
    """Sets up optimizations.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> optimization_setup = app.opti_optimization
    """

    class Setup(CommonOptimetrics, object):
        """Sets up an optimization in optiSLang.

        Parameters
        ----------
        p_app : str
            Inherited AEDT object.
        name :

        dictinputs : optional
            The default is ``None``.

        """

        def __init__(self, p_app, name, dictinputs=None):
            CommonOptimetrics.__init__(self, p_app, name, dictinputs=dictinputs, optimtype="OptiOptimization")
            pass

        @pyaedt_function_handler()
        def add_goal(
            self,
            calculation="",
            calculation_value="",
            calculation_type="discrete",
            calculation_stop="",
            reporttype="Modal Solution Data",
            solution=None,
            domain="Sweep",
            goal_name=None,
            goal_value=1,
            goal_weight=1,
            condition="==",
        ):
            """Add a calculation to the analysis.

            Parameters
            ----------
            calculation : str, optional
                Expression for the calculation, such as ``"dB(S(1,1,))"``. The default is ``""``.
            calculation_value : str, optional
                Value for the calculation, such as ``"1GHz"`` if a sweep. The default is ``""``.
                If ``calculation_type="discrete"``, the value is discrete or is a list. If the
                value is a range, it is the starting value.
            calculation_type : str, optional
                Type of the calculation. Options are ``"discrete"`` or ``"range"``.
                The default is ``"discrete"``.
            calculation_stop : str, optional
                Stopping value if ``calculation_type="range"``.  The default is ``""``.
            reporttype : str, optional
                Name of the report to add the calculation to. The default
                is ``"Modal Solution Data"``.
            solution : str, optional
                Type of the solution. The default is ``None``, in which case the default
                solution is used.
            domain : str, optional
                Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
            goal_name : str, optional
                 Name of the goal. The default is ``None``.
            goal_value : optional
                 Value for the goal. The default is ``1``.
            goal_weight : optional
                 Value for the goal weight. The default is ``1``.
            condition : string, optional
                 The default is ``"=="``.

            Returns
            -------
            bool
                ``True`` when successful, ``False`` when failed.

            References
            ----------

            >>> oModule.EditSetup
            """
            return self._add_goal(
                optigoalname="Goals",
                reporttype=reporttype,
                solution=solution,
                domain=domain,
                calculation_type=calculation_type,
                calculation=calculation,
                calc_val1=calculation_value,
                calc_val2=calculation_stop,
                goal_name=goal_name,
                goal_value=goal_value,
                goal_weight=goal_weight,
                condition=condition,
            )

    @property
    def p_app(self):
        """Parent."""
        return self._app

    @property
    def optimodule(self):
        """Optimetrics module.

        Returns
        -------
        :class:`Optimetrics`

        """
        return self._app.ooptimetrics

    def __init__(self, p_app):
        self._app = p_app
        self.setups = []
        if self._app.design_properties:
            try:
                setups_data = self._app.design_properties["Optimetrics"]["OptimetricsSetups"]
                for data in setups_data:
                    if (
                        isinstance(setups_data[data], (OrderedDict, dict))
                        and setups_data[data]["SetupType"] == "OptiOptimization"
                    ):
                        self.setups.append(self.Setup(p_app, data, setups_data[data]))
            except:
                pass

    @pyaedt_function_handler()
    def add_optimization(
        self,
        calculation,
        calculation_value,
        calculation_type="Freq",
        reporttype="Modal Solution Data",
        domain="Sweep",
        condition="<=",
        goal_value=1,
        goal_weight=1,
        solution=None,
        parametricname=None,
    ):
        """Add a basic optimization analysis.

        You can customize all options after the analysis is added.

        Parameters
        ----------
        calculation : str, optional
            Name of the calculation.
        calculation_value : str, optional
            Variation value, such as ``"1GHz"``.
        calculation_type : str, optional
            Type of the calculation. The default is ``"Freq"``.
        reporttype : str, optional
            Name of the report to add the calculation to. The default
            is ``"Modal Solution Data"``.
        domain : str, optional
            Type of the domain. The default is ``"Sweep"``. If ``None``, one sweep is taken.
        condition : string, optional
            The default is ``"<="``.
        goal_value : optional
            Value for the goal. The default is ``1``.
        goal_weight : optional
            Value for the goal weight. The default is ``1``.
        solution : str, optional
            Type of the solution. The default is ``None``, in which case the default
            solution is used.
        parametricname : str, optional
            Name of the analysis. The default is ``None``, in which case a
            default name is assigned.

        Returns
        -------
        type
            Optimization object.

        References
        ----------

        >>> oModule.InsertSetup
        """
        if not parametricname:
            parametricname = generate_unique_name("Optimization")
        setup = self.Setup(self._app, parametricname)
        sweepdefinition = OrderedDict()
        sweepdefinition["ReportType"] = reporttype
        if not solution:
            solution = self._app.nominal_sweep
        sweepdefinition["Solution"] = solution
        sweepdefinition["SimValueContext"] = OrderedDict({"Domain": domain})
        sweepdefinition["Calculation"] = calculation
        sweepdefinition["Name"] = calculation
        sweepdefinition["Ranges"] = OrderedDict(
            {"Range": ["Var:=", calculation_type, "Type:=", "d", "DiscreteValues:=", calculation_value]}
        )
        sweepdefinition["Condition"] = condition
        sweepdefinition["GoalValue"] = OrderedDict(
            {"GoalValueType": "Independent", "Format": "Real/Imag", "bG": ["v:=", "[{};]".format(goal_value)]}
        )
        sweepdefinition["Weight"] = "[{};]".format(goal_weight)

        setup.props["Goals"]["Goal"] = sweepdefinition
        setup.create()
        self.setups.append(setup)
        return setup
