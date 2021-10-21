import warnings

from ..generic.general_methods import aedt_exception_handler, retry_ntimes
from .PrimitivesCircuit import CircuitComponents


class NexximComponents(CircuitComponents):
    """Manages circuit components for Nexxim.

    Parameters
    ----------
    parent :
        Inherited parent object.
    modeler :

    """

    @property
    def design_libray(self):
        """Design library."""
        return "Nexxim Circuit Elements"

    @property
    def tab_name(self):
        """Tab name."""
        return "PassedParameterTab"

    @aedt_exception_handler
    def __getitem__(self, partname):
        """Get the object ID if the part name is an integer or the object name if it is a string.
        Parameters
        ----------
        partname : int or str
            Part ID or object name.

        Returns
        -------
        type
            Part object details.
        """
        if type(partname) is int:
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, modeler):
        CircuitComponents.__init__(self, modeler)
        self._app = modeler._app
        self._modeler = modeler
        self._currentId = 0
        pass

    @aedt_exception_handler
    def create_3dlayout_subcircuit(self, sourcename):
        """Add a subcircuit from a HFSS 3DLayout.

        .. deprecated:: 0.4.0
           Use :func:`Circuit.modeler.components.add_subcircuit_3dlayout` instead.
        """
        warnings.warn(
            "`create_3dlayout_subcircuit` is deprecated. Use `add_subcircuit_3dlayout` instead.", DeprecationWarning
        )
        return self.add_subcircuit_3dlayout(sourcename)

    @aedt_exception_handler
    def add_subcircuit_3dlayout(self, sourcename):
        """Add a subcircuit from a HFSS 3DLayout.

        Parameters
        ----------
        sourcename : str
            Name of the source design.

        Returns
        -------
        type
            el, composed_name if succeeded or False

        """
        self._app._oproject.CopyDesign(sourcename)
        self._oeditor.PasteDesign(0,
                                  ["NAME:Attributes", "Page:=", 1, "X:=", 0, "Y:=", 0, "Angle:=", 0, "Flip:=", False])
        self.refresh_all_ids()
        for el in self.components:
            if sourcename in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def create_field_model(self, design_name, solution_name, pin_names, model_type="hfss", posx=0, posy=1):
        """Create a field model.

        Parameters
        ----------
        design_name : str
            Name of the design.
        solution_name : str
            Name  of the solution.
        pin_names : list
            List of the pin names.
        model_type : str, optional
            Type of the model. The default is ``"hfss"``.
        posx : float, optional
            Position on the X axis. The default is ``0``.
        posy : float, optional.
            Position on the Y axis. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        id = self.create_unique_id()
        component_name = design_name + "_" + str(id)
        arg = [
            "NAME: " + component_name,
            "Name:=",
            component_name,
            "ModTime:=",
            1589868932,
            "Library:=",
            "",
            "LibLocation:=",
            "Project",
            "ModelType:=",
            model_type,
            "Description:=",
            "",
            "ImageFile:=",
            "",
            "SymbolPinConfiguration:=",
            0,
            ["NAME:PortInfoBlk"],
            ["NAME:PortOrderBlk"],
            "DesignName:=",
            design_name,
            "SolutionName:=",
            solution_name,
            "NewToOldMap:=",
            [],
            "OldToNewMap:=",
            [],
            "PinNames:=",
            pin_names,
            [
                "NAME:DesignerCustomization",
                "DCOption:=",
                0,
                "InterpOption:=",
                0,
                "ExtrapOption:=",
                1,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                1,
            ],
            [
                "NAME:NexximCustomization",
                "DCOption:=",
                3,
                "InterpOption:=",
                1,
                "ExtrapOption:=",
                3,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                2,
            ],
            [
                "NAME:HSpiceCustomization",
                "DCOption:=",
                1,
                "InterpOption:=",
                2,
                "ExtrapOption:=",
                3,
                "Convolution:=",
                0,
                "Passivity:=",
                0,
                "Reciprocal:=",
                False,
                "ModelOption:=",
                "",
                "DataType:=",
                3,
            ],
            "NoiseModelOption:=",
            "External",
            "WB_SystemID:=",
            design_name,
            "IsWBModel:=",
            False,
            "filename:=",
            "",
            "numberofports:=",
            len(pin_names),
            "Simulate:=",
            False,
            "CloseProject:=",
            False,
            "SaveProject:=",
            True,
            "InterpY:=",
            True,
            "InterpAlg:=",
            "auto",
            "IgnoreDepVars:=",
            False,
            "Renormalize:=",
            False,
            "RenormImpedance:=",
            50,
        ]
        self.o_model_manager.Add(arg)
        arg = [
            "NAME:" + component_name,
            "Info:=",
            [
                "Type:=",
                8,
                "NumTerminals:=",
                len(pin_names),
                "DataSource:=",
                "",
                "ModifiedOn:=",
                1589868933,
                "Manufacturer:=",
                "",
                "Symbol:=",
                "",
                "ModelNames:=",
                "",
                "Footprint:=",
                "",
                "Description:=",
                "",
                "InfoTopic:=",
                "",
                "InfoHelpFile:=",
                "",
                "IconFile:=",
                "",
                "Library:=",
                "",
                "OriginalLocation:=",
                "Project",
                "IEEE:=",
                "",
                "Author:=",
                "",
                "OriginalAuthor:=",
                "",
                "CreationDate:=",
                1589868933,
                "ExampleFile:=",
                "",
                "HiddenComponent:=",
                0,
                "CircuitEnv:=",
                0,
                "GroupID:=",
                0,
            ],
            "CircuitEnv:=",
            0,
            "Refbase:=",
            "S",
            "NumParts:=",
            1,
            "ModSinceLib:=",
            False,
        ]
        id = 2
        for pn in pin_names:
            arg.append("Terminal:=")
            arg.append([pn, pn, "A", False, id, 1, "", "Electrical", "0"])
            id += 1
        arg.append(["NAME:Properties", "TextProp:=", ["Owner", "RD", "", model_type.upper()]])
        arg.append("CompExtID:="), arg.append(5)
        arg.append(
            [
                "NAME:Parameters",
                "TextProp:=",
                ["ModelName", "RD", "", "FieldSolver"],
                "MenuProp:=",
                ["CoSimulator", "SD", "", "Default", 0],
                "ButtonProp:=",
                ["CosimDefinition", "SD", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
            ]
        )
        arg.append(
            [
                "NAME:CosimDefinitions",
                [
                    "NAME:CosimDefinition",
                    "CosimulatorType:=",
                    103,
                    "CosimDefName:=",
                    "Default",
                    "IsDefinition:=",
                    True,
                    "Connect:=",
                    True,
                    "ModelDefinitionName:=",
                    component_name,
                    "ShowRefPin2:=",
                    2,
                    "LenPropName:=",
                    "",
                ],
                "DefaultCosim:=",
                "Default",
            ]
        )

        self.o_component_manager.Add(arg)
        self._app._odesign.AddCompInstance(component_name)
        self.refresh_all_ids()
        for el in self.components:
            if component_name in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def create_resistor(self, compname=None, value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a resistor.

        Parameters
        ----------
        compname : str, optional
            Name of the resistor. The default is ``None``.
        value : float, optional
            Resistance in ohms. The default is ``50``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the resistor.
        str
            Name of the resistor.

        """
        cmpid, cmpname = self.create_component(
            compname, xpos=xpos, ypos=ypos, angle=angle, use_instance_id_netlist=use_instance_id_netlist
        )

        self.components[cmpid].set_property("R", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_inductor(self, compname=None, value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create an inductor.

        Parameters
        ----------
        compname : str, optional
            Name of the inductor. The default is ``None``.
        value : float, optional
            Inductance value. The default is ``50``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the X axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the inductor.
        str
            Name of the inductor.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Inductors",
            component_name="IND_",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("L", value)

        return cmpid, cmpname

    @aedt_exception_handler
    def create_capacitor(self, compname=None, value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a capacitor.

        Parameters
        ----------
        compname : str, optional
            Name of the capacitor. The default is ``None``.
        value : float, optional
            Capacitor value. The default is ``50``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the capacitor.
        str
            Name of the capacitor.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Capacitors",
            component_name="CAP_",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("C", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_voltage_dc(self, compname=None, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a voltage DC source.

        Parameters
        ----------
        compname : str, optional
            Name of the voltage DC source. The default is ``None``.
        value : float, optional
            Voltage value. The default is ``50``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the voltage DC source.
        str
            Name of the voltage DC source.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Independent Sources",
            component_name="V_DC",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("DC", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_current_pulse(
            self, compname=None, value_lists=[], xpos=0, ypos=0, angle=0, use_instance_id_netlist=False
    ):
        """Create a current pulse.

        Parameters
        ----------
        compname : str, optional
            Name of the current pulse. The default is ``None``.
        value_lists : list, optional
            List of values for the current pulse. The default is ``[]``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the current pulse.
        str
            Name of the current pulse.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Independent Sources",
            component_name="I_PULSE",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        if len(value_lists) > 0:
            self.components[cmpid].set_property("I1", value_lists[0])
        if len(value_lists) > 1:
            self.components[cmpid].set_property("I2", value_lists[1])
        if len(value_lists) > 2:
            self.components[cmpid].set_property("TD", value_lists[2])
        if len(value_lists) > 3:
            self.components[cmpid].set_property("TR", value_lists[3])
        if len(value_lists) > 4:
            self.components[cmpid].set_property("TF", value_lists[4])
        if len(value_lists) > 5:
            self.components[cmpid].set_property("PW", value_lists[5])
        if len(value_lists) > 6:
            self.components[cmpid].set_property("PER", value_lists[6])

        return cmpid, cmpname

    @aedt_exception_handler
    def create_voltage_pulse(
            self, compname=None, value_lists=[], xpos=0, ypos=0, angle=0, use_instance_id_netlist=False
    ):
        """Create a voltage pulse.

        Parameters
        ----------
        compname : str, optional
            Name of the voltage pulse. The default is ``None``.
        value_lists : list, optional
            List of values for the voltage pulse. The default is ``[]``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the voltage pulse.
        str
            Name of the voltage pulse.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Independent Sources",
            component_name="V_PULSE",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        if len(value_lists) > 0:
            self.components[cmpid].set_property("V1", value_lists[0])
        if len(value_lists) > 1:
            self.components[cmpid].set_property("V2", value_lists[1])
        if len(value_lists) > 2:
            self.components[cmpid].set_property("TD", value_lists[2])
        if len(value_lists) > 3:
            self.components[cmpid].set_property("TR", value_lists[3])
        if len(value_lists) > 4:
            self.components[cmpid].set_property("TF", value_lists[4])
        if len(value_lists) > 5:
            self.components[cmpid].set_property("PW", value_lists[5])
        if len(value_lists) > 6:
            self.components[cmpid].set_property("PER", value_lists[6])

        return cmpid, cmpname

    @aedt_exception_handler
    def create_current_dc(self, compname=None, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a current DC source.

        Parameters
        ----------
        compname : str, optional
            Name of the current DC source. The default is ``None``.
        value : float, optional
            Current value. The default is ``1``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the current DC source.
        str
            Name of the current DC source.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Independent Sources",
            component_name="I_DC",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("DC", value)
        return cmpid, cmpname

    def create_coupling_inductors(
            self, compname, l1, l2, value=1, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False
    ):
        """Create a coupling inductor.

        Parameters
        ----------
        compname : str
            Name of the coupling inductor.
        l1 : float, optional
            Value for the first inductor.
        l2 : float, optional
            Value for the second inductor.
        value : float, optional
            Value for the coupling inductor. The default is ``1``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the coupling inductor.
        str
            Name of the coupling inductor.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Inductors",
            component_name="K_IND",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("Inductor1", l1)
        self.components[cmpid].set_property("Inductor2", l2)
        self.components[cmpid].set_property("CouplingFactor", value)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_diode(
            self, compname=None, model_name="required", xpos=0, ypos=0, angle=0, use_instance_id_netlist=False
    ):
        """Create a diode.

        Parameters
        ----------
        compname : str
            Name of the diode. The default is ``None``.
        model_name : str, optional
            Name of the model. The default is ``"required"``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the diode.
        str
            Name of the diode.

        """
        cmpid, cmpname = self.create_component(
            compname,
            component_library="Diodes",
            component_name="DIODE_Level1",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        self.components[cmpid].set_property("MOD", model_name)
        return cmpid, cmpname

    @aedt_exception_handler
    def create_npn(self, compname=None, value=None, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create an NPN transistor.

        Parameters
        ----------
        compname : str
            Name of the NPN transistor. The default is ``None``.
        value : float, optional
            Value for the NPN transistor. The default is ``None``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the NPN transistor.
        str
            Name of the NPN transistor.

        """
        id, name = self.create_component(
            compname,
            component_library="BJTs",
            component_name="Level01_NPN",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )
        if value:
            self.components[id].set_property("MOD", value)
        return id, name

    @aedt_exception_handler
    def create_pnp(self, compname=None, value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a PNP transistor.

        Parameters
        ----------
        compname : str
            Name of the PNP transistor. The default is ``None``.
        value : float, optional
            Value for the PNP transistor. The default is ``None``.
        xpos : float, optional
            Position on the X axis. The default is ``0``.
        ypos : float, optional
            Position on the Y axis. The default is ``0``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list.
            The default is ``False``.

        Returns
        -------
        int
            ID of the PNP transistor.
        str
            Name of the PNP transistor.

        """
        id, name = self.create_component(
            compname,
            component_library="BJTs",
            component_name="Level01_PNP",
            xpos=xpos,
            ypos=ypos,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )
        if value:
            self.components[id].set_property("MOD", value)

        return id, name

    @aedt_exception_handler
    def create_new_component_from_symbol(
            self, symbol_name, pin_lists, Refbase="U", parameter_list=[], parameter_value=[]
    ):
        """Create a component from a symbol.

        Parameters
        ----------
        symbol_name : str
            Name of the symbol.
        pin_lists : list
            List of pin names.
        Refbase : str, optional
            Reference base. The default is ``"U"``.
        parameter_list : list
            List of parameters. The default is ``[]``.
        parameter_value : list
            List of parameter values. The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = [
            "NAME:" + symbol_name,
            "Info:=",
            [
                "Type:=",
                0,
                "NumTerminals:=",
                len(pin_lists),
                "DataSource:=",
                "",
                "ModifiedOn:=",
                1591858313,
                "Manufacturer:=",
                "",
                "Symbol:=",
                symbol_name,
                "ModelNames:=",
                "",
                "Footprint:=",
                "",
                "Description:=",
                "",
                "InfoTopic:=",
                "",
                "InfoHelpFile:=",
                "",
                "IconFile:=",
                "",
                "Library:=",
                "",
                "OriginalLocation:=",
                "Project",
                "IEEE:=",
                "",
                "Author:=",
                "",
                "OriginalAuthor:=",
                "",
                "CreationDate:=",
                1591858278,
                "ExampleFile:=",
                "",
                "HiddenComponent:=",
                0,
                "CircuitEnv:=",
                0,
                "GroupID:=",
                0,
            ],
            "CircuitEnv:=",
            0,
            "Refbase:=",
            Refbase,
            "NumParts:=",
            1,
            "ModSinceLib:=",
            True,
        ]

        for pin in pin_lists:
            arg.append("Terminal:=")
            arg.append([pin, pin, "A", False, 0, 1, "", "Electrical", "0"])
        arg.append("CompExtID:=")
        arg.append(1)
        arg2 = ["NAME:Parameters"]
        for el, val in zip(parameter_list, parameter_value):
            if type(val) is str:
                arg2.append("TextValueProp:=")
                arg2.append([el, "D", "", val])
            else:
                arg2.append("ValueProp:=")
                arg2.append([el, "D", "", val, False, ""])
        arg2.append("ButtonProp:=")
        arg2.append(["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []])
        arg2.append("MenuProp:=")
        arg2.append(["CoSimulator", "D", "", "DefaultNetlist", 0])

        arg.append(arg2)
        spicesintax = Refbase + "@ID "
        id = 0
        while id < len(pin_lists):
            spicesintax += "%" + str(id) + " "
            id += 1
        for el, val in zip(parameter_list, parameter_value):
            if "MOD" in el:
                spicesintax += "@{} ".format(el)
            else:
                spicesintax += "{}=@{} ".format(el, val)

        arg3 = [
            "NAME:CosimDefinitions",
            [
                "NAME:CosimDefinition",
                "CosimulatorType:=",
                4,
                "CosimDefName:=",
                "DefaultNetlist",
                "IsDefinition:=",
                True,
                "Connect:=",
                True,
                "Data:=",
                ["Nexxim Circuit:=", spicesintax],
                "GRef:=",
                ["Nexxim Circuit:=", ""],
            ],
            "DefaultCosim:=",
            "DefaultNetlist",
        ]
        arg.append(arg3)
        self.o_component_manager.Add(arg)
        return True

    @aedt_exception_handler
    def update_object_properties(self, o):
        """Update the properties of an object.

        Parameters
        ----------
        o :
            Object to update.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Object with properties.

        """
        name = o.composed_name
        proparray = self._oeditor.GetProperties("PassedParameterTab", name)
        for j in proparray:
            propval = retry_ntimes(10, self._oeditor.GetPropertyValue, "PassedParameterTab", name, j)
            o._add_property(j, propval)
        return o

    @aedt_exception_handler
    def get_comp_custom_settings(
            self, toolNum, dc=0, interp=0, extrap=1, conv=0, passivity=0, reciprocal="False", opt="", data_type=1
    ):
        """Retrieve custom settings for a resistor.

        Parameters
        ----------
        toolNum :

        dc :
            The default is ``0``.
        interp :
            The default is ``0``.
        extrap :
            The default is ``1``.
        conv :
            The default is ``0``.
        passivity : optional
            The default is ``0``.
        reciprocal : bool, optional
            The default is ``False``.
        opt : str, optional
            The default is ``""``.
        data_type : optional
            Type of the data. The default is ``1``.

        Returns
        -------
        list
            List of the custom settings for the resistor.

        """
        if toolNum == 1:
            custom = "NAME:DesignerCustomization"
        elif toolNum == 2:
            custom = "NAME:NexximCustomization"
        else:
            custom = "NAME:HSpiceCustomization"

        res = [
            custom,
            "DCOption:=",
            dc,
            "InterpOption:=",
            interp,
            "ExtrapOption:=",
            extrap,
            "Convolution:=",
            conv,
            "Passivity:=",
            passivity,
            "Reciprocal:=",
            reciprocal,
            "ModelOption:=",
            opt,
            "DataType:=",
            data_type,
        ]

        return res

    @aedt_exception_handler
    def add_subcircuit_hfss_link(
            self,
            comp_name,
            pin_names,
            source_project_path,
            source_design_name,
            solution_name="Setup1 : Sweep",
            image_subcircuit_path=None,
    ):
        """Add a subcircuit HFSS link.

        Parameters
        ----------
        comp_name : str
            Name of the subcircuit HFSS link.
        pin_names : list
            List of the pin names.
        source_project_path : str
            Path to the source project.
        source_design_name : str
            Name of the design.
        solution_name : str, optional
            Name of the solution and sweep. The
            default is ``"Setup1 : Sweep"``.
        image_subcircuit_path : str
            Path of the Picture used in Circuit.
            Default is an HFSS Picture exported automatically

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        designer_customization = self.get_comp_custom_settings(1, 0, 0, 1, 0, 0, "False", "", 1)
        nexxim_customization = self.get_comp_custom_settings(2, 3, 1, 3, 0, 0, "False", "", 2)
        hspice_customization = self.get_comp_custom_settings(3, 1, 2, 3, 0, 0, "False", "", 3)

        if image_subcircuit_path:
            if image_subcircuit_path[-3:] != "gif" or image_subcircuit_path[-3:] != "bmp" \
                    or image_subcircuit_path[-3:] != "jpg":
                image_subcircuit_path = None
                warnings.warn(
                    "Image extension is not valid. Use default image instead.", DeprecationWarning
                )
        if not image_subcircuit_path:
            image_subcircuit_path = "C:\\Program Files\\AnsysEM\\AnsysEM21.2\\Win64\\syslib\\Bitmaps\\hfss.bmp"
        filename = ""
        comp_name_aux = source_design_name
        WB_SystemID = source_design_name
        if not self._parent.project_file == source_project_path:
            filename = source_project_path
            comp_name_aux = comp_name
            WB_SystemID = ""

        compInfo = [
            "NAME:" + str(comp_name_aux),
            "Name:=",
            comp_name_aux,
            "ModTime:=",
            1591855779,
            "Library:=",
            "",
            "LibLocation:=",
            "Project",
            "ModelType:=",
            "hfss",
            "Description:=",
            "",
            "ImageFile:=",
            image_subcircuit_path,
            "SymbolPinConfiguration:=",
            0,
            ["NAME:PortInfoBlk"],
            ["NAME:PortOrderBlk"],
            "DesignName:=",
            source_design_name,
            "SolutionName:=",
            solution_name,
            "NewToOldMap:=",
            [],
            "OldToNewMap:=",
            [],
            "PinNames:=",
            pin_names,
            designer_customization,
            nexxim_customization,
            hspice_customization,
            "NoiseModelOption:=",
            "External",
            "WB_SystemID:=",
            WB_SystemID,
            "IsWBModel:=",
            False,
            "filename:=",
            filename,
            "numberofports:=",
            len(pin_names),
            "Simulate:=",
            False,
            "CloseProject:=",
            False,
            "SaveProject:=",
            True,
            "InterpY:=",
            True,
            "InterpAlg:=",
            "auto",
            "IgnoreDepVars:=",
            False,
            "Renormalize:=",
            False,
            "RenormImpedance:=",
            50,
        ]

        self.o_model_manager.Add(compInfo)

        info = [
            "Type:=",
            8,
            "NumTerminals:=",
            len(pin_names),
            "DataSource:=",
            "",
            "ModifiedOn:=",
            1591855894,
            "Manufacturer:=",
            "",
            "Symbol:=",
            "",
            "ModelNames:=",
            "",
            "Footprint:=",
            "",
            "Description:=",
            "",
            "InfoTopic:=",
            "",
            "InfoHelpFile:=",
            "",
            "IconFile:=",
            "hfss.bmp",
            "Library:=",
            "",
            "OriginalLocation:=",
            "Project",
            "IEEE:=",
            "",
            "Author:=",
            "",
            "OriginalAuthor:=",
            "",
            "CreationDate:=",
            1591855894,
            "ExampleFile:=",
            "",
            "HiddenComponent:=",
            0,
            "CircuitEnv:=",
            0,
            "GroupID:=",
            0,
        ]

        compInfo2 = [
            "NAME:" + str(comp_name),
            "Info:=",
            info,
            "CircuitEnv:=",
            0,
            "Refbase:=",
            "S",
            "NumParts:=",
            1,
            "ModSinceLib:=",
            False,
        ]

        id = 0
        for pin in pin_names:
            compInfo2.append("Terminal:=")
            compInfo2.append([pin, pin, "A", False, id, 1, "", "Electrical", "0"])
            id += 1

        compInfo2.append(["NAME:Properties", "TextProp:=", ["Owner", "RD", "", "HFSS"]])
        compInfo2.append("CompExtID:=")
        compInfo2.append(5)
        compInfo2.append(
            [
                "NAME:Parameters",
                "TextProp:=",
                ["ModelName", "RD", "", "FieldSolver"],
                "MenuProp:=",
                ["CoSimulator", "SD", "", "Default", 0],
                "ButtonProp:=",
                ["CosimDefinition", "SD", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
            ]
        )
        compInfo2.append(
            [
                "NAME:CosimDefinitions",
                [
                    "NAME:CosimDefinition",
                    "CosimulatorType:=",
                    103,
                    "CosimDefName:=",
                    "Default",
                    "IsDefinition:=",
                    True,
                    "Connect:=",
                    True,
                    "ModelDefinitionName:=",
                    comp_name_aux,
                    "ShowRefPin2:=",
                    2,
                    "LenPropName:=",
                    "",
                ],
                "DefaultCosim:=",
                "Default",
            ]
        )

        self.o_component_manager.Add(compInfo2)
        self._app._odesign.AddCompInstance(comp_name)
        self.refresh_all_ids()
        for el in self.components:
            item = comp_name
            item2 = self.components[el].composed_name
            if comp_name in self.components[el].composed_name:
                return el, self.components[el].composed_name
        return False

    @aedt_exception_handler
    def set_sim_option_on_hfss_subcircuit(self, component, option="simulate"):
        """Set the simulation option on the HFSS subscircuit.

        Parameters
        ----------
        component : str
            Address of the component instance. For example, ``"Inst@Galileo_cutout3;87;1"``.
        option : str
            Set the simulation strategy. Options are ``"simulate"`` and ``"interpolate"``. The default
            is ``"simulate"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if option == "simulate":
            setting = "Simulate missing solutions"
        elif option == "interpolate":
            setting = "Interpolate existing solutions"
        else:
            return False
        arg = ["NAME:Simulation option", "Value:=", setting]
        return self._edit_link_definition_hfss_subcircuit(component, arg)

    @aedt_exception_handler
    def set_sim_solution_on_hfss_subcircuit(self, component, solution_name="Setup1 : Sweep"):
        """Set the simulation solution on the HFSS subcircuit.

        Parameters
        ----------
        component : str
            Address of the component instance. For example, ``"Inst@Galileo_cutout3;87;1"``.
        solution_name : str, optional
            Name of the solution and sweep. The default is ``"Setup1 : Sweep"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg = ["NAME:Solution", "Value:=", solution_name]
        return self._edit_link_definition_hfss_subcircuit(component, arg)

    @aedt_exception_handler
    def _edit_link_definition_hfss_subcircuit(self, component, edited_prop):
        """Generic function to set the link definition for an hfss subcircuit."""
        complist = component.split(";")
        complist2 = complist[0].split("@")
        arg = ["NAME:AllTabs"]
        arg1 = ["NAME:Model"]
        arg2 = ["NAME:PropServers", "Component@" + str(complist2[1])]
        arg3 = ["NAME:ChangedProps", edited_prop]

        arg1.append(arg2)
        arg1.append(arg3)
        arg.append(arg1)

        self._app._oproject.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def refresh_dynamic_link(self, component_name):
        """Refresh a dynamic link.

        Parameters
        ----------
        component_name : str
            Name of the dynamic link.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.o_component_manager.UpdateDynamicLink(component_name)
        return True

    @aedt_exception_handler
    def push_excitations(self, instance_name, thevenin_calculation=False, setup_name="LinearFrequency"):
        """Push excitations.

        .. deprecated:: 0.4.0
           Use :func:`Circuit.push_excitations` instead.
        """
        warnings.warn(
            "`circuit.modeler.components.push_excitation` is deprecated. " "Use `circuit.push_excitation` instead.",
            DeprecationWarning,
        )
        return self._app.push_excitations(instance_name, thevenin_calculation, setup_name)

    @aedt_exception_handler
    def assign_sin_excitation2ports(self, ports, settings):
        """Assign a voltage sinusoidal excitation to circuit ports.

        .. deprecated:: 0.4.0
           Use :func:`Circuit.modeler.components.assign_voltage_sinusoidal_excitation_to_ports` instead.
        """
        warnings.warn(
            "`assign_sin_excitation2ports` is deprecated. "
            "Use `assign_voltage_sinusoidal_excitation_to_ports` instead.",
            DeprecationWarning,
        )
        return self._app.assign_voltage_sinusoidal_excitation_to_ports(ports, settings)
