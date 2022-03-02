"""
This module contains EDB general methods and related methods.

"""
import logging
import os
import warnings

from pyaedt.generic.general_methods import aedt_exception_handler

try:
    import clr

    clr.AddReference("System.Collections")
    from System.Collections.Generic import List
except ImportError:
    if os.name != "posix":
        warnings.warn("This module requires pythonnet.")

logger = logging.getLogger(__name__)


@aedt_exception_handler
def convert_netdict_to_pydict(dict_in):
    """Convert a net dictionary to a Python dictionary.

    Parameters
    ----------
    dict_in : dict
        Net dictionary to convert.

    Returns
    -------
    dict
        Dictionary converted to Python.

    """
    pydict = {}
    for key in dict_in.Keys:
        pydict[key] = dict_in[key]
    return pydict


@aedt_exception_handler
def convert_pydict_to_netdict(dict):
    """Convert a Python dictionarty to a Net dictionary.

    Parameters
    ----------
    dict : dict
        Python dictionary to convert.


    Returns
    -------
    dict
        Dictionary converted to Net.
    """
    type = dict[dict.Keys[0]]
    # to be completed


@aedt_exception_handler
def convert_py_list_to_net_list(pylist):
    """Convert a Python list to a Net list.

    Parameters
    ----------
    pylist : list
        Python list to convert.

    Returns
    -------
    list
        List converted to Net.
    """
    if not isinstance(pylist, (list, tuple)):
        pylist = [pylist]
    ls = list([type(item) for item in pylist])
    if len(ls) > 0:
        net_list = List[ls[0]]()
        for el in pylist:
            net_list.Add(el)
        return net_list


@aedt_exception_handler
def convert_net_list_to_py_list(netlist):
    """Convert a Net list to a Python list.

    Parameters
    ----------
    netlist : list
       Net list to convert.


    Returns
    -------
    list
        List converted to Python.
    """
    pylist = []
    for el in netlist:
        pylist.__add__(el)
    return pylist
