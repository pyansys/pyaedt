"""
This module contains all RMxprt functionalities in the ``rmxprt`` class.

Examples
--------

Create a ``Rmxprt`` object and connect to an existing RMxprt design or create a new RMxprt design if one does not exist.

>>> app = Rmxprt()

Create a ``Rmxprt`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> app = Rmxprt(projectname)

Create a ``RMxprt`` object and link to a design named ``designname`` in a project named ``projectname``.

>>> app = Rmxprt(projectname,designame)

Create a ``RMxprt`` object and open the specified project.

>>> app = Rmxprt("myfile.aedt")

"""
from __future__ import absolute_import
from .application.Design import Design
from .application.AnalysisRMxprt import FieldAnalysisRMxprt
from .generic.general_methods import aedt_exception_handler, generate_unique_name


class RMXprtModule(object):
    """ """

    component = None
    prop_servers = None

    @aedt_exception_handler
    def get_prop_server(self, parameter_name):
        """

        Parameters
        ----------
        parameter_name : str
            Name of the parameter.
            

        Returns
        -------

        """
        prop_server = None
        for key, parameter_list in self.prop_servers.items():
            if parameter_name in parameter_list:
                prop_server = key
                break
        assert prop_server is not None,\
            "Unknown parameter name {0} in component {1}!".format(prop_server, self.component)
        return prop_server

    def __init__(self, oeditor):
        self._oeditor = oeditor

    @aedt_exception_handler
    def __setitem__(self, parameter_name, value):
        self.set_rmxprt_parameter(parameter_name, value)
        return True

    @aedt_exception_handler
    def set_rmxprt_parameter(self, parameter_name, value):
        """

        Parameters
        ----------
        parameter_name : str
            Name of the parameter.  
        value :
            

        Returns
        -------

        """
        prop_server = self.get_prop_server(parameter_name)
        separator = ":" if prop_server else ""
        self._oeditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:" + self.component,
                    [
                        "NAME:PropServers",
                        "{0}{1}{2}".format(self.component, separator, prop_server)
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:" + parameter_name,
                            "Value:="		, value
                        ]
                    ]
                ]
            ])
        return True


class Stator(RMXprtModule):
    """ """
    component = "Stator"
    prop_servers = {"":        ["Outer Diameter", "Inner Diameter", "Length", "Stacking Factor"
                                "Steel Type", "Number of Slots", "Slot Type", "Lamination Sectors",
                                "Press Board Thickness", "Skew Width"],
                    "Slot":    ["Hs0", "Hs1", "Hs2", "Bs0", "Bs1", "Bs2"],
                    "Winding": ["Winding Type", "Parallel Branches"]}


class Rotor(RMXprtModule):
    """ """
    component = "Rotor"
    prop_servers = {"":        ["Outer Diameter"],
                    "Slot":    [],
                    "Winding": []}


class Rmxprt(FieldAnalysisRMxprt):
    """RMxprt Object

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project or AEDTZ archive to open. 
        The default is ``None``. If ``None``, try to get an active project and, if no projects are present, 
        create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If ``None``, try to get an active design and, 
        if no designs are present, create an empty design.
    solution_type : str, optional
        Solution type to apply to the design. The default is ``None``. If ``None`, the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
        is used or nothing is used.

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, model_units=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        FieldAnalysisRMxprt.__init__(self, "RMxprtSolution", projectname, designname, solution_type, setup_name,
                                     specified_version, NG, AlwaysNew, release_on_exit)
        if not model_units or model_units == "mm":
            model_units = "mm"
        else:
            assert model_units == "in", "Invalid model units string {}".format(model_units)
        self.modeler.oeditor.SetMachineUnits(
            [
                "NAME:Units Parameter",
                "Units:=", model_units,
                "Rescale:="    	, False
            ])
        self.stator = Stator(self.modeler.oeditor)
        self.rotor = Rotor(self.modeler.oeditor)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        Design.__exit__(self, ex_type, ex_value, ex_traceback)

    def __enter__(self):
        return self


