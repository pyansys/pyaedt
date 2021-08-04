"""
EDB  Analysis
-------------
This example shows how to use EDB to interact with a layout.
"""
# sphinx_gallery_thumbnail_path = 'Resources/edb.png'

import shutil

import os
import time
from pyaedt import generate_unique_name, examples

if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
example_path = examples.download_aedb()
targetfolder = os.path.join(temp_folder,'Galileo.aedb')
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)
targetfile=os.path.join(targetfolder)
print(targetfile)
aedt_file = targetfile[:-12]+"aedt"


###############################################################################

from pyaedt import Edb

###############################################################################
# Launch the ``Edb`` class.
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This example uses EDB 2021.1.

# This example uses SI units.

if os.path.exists(aedt_file): os.remove(aedt_file)
edb = Edb(edbpath=targetfile)

###############################################################################
# Compute nets and components.
# There are queries for nets, stackups, layers, components, and geometries.

print("Nets {}".format(len(edb.core_nets.nets.keys())))
start = time.time()
print("Components {}".format(len(edb.core_components.components.keys())))
print("elapsed time = ", time.time() - start)

###############################################################################
# Get a pin position.
# The next example shows how to get all pins for a specific component and get 
# the position of each of them.
# Each pin is a list of ``[X, Y]`` coordinate postions.

pins = edb.core_components.get_pin_from_component("U2")
for pin in pins:
    print(edb.core_components.get_pin_position(pin))

###############################################################################
# Get all nets connected to a specific component.

edb.core_components.get_component_net_connection_info("U2")

###############################################################################
# Compute rats.

rats = edb.core_components.get_rats()

###############################################################################
# Get all DC-connected net lists through inductance.
# Inputs needed are ground net lists. This method returns a list of all nets 
# connected to a ground thorugh an inductor.

GROUND_NETS = ["GND", "PGND"]
dc_connected_net_list = edb.core_nets.get_dcconnected_net_list(GROUND_NETS)
print(dc_connected_net_list)

###############################################################################
# Get the power tree based on a specific net.

VRM = "U3A1"
OUTPUT_NET = "BST_V1P0_S0"
powertree_df, power_nets = edb.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
for el in powertree_df:
    print(el)

###############################################################################
# Delete all RLCs with only one pin.
# This method is useful for removing components not needed in the simulation.

edb.core_components.delete_single_pin_rlc()

###############################################################################
# Delete a component.
# You can manually delete one or more components.

edb.core_components.delete_component("C3B17")

###############################################################################
# Delete one or more nets.
# You can manually delete one or more nets.

edb.core_nets.delete_nets("A0_N")

###############################################################################
# Get the stackup limits, top and bottom layers, and elevations.

print(edb.core_stackup.stackup_limits())

###############################################################################
# Create a new coaxial port for HFSS simulation.

edb.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

###############################################################################
# Edit the stackup and material.
# You can change stackup properties with assignment.
# Materials can be created and assigned to layers.

edb.core_stackup.stackup_layers.layers['TOP'].thickness = "75um"
edb.core_stackup.create_debye_material("My_Debye", 5, 3, 0.02, 0.05, 1e5, 1e9)
edb.core_stackup.stackup_layers.layers['UNNAMED_002'].material_name = "My_Debye"

###############################################################################
# Create a circuit port for SIwave simulation.

edb.core_siwave.create_circuit_port("U2A5", "DDR3_DM0")

edb.core_siwave.add_siwave_ac_analysis()

edb.core_siwave.add_siwave_dc_analysis()

###############################################################################
# Save modifications.

edb.save_edb()

###############################################################################
# Close EDB. 
# After EDB is closed, it can be opened by AEDT.

edb.close_edb()
