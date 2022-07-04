import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pyaedt.common_rpc import launch_server

if int(sys.argv[1]) == 1:
    val = True
else:
    val = False

if len(sys.argv) == 4:
    ansys_em_path=sys.argv[3]
else:
    ansys_em_path=""
launch_server(ansysem_path=ansys_em_path, non_graphical=val, port=int(sys.argv[2]))
