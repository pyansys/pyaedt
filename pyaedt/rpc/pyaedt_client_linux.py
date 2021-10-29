import sys
import os
sys.path.append(pyaedt_path)
sys.path.append(os.path.join(pyaedt_path, "pyaedt", "third_party", "ironpython"))

from pyaedt.rpc.rpyc_services import PyaedtServiceWindows
from rpyc import OneShotServer

safe_attrs = {'__abs__', '__add__', '__and__', '__bool__', '__class__', '__code__', '__cmp__', '__contains__', '__delitem__',
              '__delslice__', '__div__', '__divmod__', '__doc__', '__eq__', '__float__', '__floordiv__', '__func__',
              '__ge__', '__dict__', 
              '__getitem__', '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
              '__ifloordiv__',
              '__ilshift__', '__imod__', '__imul__', '__index__', '__int__', '__invert__', '__ior__', '__ipow__',
              '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', '__long__',
              '__lshift__', '__lt__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__new__',
              '__nonzero__',
              '__oct__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdiv__', '__rdivmod__',
              '__repr__',
              '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__rpow__', '__rrshift__',
              '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__str__',
              '__sub__',
              '__truediv__', '__xor__', 'next', '__length_hint__', '__enter__', '__exit__', '__next__',
              '__format__'}
OneShotServer(PyaedtServiceWindows, hostname=hostname, port=port,
              protocol_config={'sync_request_timeout': None, 'allow_public_attrs': True,
                               'allow_setattr': True, 'allow_getattr': True, 'allow_delattr': True,'safe_attrs':safe_attrs }).start()
