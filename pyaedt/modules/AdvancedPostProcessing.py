"""
This module contains the `PostProcessor` class.

It contains all advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.
"""
from __future__ import absolute_import

import math
import os
import time
import warnings

from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modules.PostProcessor import PostProcessor as Post
from pyaedt.generic.constants import CSS4_COLORS, AEDT_UNITS

try:
    import numpy as np
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install numpy\n\nRequires CPython."
    )

try:
    import pyvista as pv

    pyvista_available = True
except ImportError:
    warnings.warn(
        "The PyVista module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install pyvista\n\nRequires CPython."
    )

try:
    from IPython.display import Image

    ipython_available = True
except ImportError:
    warnings.warn(
        "The Ipython module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install ipython\n\nRequires CPython."
    )

try:
    import matplotlib.pyplot as plt
except ImportError:
    warnings.warn(
        "The Matplotlib module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install matplotlib\n\nRequires CPython."
    )


def is_notebook():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_float(istring):
    """Convert a string to a float.

    Parameters
    ----------
    istring : str
        String to convert to a float.

    Returns
    -------
    float
        Converted float when successful, ``0`` when when failed.
    """
    try:
        return float(istring.strip())
    except Exception:
        return 0


class ObjClass(object):
    """Class that manages mesh files to be plotted in pyvista."""

    def __init__(self, path, color, opacity, units):
        self.path = path
        self._color = (0, 0, 0)
        self.color = color
        self.opacity = opacity
        self.units = units
        self._cached_mesh = None
        self._cached_polydata = None
        self.name = os.path.splitext(self.path)[0]

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, (tuple, list)):
            self._color = value
        elif value in CSS4_COLORS:
            h = CSS4_COLORS[value].lstrip("#")
            self._color = tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))


class FieldClass(object):
    """Class to manage Field data to be plotted in pyvista."""

    def __init__(self, path, log_scale=True, coordinate_units="meter", opacity=1, color_map="rainbow", label="Field"):
        self.path = path
        self.log_scale = log_scale
        self.units = coordinate_units
        self.opacity = opacity
        self.color_map = color_map
        self._cached_mesh = None
        self._cached_polydata = None
        self.label = label
        self.name = os.path.splitext(self.path)[0]


class ModelPlotter(object):
    """Class that manage the plot data."""

    def __init__(self):
        self._objects = []
        self._fields = []
        self._frames = []
        self.show_axes = True
        self.show_legend = True
        self.show_grid = True
        self.is_notebook = is_notebook()
        self.gif_file = None
        self.legend = True
        self._background_color = (255, 255, 255)
        self.off_screen = False
        self.windows_size = [1024, 768]
        self.pv = None
        self.view = "isometric"
        self.units = "meter"
        self.frame_per_seconds = 1
        self._plot_meshes = []
        self.range_min = None
        self.range_max = None
        self.image_file = None

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, value):
        if isinstance(value, (tuple, list)):
            self._background_color = value
        elif value in CSS4_COLORS:
            h = CSS4_COLORS[value].lstrip("#")
            self._background_color = tuple(int(h[i: i + 2], 16) for i in (0, 2, 4))

    @property
    def fields(self):
        """Field Object.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.FieldClass`
        """
        return self._fields

    @property
    def frames(self):
        """Frames list for animation.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.FieldClass`
        """
        return self._frames

    @property
    def objects(self):
        """Field Object.

        Returns
        -------
        list of :class:`pyaedt.modules.AdvancedPostProcessing.ObjClass`
        """
        return self._objects

    @aedt_exception_handler
    def add_object(self, cad_path, cad_color="dodgerblue", opacity=1, units="mm"):
        """Add an mesh file to the scenario. It can be obj or any of pyvista supported files.

        Parameters
        ----------
        cad_path : str
            Full path to the file.
        cad_color : str or tuple
            Can be a string with color name or a tuple with (r,g,b) values.
        opacity : float
            Value between 0 to 1 of opacity.
        units : str
            Model units.

        Returns
        -------
        bool
        """
        self._objects.append(ObjClass(cad_path, cad_color, opacity, units))
        self.units = units
        return True

    @aedt_exception_handler
    def add_field_from_file(
            self,
            field_path,
            log_scale=True,
            coordinate_units="meter",
            opacity=1,
            color_map="rainbow",
    ):
        """Add a field file to the scenario. It can be aedtplt, fld or csv file.

        Parameters
        ----------
        field_path : str
            Full path to the file.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.
        Returns
        -------
        bool
        """
        self._fields.append(FieldClass(field_path, log_scale, coordinate_units, opacity, color_map))

    @aedt_exception_handler
    def add_frames_from_file(
            self,
            field_files,
            log_scale=True,
            coordinate_units="meter",
            opacity=1,
            color_map="rainbow",
    ):
        """Add a field file to the scenario. It can be aedtplt, fld or csv file.

        Parameters
        ----------
        field_files : list
            list of full path to frame file.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.
        Returns
        -------
        bool
        """
        for field in field_files:
            self._frames.append(FieldClass(field, log_scale, coordinate_units, opacity, color_map))

    @aedt_exception_handler
    def add_field_from_data(
            self, coordinates, fields_data, log_scale=True, coordinate_units="meter", opacity=1, color_map="rainbow"
    ):
        """Add field data to the scenario.

        Parameters
        ----------
        coordinates : list of list
            List of list [x,y,z] coordinates.
        fields_data : list
            List of list Fields Value.
        log_scale : bool
            Either if the field has to be plotted log or not.
        coordinate_units : str
            Fields coordinates units.
        opacity : float
            Value between 0 to 1 of opacity.
        color_map : str
            Color map of field plot. Default rainbow.

        Returns
        -------
        bool
        """
        self._fields.append(FieldClass(None, log_scale, coordinate_units, opacity, color_map))
        vertices = np.array(coordinates)
        filedata = pv.PolyData(vertices)
        filedata = filedata.delaunay_2d()
        filedata.point_data[self.fields[-1].label] = np.array(fields_data)
        self.fields[-1]._cached_polydata = filedata

    @aedt_exception_handler
    def _triangle_vertex(self, elements_nodes, num_nodes_per_element, take_all_nodes=True):
        trg_vertex = []
        if num_nodes_per_element == 10 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[4]])
                trg_vertex.append([e[1], e[4], e[3]])
                trg_vertex.append([e[3], e[4], e[5]])

                trg_vertex.append([e[9], e[6], e[8]])
                trg_vertex.append([e[6], e[0], e[3]])
                trg_vertex.append([e[6], e[3], e[8]])
                trg_vertex.append([e[8], e[3], e[5]])

                trg_vertex.append([e[9], e[7], e[8]])
                trg_vertex.append([e[7], e[2], e[4]])
                trg_vertex.append([e[7], e[4], e[8]])
                trg_vertex.append([e[8], e[4], e[5]])

                trg_vertex.append([e[9], e[7], e[6]])
                trg_vertex.append([e[7], e[2], e[1]])
                trg_vertex.append([e[7], e[1], e[6]])
                trg_vertex.append([e[6], e[1], e[0]])
        elif num_nodes_per_element == 10 and not take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[2], e[5]])
                trg_vertex.append([e[9], e[0], e[5]])
                trg_vertex.append([e[9], e[2], e[0]])
                trg_vertex.append([e[9], e[2], e[5]])

        elif num_nodes_per_element == 6 and not take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[2], e[5]])

        elif num_nodes_per_element == 6 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[4]])
                trg_vertex.append([e[1], e[4], e[3]])
                trg_vertex.append([e[3], e[4], e[5]])

        elif num_nodes_per_element == 4 and take_all_nodes:
            for e in elements_nodes:
                trg_vertex.append([e[0], e[1], e[3]])
                trg_vertex.append([e[1], e[2], e[3]])
                trg_vertex.append([e[0], e[1], e[2]])
                trg_vertex.append([e[0], e[2], e[3]])

        elif num_nodes_per_element == 3:
            trg_vertex = elements_nodes

        return trg_vertex

    @aedt_exception_handler
    def _read_mesh_files(self, read_frames=False):
        for cad in self.objects:
            if not cad._cached_polydata:
                filedata = pv.read(cad.path)
                cad._cached_polydata = filedata
            color_cad = [i / 256 for i in cad.color]
            cad._cached_mesh = self.pv.add_mesh(cad._cached_polydata, color=color_cad, opacity=cad.opacity)
        obj_to_iterate = [i for i in self._fields]
        if read_frames:
            for i in self.frames:
                obj_to_iterate.append(i)
        for field in obj_to_iterate:
            if field.path and not field._cached_polydata:
                if ".fld" in field.path:
                    points = []
                    with open(field.path, "r") as f:
                        lines = f.readlines()
                        id = 0
                        for line in lines:
                            if id > 1:
                                points.append([float(i) for i in line.split(" ")])
                            else:
                                id += 1
                    fields = [i[-1] for i in points]
                    try:
                        conv = 1 / AEDT_UNITS["Length"][self.units]
                    except:
                        conv = 1
                    nodes = [[i[0] * conv, i[1] * conv, i[2] * conv] for i in points]
                    vertices = np.array(nodes)
                    filedata = pv.PolyData(vertices)
                    filedata = filedata.delaunay_2d()
                    filedata.point_data[field.label] = np.array(fields)
                    field._cached_polydata = filedata
                elif ".aedtplt" in field.path:
                    lines = []
                    with open(field.path, "r") as f:
                        drawing_found = False
                        for line in f:
                            if "$begin Drawing" in line:
                                drawing_found = True
                                l_tmp = []
                                continue
                            if "$end Drawing" in line:
                                lines.append(l_tmp)
                                drawing_found = False
                                continue
                            if drawing_found:
                                l_tmp.append(line)
                                continue
                    surf = None
                    for drawing_lines in lines:
                        bounding = []
                        elements = []
                        nodes_list = []
                        solution = []
                        for l in drawing_lines:
                            if "BoundingBox(" in l:
                                bounding = l[l.find("(") + 1: -2].split(",")
                                bounding = [i.strip() for i in bounding]
                            if "Elements(" in l:
                                elements = l[l.find("(") + 1: -2].split(",")
                                elements = [int(i.strip()) for i in elements]
                            if "Nodes(" in l:
                                nodes_list = l[l.find("(") + 1: -2].split(",")
                                nodes_list = [float(i.strip()) for i in nodes_list]
                            if "ElemSolution(" in l:
                                # convert list of strings to list of floats
                                sols = l[l.find("(") + 1: -2].split(",")
                                sols = [is_float(value) for value in sols]

                                # sols = [float(i.strip()) for i in sols]
                                num_solution_per_element = int(sols[2])
                                sols = sols[3:]
                                sols = [
                                    sols[i: i + num_solution_per_element]
                                    for i in range(0, len(sols), num_solution_per_element)
                                ]
                                solution = [sum(i) / num_solution_per_element for i in sols]

                        nodes = [
                            [nodes_list[i], nodes_list[i + 1], nodes_list[i + 2]] for i in range(0, len(nodes_list), 3)
                        ]
                        num_nodes = elements[0]
                        num_elements = elements[1]
                        elements = elements[2:]
                        element_type = elements[0]
                        num_nodes_per_element = elements[4]
                        hl = 5  # header length
                        elements_nodes = []
                        for i in range(0, len(elements), num_nodes_per_element + hl):
                            elements_nodes.append([elements[i + hl + n] for n in range(num_nodes_per_element)])
                        if solution:
                            take_all_nodes = True  # solution case
                        else:
                            take_all_nodes = False  # mesh case
                        trg_vertex = self._triangle_vertex(elements_nodes, num_nodes_per_element, take_all_nodes)
                        # remove duplicates
                        nodup_list = [list(i) for i in list(set([frozenset(t) for t in trg_vertex]))]
                        sols_vertex = []
                        if solution:
                            sv = {}
                            for els, s in zip(elements_nodes, solution):
                                for el in els:
                                    if el in sv:
                                        sv[el] = (sv[el] + s) / 2
                                    else:
                                        sv[el] = s
                            sols_vertex = [sv[v] for v in sorted(sv.keys())]
                        array = [[3] + [j - 1 for j in i] for i in nodup_list]
                        faces = np.hstack(array)
                        vertices = np.array(nodes)
                        surf = pv.PolyData(vertices, faces)
                        if sols_vertex:
                            temps = np.array(sols_vertex)
                            mean = np.mean(temps)
                            std = np.std(temps)
                            if np.min(temps) > 0:
                                log = True
                            else:
                                log = False
                            surf.point_data[field.label] = temps
                    field.log = log
                    field._cached_polydata = surf

    @aedt_exception_handler
    def _add_buttons(self):
        size = int(self.pv.window_size[1] / 40)
        startpos = self.pv.window_size[1] - 2 * size
        endpos = 100
        color = self.pv.background_color
        axes_color = [0 if i >= 128 else 1 for i in color]
        buttons = []
        texts = []
        max_elements = (startpos - endpos) // (size + (size // 10))

        class SetVisibilityCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, actor):
                self.actor = actor

            def __call__(self, state):
                self.actor.SetVisibility(state)

        class ChangePageCallback:
            """Helper callback to keep a reference to the actor being modified."""

            def __init__(self, plot, actor):
                self.plot = plot
                self.actors = actor
                self.id = 0
                self.endpos = 100
                self.size = int(plot.window_size[1] / 40)
                self.startpos = plot.window_size[1] - 2 * self.size
                self.max_elements = (self.startpos - self.endpos) // (self.size + (self.size // 10))
                self.i = self.max_elements

            def __call__(self, state):
                self.plot.button_widgets = [self.plot.button_widgets[0]]
                self.id += 1
                k = 0
                startpos = self.startpos
                while k < self.max_elements:
                    if len(self.text) > k:
                        self.plot.remove_actor(self.text[k])
                    k += 1
                self.text = []
                k = 0

                while k < self.max_elements:
                    if self.i >= len(self.actors):
                        self.i = 0
                        self.id = 0
                    callback = SetVisibilityCallback(self.actors[self.i])
                    self.plot.add_checkbox_button_widget(
                        callback,
                        value=self.actors[self.i]._cached_mesh.GetVisibility() == 1,
                        position=(5.0, startpos),
                        size=self.size,
                        border_size=1,
                        color_on=self.actors[self.i]._cached_mesh.color,
                        color_off="grey",
                        background_color=None,
                    )
                    self.text.append(
                        self.plot.add_text(
                            self.actors[self.i].name,
                            position=(25.0, startpos),
                            font_size=self.size // 3,
                            color=self.actors[self.i]._cached_mesh.color,
                        )
                    )
                    startpos = startpos - self.size - (self.size // 10)
                    k += 1
                    self.i += 1

        el = 1
        for actor in self.objects:
            if el < max_elements:
                callback = SetVisibilityCallback(actor._cached_mesh)
                buttons.append(
                    self.pv.add_checkbox_button_widget(
                        callback,
                        value=True,
                        position=(5.0, startpos + 50),
                        size=size,
                        border_size=1,
                        color_on=actor.color,
                        color_off="grey",
                        background_color=None,
                    )
                )
                texts.append(
                    self.pv.add_text(actor.name, position=(50.0, startpos + 50), font_size=size // 3, color=axes_color)
                )
                startpos = startpos - size - (size // 10)
                el += 1
        el = 1
        for actor in self._fields:
            if actor._cached_mesh and el < max_elements:
                callback = SetVisibilityCallback(actor._cached_mesh)
                buttons.append(
                    self.pv.add_checkbox_button_widget(
                        callback,
                        value=True,
                        position=(5.0, startpos + 50),
                        size=size,
                        border_size=1,
                        color_on="blue",
                        color_off="grey",
                        background_color=None,
                    )
                )
                texts.append(
                    self.pv.add_text(actor.name, position=(50.0, startpos + 50), font_size=size // 3, color=axes_color)
                )
                startpos = startpos - size - (size // 10)
                el += 1
        actors = [i for i in self._fields if i._cached_mesh] + self._objects
        if texts and len(texts) >= max_elements:
            callback = ChangePageCallback(self.pv, actors)
            self.pv.add_checkbox_button_widget(
                callback,
                value=True,
                position=(5.0, self.pv.window_size[1]),
                size=int(1.5 * size),
                border_size=2,
                color_on=axes_color,
                color_off=axes_color,
            )
            plot.add_text("Next", position=(50.0, plot.window_size[1]), font_size=size // 3, color="grey")
            plot.button_widgets.insert(0, plot.button_widgets.pop(plot.button_widgets.index(plot.button_widgets[-1])))

    @aedt_exception_handler
    def plot(self, export_image_path=None):
        """Plot the current available Data.

        Parameters
        ----------

        export_image_path : str
            Path to image to save.

        Returns
        -------
        bool
        """
        start = time.time()
        self.pv = pv.Plotter(notebook=is_notebook(), off_screen=self.off_screen, window_size=self.windows_size)
        self.pv.background_color = [i/256 for i in self.background_color]
        self._read_mesh_files()

        axes_color = [0 if i >= 128 else 1 for i in self.background_color]
        sargs = dict(
            title_font_size=10,
            label_font_size=10,
            shadow=True,
            n_labels=9,
            italic=True,
            fmt="%.1f",
            font_family="arial",
            interactive=True,
            color=axes_color,
            vertical=False,
        )
        for field in self._fields:
            if self.range_max is not None and self.range_min is not None:
                field._cached_mesh = self.pv.add_mesh(
                    field._cached_polydata,
                    scalars=field.label,
                    log_scale=field.log_scale,
                    scalar_bar_args=sargs,
                    cmap=field.color_map,
                    clim=[self.range_min, self.range_max],
                    opacity=field.opacity,
                )
            else:
                field._cached_mesh = self.pv.add_mesh(
                    field._cached_polydata,
                    scalars=field.label,
                    log_scale=field.log_scale,
                    scalar_bar_args=sargs,
                    cmap=field.color_map,
                    clim=[self.range_min, self.range_max],
                    opacity=field.opacity,
                )
        self._add_buttons()
        end = time.time() - start
        files_list = []
        if self.show_axes:
            self.pv.show_axes()
        if self.show_grid and not self.is_notebook:
            self.pv.show_grid(color=tuple(axes_color))
        self.pv.add_bounding_box(color=tuple(axes_color))
        if self.view == "isometric":
            self.pv.view_isometric()
        elif self.view == "top":
            self.pv.view_yz()
        elif self.view == "front":
            self.pv.view_xz()
        elif self.view == "top":
            self.pv.view_xy()
        if export_image_path:
            self.pv.show(screenshot=export_image_path, full_screen=True)
        elif self.is_notebook:
            self.pv.show()
        else:
            self.pv.show(full_screen=True)
        self.image_file = export_image_path
        return True

    @aedt_exception_handler
    def clean_cache_and_files(self, remove_objs=True, remove_fields=True, clean_cache=True):
        """

        Parameters
        ----------
        remove_objs
        remove_fields
        clean_cache

        Returns
        -------

        """
        if remove_objs:
            for el in self.objects:
                if os.path.exists(el.path):
                    os.remove(el.path)
                if clean_cache:
                    el._cached_mesh = None
                    el._cached_polydata = None
        if remove_fields:
            for el in self.fields:
                if os.path.exists(el.path):
                    os.remove(el.path)
                if clean_cache:
                    el._cached_mesh = None
                    el._cached_polydata = None
        return True

    @aedt_exception_handler
    def animate(self):
        """Animate the current field plot.

        Returns
        -------
        bool
        """
        start = time.time()
        assert len(self.frames) > 0, "Number of Fields have to be greater than 1 to do an animation."
        self.pv = pv.Plotter(notebook=is_notebook(), off_screen=self.off_screen, window_size=self.windows_size)
        self.pv.background_color = [i/256 for i in self.background_color]
        self._read_mesh_files(read_frames=True)
        end = time.time() - start
        files_list = []
        axes_color = [0 if i >= 128 else 1 for i in self.background_color]

        if self.show_axes:
            self.pv.show_axes()
        if self.show_grid and not self.is_notebook:
            self.pv.show_grid(color=tuple(axes_color))
        self.pv.add_bounding_box(color=tuple(axes_color))
        if self.show_legend:
            labels = []
            for m in self.objects:
                labels.append([m.name, m.color])
            for m in self.frames:
                labels.append([m.name, "red"])
            self.pv.add_legend(labels=labels, bcolor=None, face="circle", size=[0.15, 0.15])
        if self.view == "isometric":
            self.pv.view_isometric()
        elif self.view == "top":
            self.pv.view_yz()
        elif self.view == "front":
            self.pv.view_xz()
        elif self.view == "top":
            self.pv.view_xy()

        self._animating = True

        if self.gif_file:
            self.pv.open_gif(self.gif_file)

        def q_callback():
            """exit when user wants to leave"""
            self._animating = False

        self._pause = False

        def p_callback():
            """exit when user wants to leave"""
            self._pause = not self._pause

        self.pv.add_text("Press p for Play/Pause, Press q to exit ", font_size=8, position="upper_left")
        self.pv.add_text(" ", font_size=10, position=[0, 0])
        self.pv.add_key_event("q", q_callback)
        self.pv.add_key_event("p", p_callback)

        sargs = dict(
            title_font_size=10,
            label_font_size=10,
            shadow=True,
            n_labels=9,
            italic=True,
            fmt="%.1f",
            font_family="arial",
        )

        for field in self._fields:
            field._cached_mesh = self.pv.add_mesh(
                field._cached_polydata,
                scalars=field.label,
                log_scale=field.log_scale,
                scalar_bar_args=sargs,
                cmap=field.color_map,
                opacity=field.opacity,
            )
        # run until q is pressed

        cpos = self.pv.show(interactive=False, auto_close=False, interactive_update=not self.off_screen)

        if self.range_min is not None and self.range_max is not None:
            mins = self.range_min
            maxs = self.range_max
        else:
            mins = 1e20
            maxs = -1e20
            for el in self.frames:
                if np.min(el._cached_polydata.point_data[el.label]) < mins:
                    mins = np.min(el._cached_polydata.point_data[el.label])
                if np.max(el._cached_polydata.point_data[el.label]) > maxs:
                    maxs = np.max(el._cached_polydata.point_data[el.label])

        self.frames[0]._cached_mesh = self.pv.add_mesh(
            self.frames[0]._cached_polydata,
            scalars=self.frames[0].label,
            log_scale=self.frames[0].log_scale,
            scalar_bar_args=sargs,
            cmap=self.frames[0].color_map,
            clim=[mins, maxs],
            show_edges=False,
            pickable=True,
            smooth_shading=True,
            name="FieldPlot",
        )
        start = time.time()

        self.pv.update(1, force_redraw=True)
        if self.gif_file:
            first_loop = True
            self.pv.write_frame()
        else:
            first_loop = False
        i = 1
        while self._animating:
            if self._pause:
                time.sleep(1)
                self.pv.update(1, force_redraw=True)
                continue
            # p.remove_actor("FieldPlot")
            if i >= len(self.frames):
                if self.off_screen:
                    break
                i = 0
                first_loop = False
            scalars = self.frames[i]._cached_polydata.point_data[self.frames[i].label]
            self.pv.update_scalars(scalars, render=False)
            # p.add_mesh(surfs[i], scalars=plot_label, log_scale=log, scalar_bar_args=sargs, cmap='rainbow',
            #            show_edges=False, pickable=True, smooth_shading=True, name="FieldPlot")
            if not hasattr(self.pv, "ren_win"):
                break
            # p.update(1, force_redraw=True)
            time.sleep(max(0, self.frame_per_seconds - (time.time() - start)))
            start = time.time()
            if self.off_screen:
                self.pv.render()
            else:
                self.pv.update(1, force_redraw=True)
            if first_loop:
                self.pv.write_frame()

            time.sleep(0.2)
            i += 1
        self.pv.close()

        return True


class PostProcessor(Post):
    """Contains advanced postprocessing functionalities that require Python 3.x packages like NumPy and Matplotlib.

    Parameters
    ----------
    app :
        Inherited parent object.

    Examples
    --------
    Basic usage demonstrated with an HFSS, Maxwell, or any other design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> post = aedtapp.post
    """

    def __init__(self, app):
        Post.__init__(self, app)

    @aedt_exception_handler
    def nb_display(self, show_axis=True, show_grid=True, show_ruler=True):
        """Show the Jupyter Notebook display.

          .. note::
              .assign_curvature_extraction Jupyter Notebook is not supported by IronPython.

         Parameters
         ----------
         show_axis : bool, optional
             Whether to show the axes. The default is ``True``.
         show_grid : bool, optional
             Whether to show the grid. The default is ``True``.
         show_ruler : bool, optional
             Whether to show the ruler. The default is ``True``.

        Returns
        -------
        :class:`IPython.core.display.Image`
            Jupyter notebook image.

        """
        file_name = self.export_model_picture(show_axis=show_axis, show_grid=show_grid, show_ruler=show_ruler)
        return Image(file_name, width=500)

    @aedt_exception_handler
    def get_efields_data(self, setup_sweep_name="", ff_setup="Infinite Sphere1", freq="All"):
        """Compute Etheta and EPhi.

        .. warning::
           This method requires NumPy to be installed on your machine.


        Parameters
        ----------
        setup_sweep_name : str, optional
            Name of the setup for computing the report. The default is ``""``, in
            which case the nominal adaptive is applied.
        ff_setup : str, optional
            Far field setup. The default is ``"Infinite Sphere1"``.
        freq : str, optional
            The default is ``"All"``.

        Returns
        -------
        np.ndarray
            numpy array containing ``[theta_range, phi_range, Etheta, Ephi]``.
        """
        if not setup_sweep_name:
            setup_sweep_name = self._app.nominal_adaptive
        results_dict = {}
        all_sources = self.post_osolution.GetAllSources()
        # assuming only 1 mode
        all_sources_with_modes = [s + ":1" for s in all_sources]

        for n, source in enumerate(all_sources_with_modes):
            edit_sources_ctxt = [["IncludePortPostProcessing:=", False, "SpecifySystemPower:=", False]]
            for m, each in enumerate(all_sources_with_modes):
                if n == m:  # set only 1 source to 1W, all the rest to 0
                    mag = 1
                else:
                    mag = 0
                phase = 0
                edit_sources_ctxt.append(
                    ["Name:=", "{}".format(each), "Magnitude:=", "{}W".format(mag), "Phase:=", "{}deg".format(phase)]
                )
            self.post_osolution.EditSources(edit_sources_ctxt)

            ctxt = ["Context:=", ff_setup]

            sweeps = ["Theta:=", ["All"], "Phi:=", ["All"], "Freq:=", [freq]]

            trace_name = "rETheta"
            solnData = self.get_far_field_data(
                setup_sweep_name=setup_sweep_name, domain=ff_setup, expression=trace_name
            )

            data = solnData.nominal_variation

            theta_vals = np.degrees(np.array(data.GetSweepValues("Theta")))
            phi_vals = np.degrees(np.array(data.GetSweepValues("Phi")))
            # phi is outer loop
            theta_unique = np.unique(theta_vals)
            phi_unique = np.unique(phi_vals)
            theta_range = np.linspace(np.min(theta_vals), np.max(theta_vals), np.size(theta_unique))
            phi_range = np.linspace(np.min(phi_vals), np.max(phi_vals), np.size(phi_unique))
            real_theta = np.array(data.GetRealDataValues(trace_name))
            imag_theta = np.array(data.GetImagDataValues(trace_name))

            trace_name = "rEPhi"
            solnData = self.get_far_field_data(
                setup_sweep_name=setup_sweep_name, domain=ff_setup, expression=trace_name
            )
            data = solnData.nominal_variation

            real_phi = np.array(data.GetRealDataValues(trace_name))
            imag_phi = np.array(data.GetImagDataValues(trace_name))

            Etheta = np.vectorize(complex)(real_theta, imag_theta)
            Ephi = np.vectorize(complex)(real_phi, imag_phi)
            source_name_without_mode = source.replace(":1", "")
            results_dict[source_name_without_mode] = [theta_range, phi_range, Etheta, Ephi]
        return results_dict

    @aedt_exception_handler
    def ff_sum_with_delta_phase(self, ff_data, xphase=0, yphase=0):
        """Generate a far field sum with a delta phase.

        Parameters
        ----------
        ff_data :

        xphase : float, optional
            Phase in the X-axis direction. The default is ``0``.
        yphase : float, optional
            Phase in the Y-axis direction. The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        array_size = [4, 4]
        loc_offset = 2

        rETheta = ff_data[2]
        rEPhi = ff_data[3]
        weight = np.zeros((array_size[0], array_size[0]))
        mag = np.ones((array_size[0], array_size[0]))
        for m in range(array_size[0]):
            for n in range(array_size[1]):
                mag = mag[m][n]
                ang = np.radians(xphase * m) + np.radians(yphase * n)
                weight[m][n] = np.sqrt(mag) * np.exp(1 * ang)
        return True

    @aedt_exception_handler
    def export_model_obj(self, obj_list=None, export_path=None, export_as_single_objects=False, air_objects=False):
        """Export the model.

        Parameters
        ----------
        obj_list : list, optional
            List of objects to export. Export every model object except 3D ones, vacuum and air objects.
        export_path : str, optional
            Full path of the exported obj file.
        export_as_single_objects : bool, optional
            Define if the model will be exported as single obj or list of objs for each object.
        air_objects : bool, optional
            Define if air and vacuum objects will be exported.

        Returns
        -------
        list
            Files obj path.
        """

        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        if not export_path:
            export_path = self._app.project_path
        if not obj_list:
            obj_list = self._app.modeler.primitives.object_names
            if not air_objects:
                obj_list = [
                    i
                    for i in obj_list
                    if not self._app.modeler[i].is3d
                       or (
                               self._app.modeler[i].material_name.lower() != "vacuum"
                               and self._app.modeler[i].material_name.lower() != "air"
                       )
                ]
        if export_as_single_objects:
            files_exported = []
            for el in obj_list:
                fname = os.path.join(
                    export_path, "Model_{}_{}.obj".format(el, self._app.modeler[el].material_name.lower())
                )
                self._app.modeler.oeditor.ExportModelMeshToFile(fname, [el])
                files_exported.append([fname, self._app.modeler[el].color, 1 - self._app.modeler[el].transparency])
            return files_exported
        else:
            fname = os.path.join(export_path, "Model_AllObjs_AllMats.obj")
            self._app.modeler.oeditor.ExportModelMeshToFile(fname, obj_list)
            return [fname, "grey", 0.6]

    @aedt_exception_handler
    def export_mesh_obj(self, setup_name=None, intrinsic_dict={}):
        """Export the mesh.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.
        intrinsic_dict : dict, optipnal.
            Intrinsic dictionary that is needed for the export.
            The default is ``{}``.

        Returns
        -------

        """
        project_path = self._app.project_path

        if not setup_name:
            setup_name = self._app.nominal_adaptive
        face_lists = []
        obj_list = self._app.modeler.primitives.object_names
        for el in obj_list:
            obj_id = self._app.modeler.primitives.get_obj_id(el)
            if not self._app.modeler.primitives.objects[obj_id].is3d or (
                    self._app.modeler.primitives.objects[obj_id].material_name != "vacuum"
                    and self._app.modeler.primitives.objects[obj_id].material_name != "air"
            ):
                face_lists += self._app.modeler.primitives.get_object_faces(obj_id)
        plot = self.create_fieldplot_surface(face_lists, "Mesh", setup_name, intrinsic_dict)
        if plot:
            file_to_add = self.export_field_plot(plot.name, project_path)
            plot.delete()
            return file_to_add
        return None

    @aedt_exception_handler
    def plot_model_obj(
            self,
            objects=None,
            export_afterplot=True,
            export_path=None,
            plot_separate_objects=True,
            air_objects=False,
            show_axes=True,
            show_grid=True,
            background_color="white",
            windows_size=None,
            off_screen=False,
            color=None,
            color_by_material=False,
            opacity=None,
    ):
        """Plot the model or a substet of objects.

        Parameters
        ----------
        objects : list, optional
            Optional list of objects to plot. If `None` all objects will be exported.
        export_afterplot : bool, optional
            Set to True if the image has to be exported after the plot is completed.
        export_path : str, optional
            File name with full path. If `None` Project directory will be used.
        plot_separate_objects : bool, optional
            Plot each object separately. It may require more time to export from AEDT.
        air_objects : bool, optional
            Plot also air and vacuum objects.
        show_axes : bool, optional
            Define if axes will be visible or not.
        show_grid : bool, optional
            Define if grid will be visible or not.
        show_legend : bool, optional
            Define if legend is visible or not.
        background_color : str, list, optional
            Define the plot background color. Default is `"white"`.
            One of the keys of `pyaedt.generic.constants.CSS4_COLORS` can be used.
        object_selector : bool, optional
            Enable the list of object to hide show objects.
        windows_size : list, optional
            Windows Plot size.
        off_screen : bool, optional
            Off Screen plot.
        color : str, list
            Color of the object. Can be color name or list of RGB. If None automatic color from model or material.
        color_by_material : bool
            Either to color object by material or by their AEDT value.

        Returns
        -------
        list
            List of plot files.
        """
        assert self._app._aedt_version >= "2021.2", self.logger.error("Object is supported from AEDT 2021 R2.")
        files = self.export_model_obj(
            obj_list=objects, export_as_single_objects=plot_separate_objects, air_objects=air_objects
        )
        if not files:
            self.logger.warning("No Objects exported. Try other options or include Air objects.")
            return False

        model = ModelPlotter()

        for file in files:
            if opacity:
                model.add_object(file[0], file[1], opacity, self.modeler.model_units)
        model.background_color = background_color
        model.off_screen = off_screen
        model.show_axes = show_axes
        model.show_grid = show_grid
        if export_afterplot:
            if export_path:
                model.plot(export_path)
            else:
                file_name = os.path.join(self._app.project_path, self._app.project_name + ".png")
                model.plot(file_name)
        else:
            model.plot()
        model.clean_cache_and_files(clean_cache=False)
        return model

    @aedt_exception_handler
    def plot_field_from_fieldplot(
            self,
            plotname,
            project_path="",
            meshplot=False,
            imageformat="jpg",
            view="isometric",
            plot_label="Temperature",
            plot_folder=None,
            off_screen=False,
            scale_min=None,
            scale_max=None,
    ):
        """Export a field plot to an image file (JPG or PNG) using Python Plotly.

        .. note::
           The Plotly module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plotname : str
            Name of the field plot to export.
        project_path : str, optional
            Path for saving the image file. The default is ``""``.
        meshplot : bool, optional
            Whether to create and plot the mesh over the fields. The
            default is ``False``.
        imageformat : str, optional
            Format of the image file. Options are ``"jpg"``,
            ``"png"``, ``"svg"``, and ``"webp"``. The default is
            ``"jpg"``.
        view : str, optional
            View to export. Options are ``isometric``, ``top``, ``front``,
             ``left``, ``all``.. The default is ``"iso"``. If ``"all"``, all views are exported.
        plot_label : str, optional
            Type of the plot. The default is ``"Temperature"``.
        plot_folder : str, optional
            Plot folder to update before exporting the field.
            The default is ``None``, in which case all plot
            folders are updated.
        off_screen : bool, optional
            Export Image without plotting on UI.
        scale_min : float, optional
            Fix the Scale Minimum value.
        scale_max : float, optional
            Fix the Scale Maximum value.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
            Model Object.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)

        start = time.time()
        if not project_path:
            project_path = self._app.project_path
        file_to_add = self.export_field_plot(plotname, project_path)
        models = None
        if not file_to_add:
            return False
        else:
            if meshplot:
                if self._app._aedt_version >= "2021.2":
                    models = self.export_model_obj(export_as_single_objects=True, air_objects=False)

        model = ModelPlotter()
        model.off_screen = off_screen

        if file_to_add:
            model.add_field_from_file(file_to_add, coordinate_units=self.modeler.model_units)
            if plot_label:
                model.fields[0].label = plot_label
        if models:
            for m in models:
                model.add_object(m[0], m[1], m[2])
        model.view = view

        if scale_min and scale_max:
            model.range_min = scale_min
            model.range_max = scale_max
        model.plot(os.path.join(project_path, self._app.project_name + "." + imageformat))
        model.clean_cache_and_files(clean_cache=False)

        return model

    @aedt_exception_handler
    def animate_fields_from_aedtplt(
            self,
            plotname,
            plot_folder=None,
            meshplot=False,
            variation_variable="Phi",
            variation_list=["0deg"],
            project_path="",
            export_gif=False,
            off_screen=False,
    ):
        """Generate a field plot to an image file (JPG or PNG) using PyVista.

        .. note::
           The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        Parameters
        ----------
        plotname : str
            Name of the plot or the name of the object.
        plot_folder : str, optional
            Name of the folder in which the plot resides. The default
            is ``None``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variation_list : list, optional
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""``.
        meshplot : bool, optional
             The default is ``False``. Valid from Version 2021.2.
        export_gif : bool, optional
             The default is ``False``.
        off_screen : bool, optional
             Generate the animation without showing an interactive plot.  The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
            Model Object.
        """
        if not plot_folder:
            self.ofieldsreporter.UpdateAllFieldsPlots()
        else:
            self.ofieldsreporter.UpdateQuantityFieldsPlots(plot_folder)
        models_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                models_to_add.extend(self.export_model_obj(export_as_single_objects=True, air_objects=False))
        fields_to_add = []
        if not project_path:
            project_path = self._app.project_path
        for el in variation_list:
            self._app._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:FieldsPostProcessorTab",
                        ["NAME:PropServers", "FieldsReporter:" + plotname],
                        ["NAME:ChangedProps", ["NAME:" + variation_variable, "Value:=", el]],
                    ],
                ]
            )
            fields_to_add.append(
                self.export_field_plot(plotname, project_path, plotname + variation_variable + str(el))
            )

        model = ModelPlotter()
        model.off_screen = off_screen
        if models_to_add:
            for m in models_to_add:
                model.add_object(m[0], cad_color=m[1], opacity=m[2])
        if fields_to_add:
            model.add_frames_from_file(fields_to_add)
        if export_gif:
            model.gif_file = os.path.join(self._app.project_path, self._app.project_name + ".gif")
        model.animate()
        model.clean_cache_and_files(clean_cache=False)

        return model

    @aedt_exception_handler
    def animate_fields_from_aedtplt_2(
            self,
            quantityname,
            object_list,
            plottype,
            meshplot=False,
            setup_name=None,
            intrinsic_dict={},
            variation_variable="Phi",
            variation_list=["0deg"],
            project_path="",
            export_gif=False,
            off_screen=False,
    ):
        """Generate a field plot to an image file (JPG or PNG) using PyVista.

         .. note::
            The PyVista module rebuilds the mesh and the overlap fields on the mesh.

        This method creates the plot and exports it.
        It is an alternative to the method :func:`animate_fields_from_aedtplt`,
        which uses an existing plot.

        Parameters
        ----------
        quantityname : str
            Name of the plot or the name of the object.
        object_list : list, optional
            Name of the ``folderplot`` folder.
        plottype : str
            Type of the plot. Options are ``"Surface"``, ``"Volume"``, and
            ``"CutPlane"``.
        meshplot : bool, optional
            The default is ``False``.
        setup_name : str, optional
            Name of the setup (sweep) to use for the export. The default is
            ``None``.
        intrinsic_dict : dict, optional
            Intrinsic dictionary that is needed for the export.
            The default is ``{}``.
        variation_variable : str, optional
            Variable to vary. The default is ``"Phi"``.
        variation_list : list, option
            List of variation values with units. The default is
            ``["0deg"]``.
        project_path : str, optional
            Path for the export. The default is ``""``.
        export_gif : bool, optional
             Whether to export to a GIF file. The default is ``False``,
             in which case the plot is exported to a JPG file.
        off_screen : bool, optional
             The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.ModelPlotter`
            Model Object.
        """
        if not project_path:
            project_path = self._app.project_path
        models_to_add = []
        if meshplot:
            if self._app._aedt_version >= "2021.2":
                models_to_add.extend(self.export_model_obj(export_as_single_objects=True, air_objects=False))
        v = 0
        fields_to_add = []
        for el in variation_list:
            intrinsic_dict[variation_variable] = el
            if plottype == "Surface":
                plotf = self.create_fieldplot_surface(object_list, quantityname, setup_name, intrinsic_dict)
            elif plottype == "Volume":
                plotf = self.create_fieldplot_volume(object_list, quantityname, setup_name, intrinsic_dict)
            else:
                plotf = self.create_fieldplot_cutplane(object_list, quantityname, setup_name, intrinsic_dict)
            if plotf:
                file_to_add = self.export_field_plot(plotf.name, project_path, plotf.name + str(v))
                if file_to_add:
                    fields_to_add.append(file_to_add)
                plotf.delete()
            v += 1
        model = ModelPlotter()
        model.off_screen = off_screen
        if models_to_add:
            for m in models_to_add:
                model.add_object(m[0], cad_color=m[1], opacity=m[2])
        if fields_to_add:
            model.add_frames_from_file(fields_to_add)
        if export_gif:
            model.gif_file = os.path.join(self._app.project_path, self._app.project_name + ".gif")
            model.animate()
        model.clean_cache_and_files(clean_cache=False)

        return model

    @aedt_exception_handler
    def far_field_plot(self, ff_data, x=0, y=0, qty="rETotal", dB=True, array_size=[4, 4]):
        """Generate a far field plot.

        Parameters
        ----------
        ff_data :

        x : float, optional
            The default is ``0``.
        y : float, optional
            The default is ``0``.
        qty : str, optional
            The default is ``"rETotal"``.
        dB : bool, optional
            The default is ``True``.
        array_size : list
            List for the array size. The default is ``[4, 4]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        loc_offset = 2  # if array index is not starting at [1,1]
        xphase = float(y)
        yphase = float(x)
        array_shape = (array_size[0], array_size[1])
        weight = np.zeros(array_shape, dtype=complex)
        mag = np.ones(array_shape, dtype="object")
        port_names_arranged = np.chararray(array_shape)
        all_ports = ff_data.keys()
        w_dict = {}
        # calculate weights based off of progressive phase shift
        port_name = []
        for m in range(array_shape[0]):
            for n in range(array_shape[1]):
                mag_val = mag[m][n]
                ang = np.radians(xphase * m) + np.radians(yphase * n)
                weight[m][n] = np.sqrt(mag_val) * np.exp(1j * ang)
                current_index_str = "[" + str(m + 1 + loc_offset) + "," + str(n + 1 + loc_offset) + "]"
                port_name = [y for y in all_ports if current_index_str in y]
                w_dict[port_name[0]] = weight[m][n]

        length_of_ff_data = len(ff_data[port_name[0]][2])

        array_shape = (len(w_dict), length_of_ff_data)
        rEtheta_fields = np.zeros(array_shape, dtype=complex)
        rEphi_fields = np.zeros(array_shape, dtype=complex)
        w = np.zeros((1, array_shape[0]), dtype=complex)
        # create port mapping
        Ntheta = 0
        Nphi = 0
        for n, port in enumerate(ff_data.keys()):
            re_theta = ff_data[port][2]
            re_phi = ff_data[port][3]
            re_theta = re_theta * w_dict[port]

            w[0][n] = w_dict[port]
            re_phi = re_phi * w_dict[port]

            rEtheta_fields[n] = re_theta
            rEphi_fields[n] = re_phi

            theta_range = ff_data[port][0]
            phi_range = ff_data[port][1]
            theta = [int(np.min(theta_range)), int(np.max(theta_range)), np.size(theta_range)]
            phi = [int(np.min(phi_range)), int(np.max(phi_range)), np.size(phi_range)]
            Ntheta = len(theta_range)
            Nphi = len(phi_range)

        rEtheta_fields = np.dot(w, rEtheta_fields)
        rEtheta_fields = np.reshape(rEtheta_fields, (Ntheta, Nphi))

        rEphi_fields = np.dot(w, rEphi_fields)
        rEphi_fields = np.reshape(rEphi_fields, (Ntheta, Nphi))

        all_qtys = {}
        all_qtys["rEPhi"] = rEphi_fields
        all_qtys["rETheta"] = rEtheta_fields
        all_qtys["rETotal"] = np.sqrt(np.power(np.abs(rEphi_fields), 2) + np.power(np.abs(rEtheta_fields), 2))

        pin = np.sum(w)
        print(str(pin))
        real_gain = 2 * np.pi * np.abs(np.power(all_qtys["rETotal"], 2)) / pin / 377
        all_qtys["RealizedGain"] = real_gain

        if dB:
            if "Gain" in qty:
                qty_to_plot = 10 * np.log10(np.abs(all_qtys[qty]))
            else:
                qty_to_plot = 20 * np.log10(np.abs(all_qtys[qty]))
            qty_str = qty + " (dB)"
        else:
            qty_to_plot = np.abs(all_qtys[qty])
            qty_str = qty + " (mag)"

        plt.figure(figsize=(15, 10))
        plt.title(qty_str)
        plt.xlabel("Theta (degree)")
        plt.ylabel("Phi (degree)")

        plt.imshow(qty_to_plot, cmap="jet")
        plt.colorbar()

        np.max(qty_to_plot)

    @aedt_exception_handler
    def create_3d_plot(
            self, solution_data, nominal_sweep="Freq", nominal_value=1, primary_sweep="Theta", secondary_sweep="Phi"
    ):
        """Create a 3D plot using Matplotlib.

        Parameters
        ----------
        solution_data :
            Input data for the solution.
        nominal_sweep : str, optional
            Name of the nominal sweep. The default is ``"Freq"``.
        nominal_value : str, optional
            Value for the nominal sweep. The default is ``1``.
        primary_sweep : str, optional
            Primary sweep. The default is ``"Theta"``.
        secondary_sweep : str, optional
            Secondary sweep. The default is ``"Phi"``.

        Returns
        -------
         bool
             ``True`` when successful, ``False`` when failed.
        """
        legend = []
        Freq = nominal_value
        solution_data.nominal_sweeps[nominal_sweep] = Freq
        solution_data.primary_sweep = primary_sweep
        solution_data.nominal_sweeps[primary_sweep] = 45
        theta = np.array((solution_data.sweeps[primary_sweep]))
        phi = np.array((solution_data.sweeps[secondary_sweep]))
        r = []
        i = 0
        phi1 = []
        theta1 = [i * math.pi / 180 for i in theta]
        for el in solution_data.sweeps[secondary_sweep]:
            solution_data.nominal_sweeps[secondary_sweep] = el
            phi1.append(el * math.pi / 180)
            r.append(solution_data.data_magnitude())
        THETA, PHI = np.meshgrid(theta1, phi1)

        R = np.array(r)
        X = R * np.sin(THETA) * np.cos(PHI)
        Y = R * np.sin(THETA) * np.sin(PHI)

        Z = R * np.cos(THETA)
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(1, 1, 1, projection="3d")
        plot = ax1.plot_surface(
            X, Y, Z, rstride=1, cstride=1, cmap=plt.get_cmap("jet"), linewidth=0, antialiased=True, alpha=0.5
        )
        fig1.set_size_inches(10, 10)
