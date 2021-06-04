"""

EDB  Analysis
--------------------------------------------
This Example shows how to use EDB co to interact with a layout
"""

import os
import sys
import pathlib
import glob
import shutil
local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
sys.path.append(os.path.join(aedt_lib_path))
import clr
import os
import time
from pyaedt import generate_unique_name, examples
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
example_path =examples.download_aedb()
targetfolder = os.path.join(temp_folder,'Galileo.aedb')
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)
targetfile=os.path.join(targetfolder)
print(targetfile)
aedt_file = targetfile[:-12]+"aedt"


#################################

from pyaedt import Edb

#################################

if os.path.exists(aedt_file): os.remove(aedt_file)
edb = Edb(edbpath=targetfile)

#################################
# Compute Nets and Components

print("Nets {}".format(len(edb.core_nets.nets.keys())))
start = time.time()
print("Components {}".format(len(edb.core_components.components.keys())))
print("elapsed time = ", time.time() - start)

#################################
# Get Pin Position


pins = edb.core_components.get_pin_from_component("U2")
for pin in pins:
    print(edb.core_components.get_pin_position(pin))


#################################
# Get all components connected to a net

edb.core_components.get_component_net_connection_info("U2")

#################################
# Compute Rats

rats = edb.core_components.get_rats()

#################################
# Get all dc connected netlist through inductance

GROUND_NETS = ["GND", "PGND"]
dc_connected_net_list = edb.core_nets.get_dcconnected_net_list(GROUND_NETS)
print(dc_connected_net_list)

#################################
# Get Power Tree

VRM = "U3A1"
OUTPUT_NET = "BST_V1P0_S0"
powertree_df, power_nets = edb.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
for el in powertree_df:
    print(el)



#################################
# Delete all RLC with 1 pin only


edb.core_components.delete_single_pin_rlc()

#################################
# Delete component

edb.core_components.delete_component("C3B17")

#################################
# Delete one or more net

edb.core_nets.delete_nets("A0_N")

#################################
# Save Modification

edb.save_edb()

#################################
# Close modifications

edb.close_edb()

#################################


