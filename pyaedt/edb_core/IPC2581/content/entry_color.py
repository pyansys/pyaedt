from pyaedt.edb_core.IPC2581.content.color import Color


class EntryColor(object):
    def __init__(self):
        self.name = ""
        self.color = Color()

    def write_xml(self):
        pass