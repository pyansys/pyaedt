from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler
from .Object3d import CircuitComponent
from .PrimitivesCircuit import CircuitComponents


class SimplorerComponents(CircuitComponents):
    """SimplorerComponents class.
    
    This class is for managing all circuit components for Simplorer.
    """

    @property
    def design_libray(self):
        """ """
        return "Simplorer Elements"

    @property
    def tab_name(self):
        """ """
        return "Quantities"

    @aedt_exception_handler
    def __getitem__(self, partname):
        """
        
        Parameters
        ----------
        partname : int or str
            ID or name of object.
        
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

    def __init__(self, parent, modeler):
        CircuitComponents.__init__(self, parent, modeler)
        self._parent = parent
        self.modeler = modeler
        self._currentId = 0
        self.components = defaultdict(CircuitComponent)
        pass

    @aedt_exception_handler
    def create_resistor(self, compname=None, value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """Create a new resistor.

        Parameters
        ----------
        compname : str, optional
            Name of the resistor. The default is ``None``.
        value : float, optional
            Value for the resistor. The default is ``50``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the resistor.
        str
            Name of the resistor.
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="R", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        self.components[id].set_property("R", value)

        return id, name

    @aedt_exception_handler
    def create_inductor(self, compname=None,value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """Create a new inductor.

        Parameters
        ----------
        compname : str, optional
            Name of the inductor. The default is ``None``.
        value : float, optional
            Value for the inductor. The default is ``50``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the inductor.
        str
            Name of the inductor.
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="L", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        self.components[id].set_property("L", value)
        return id, name

    @aedt_exception_handler
    def create_capacitor(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new capacitor.

        Parameters
        ----------
        compname : str, optional
            Name of the capacitor. The default is ``None``.
        value : float, optional
            Value for the capacitor. The default is ``50``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the capacitor.
        str
            Name of the capacitor.
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="C", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)


        self.components[id].set_property("C", value)
        return id, name

    @aedt_exception_handler
    def create_diode(self, compname=None, model_name="required", xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new diode.

        Parameters
        ----------
        compname : str
            Name of the diode. The default is ``None``.
        model_name : str, optional
            Name of the model.  The default is ``"required"``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the diode.
        str
            Name of the diode.
        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="D", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)
        return id, name

    @aedt_exception_handler
    def create_npn(self, compname=None, value=None, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new transistor NPN.

        Parameters
        ----------
        compname : str, optional
            Name of the transistor NPN. The default is ``None``.
        value : float, optional
            Value for the transistor NPN. The default is ``50``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the transistor NPN.
        str
            Name of the transistor NPN.
        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="BJT", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)
        return id, name

    @aedt_exception_handler
    def create_pnp(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """Create a new transistor PNP.

        Parameters
        ----------
        compname : str, optional
            Name of the transistor PNP. The default is ``None``.
        value : float, optional
            Value for the transistor PNP. The default is ``50``.
        xpos : optional
            X-axis position. The default is ``0``.
        ypos : optional
            Y-axis position. The default is ``0``.
        angle : float, optional
            Angle value. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The defaut is ``False``.

        Returns
        -------
        type
            ID of the transistor PNP.
        str
            Name of the transistor PNP.

        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="BJT", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        return id, name
