import os
from collections import OrderedDict

from pyaedt.generic.constants import LineStyle
from pyaedt.generic.constants import SymbolStyle
from pyaedt.generic.constants import TraceType
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators


def _props_with_default(dict_in, key, default_value=None):
    return dict_in[key] if dict_in.get(key, None) != None else default_value


class LimitLine(object):
    """Line Limit Management Class."""

    def __init__(self, report_setup, trace_name):
        self._oreport_setup = report_setup
        self.line_name = trace_name
        self.LINESTYLE = LineStyle()

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Limit Line", ["NAME:PropServers", self.line_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_line_properties(
        self, style=None, width=None, hatch_above=None, violation_emphasis=None, hatch_pixels=None, color=None
    ):
        """Set trace properties.

        Parameters
        ----------
        style : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        width : int, optional
            Width of the limit line. The default is ``None``.
        hatch_above : bool
           Whether the hatch is above the limit line. The default is ``None``.
        violation_emphasis : bool
            Whether to add violation emphasis. The default is ``None``.
        hatch_pixels : int
            Number of pixels for the hatch. The default is ``None``.
        color : tuple, list
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            "True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if style:
            props.append(["NAME:Line Style", "Value:=", style])
        if width and isinstance(width, (int, float, str)):
            props.append(["NAME:Line Width", "Value:=", str(width)])
        if hatch_above and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Above", "Value:=", hatch_above])
        if hatch_pixels and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Pixels", "Value:=", str(hatch_pixels)])
        if violation_emphasis:
            props.append(["NAME:Violation Emphasis", "Value:=", violation_emphasis])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)


class Note(object):
    """Note Management Class."""

    def __init__(self, report_setup, plot_note_name):
        self._oreport_setup = report_setup
        self.plot_note_name = plot_note_name

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        prop_server_name = self.plot_note_name
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Note", ["NAME:PropServers", prop_server_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_note_properties(
        self,
        text=None,
        back_color=None,
        background_visibility=None,
        border_color=None,
        border_visibility=None,
        border_width=None,
        font="Arial",
        font_size=12,
        italic=False,
        bold=False,
        color=(0, 0, 0),
    ):
        """Set note properties.

        Parameters
        ----------
        text : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        back_color : int
            Background color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        background_visibility : bool
            Whether to view background. The default is ``None``.
        border_color : int
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        border_visibility : bool
            Whether to view text border. The default is ``None``.
            The default is ``None``.
        border_width : int
            Text boarder width.
            The default is ``None``.
        font : str, optional
            The default is ``None``.
        font_size : int, optional
            The default is ``None``.
        italic : bool
            Whether the text is italic.
            The default is ``None``.
        bold : bool
            Whether the text is bold.
            The default is ``None``.
        color : int =(0, 0, 0)
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            "True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if text:
            props.append(["NAME:Note Text", "Value:=", text])
        if back_color and isinstance(back_color, (list, tuple)) and len(back_color) == 3:
            props.append(["NAME:Back Color", "R:=", back_color[0], "G:=", back_color[1], "B:=", back_color[2]])
        if background_visibility is not None:
            props.append(["NAME:Background Visibility", "Value:=", background_visibility])
        if border_color and isinstance(border_color, (list, tuple)) and len(border_color) == 3:
            props.append(["NAME:Border Color", "R:=", border_color[0], "G:=", border_color[1], "B:=", border_color[2]])
        if border_visibility is not None:
            props.append(["NAME:Border Visibility", "Value:=", border_visibility])
        if border_width and isinstance(border_width, (int, float)):
            props.append(["NAME:Border Width", "Value:=", str(border_width)])

        font_props = [
            "NAME:Note Font",
            "Height:=",
            -1 * font_size - 2,
            "Width:=",
            0,
            "Escapement:=",
            0,
            "Orientation:=",
            0,
            "Weight:=",
            700 if bold else 400,
            "Italic:=",
            255 if italic else 0,
            "Underline:=",
            0,
            "StrikeOut:=",
            0,
            "CharSet:=",
            0,
            "OutPrecision:=",
            3,
            "ClipPrecision:=",
            2,
            "Quality:=",
            1,
            "PitchAndFamily:=",
            34,
            "FaceName:=",
            font,
            "R:=",
            color[0],
            "G:=",
            color[1],
            "B:=",
            color[2],
        ]
        props.append(font_props)
        return self._change_property(props)


class Trace(object):
    """Provides trace management."""

    def __init__(self, report_setup, trace_name):
        self._oreport_setup = report_setup
        self.trace_name = trace_name
        self.LINESTYLE = LineStyle()
        self.TRACETYPE = TraceType()
        self.SYMBOLSTYLE = SymbolStyle()

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Attributes", ["NAME:PropServers", self.trace_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_trace_properties(self, trace_style=None, width=None, trace_type=None, color=None):
        """Set trace properties.

         Parameters
         ----------
        trace_style : str, optional
             Style for the trace line. The default is ``None``. You can also use
             the ``LINESTYLE`` property.
         width : int, optional
             Width of the trace line. The default is ``None``.
         trace_type : str
            Type of the trace line. The default is ``None``. You can also use the ``TRACETYPE``
            property.
         color : tuple, list
             Trace line color specified as a tuple (R,G,B) or a list of integers [0,255].
             The default is ``None``.

         Returns
         -------
         bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if trace_style:
            props.append(["NAME:Line Style", "Value:=", trace_style])
        if width and isinstance(width, (int, float, str)):
            props.append(["NAME:Line Width", "Value:=", str(width)])
        if trace_type:
            props.append(["NAME:Trace Type", "Value:=", trace_type])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)

    @pyaedt_function_handler()
    def set_symbol_properties(self, show=True, style=None, show_arrows=None, fill=None, color=None):
        """Set symbol properties.

        Parameters
        ----------
        show : bool, optional
            Whether to show the symbol. The default is ``True``.
        style : str, optional
           Style of the style. The default is ``None``. You can also use the ``SYMBOLSTYLE``
           property.
        show_arrows : bool, optional
            Whether to show arrows. The default is ``None``.
        fill : bool, optional
            Whether to fill the symbol with a color. The default is ``None``.
        color : tuple, list
            Symbol fill color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps", ["NAME:Show Symbol", "Value:=", show]]
        if style:
            props.append(["NAME:Symbol Style", "Value:=", style])
        if show_arrows:
            props.append(["NAME:Show Arrows", "Value:=", show_arrows])
        if fill:
            props.append(["NAME:Fill Symbol", "Value:=", fill])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Symbol Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)


class CommonReport(object):
    """Provides common reports."""

    def __init__(self, app, report_category, setup_name):
        self._post = app
        self.props = OrderedDict()
        self.report_category = report_category
        self.setup = setup_name
        self.props["Report Type"] = "Rectangular Plot"
        self.props["Context"] = OrderedDict()
        self.props["Context"]["Domain"] = "Sweep"
        self.props["Context"]["Primary Sweep"] = "Freq"
        self.props["Context"]["Primary Sweep Range"] = ["All"]
        self.props["Context"]["Secondary Sweep Range"] = ["All"]
        self.props["Context"]["Variations"] = {"Freq": ["All"]}
        for el, k in self._post._app.available_variations.nominal_w_values_dict.items():
            self.props["Context"]["Variations"][el] = k
        self.props["Expressions"] = None
        self.props["Plot Name"] = None
        self._is_created = True

    @property
    def differential_pairs(self):
        """Get and Set Differential Pairs flag.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Differential Pairs", False)

    @differential_pairs.setter
    def differential_pairs(self, value):
        self.props["Context"]["Differential Pairs"] = value

    @property
    def matrix(self):
        """Get and Q2D/Q3D Matrix name.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Matrix", None)

    @matrix.setter
    def matrix(self, value):
        self.props["Context"]["Matrix"] = value

    @property
    def polyline(self):
        """Get and Set Polyline name for field report.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Polyline", None)

    @polyline.setter
    def polyline(self, value):
        self.props["Context"]["Polyline"] = value

    @property
    def expressions(self):
        """Get and Set the Expressions names.

        Returns
        -------
        str
        """
        if self.props.get("Expressions", {}):
            return list(self.props.get("Expressions", {}).keys())
        return []

    @expressions.setter
    def expressions(self, value):
        if not isinstance(value, list):
            value = [value]
        for el in value:
            if not self.props.get("Expressions", None):
                self.props["Expressions"] = {}
            self.props["Expressions"][el] = {}

    @property
    def report_category(self):
        """Get and Report Category.

        Returns
        -------
        str
        """
        return self.props["Report Category"]

    @report_category.setter
    def report_category(self, value):
        self.props["Report Category"] = value

    @property
    def report_type(self):
        """Get/Set the report Type. Available values are `"3D Polar Plot"`, `"3D Spherical Plot"`,
        `"Radiation Pattern"`, `"Rectangular Plot"`, `"Data Table"`,
        `"Smith Chart"`, `"Rectangular Contour Plot"`.

        Returns
        -------
        str
        """
        return self.props["Report Type"]

    @report_type.setter
    def report_type(self, report):
        self.props["Report Type"] = report
        if not self.primary_sweep:
            if self.props["Report Type"] in ["3D Polar Plot", "3D Spherical Plot"]:
                self.primary_sweep = "Phi"
                self.secondary_sweep = "Theta"
            elif self.props["Report Type"] == "Radiation Pattern":
                self.primary_sweep = "Phi"
            elif self.domain == "Sweep":
                self.primary_sweep = "Freq"
            elif self.domain == "Time":
                self.primary_sweep = "Time"

    @property
    def traces(self):
        """Return the list of available traces in the report.

        .. note::
            This property works in version 2022 R1 and later. However, It works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        list of :class:`pyaedt.modules.report_templates.Trace`
        """
        _traces = []
        try:
            oo = self._post.oreportsetup.GetChildObject(self.plot_name)
            oo_names = self._post.oreportsetup.GetChildObject(self.plot_name).GetChildNames()
        except:
            return _traces
        for el in oo_names:
            if el in ["Legend", "Grid", "AxisX", "AxisY1", "Header", "General", "CartesianDisplayTypeProperty"]:
                continue
            try:
                oo1 = oo.GetChildObject(el).GetChildNames()

                for i in oo1:
                    _traces.append(Trace(self._post.oreportsetup, "{}:{}:{}".format(self.plot_name, el, i)))
            except:
                pass
        return _traces

    @pyaedt_function_handler()
    def _update_traces(self):
        for trace in self.traces:
            trace_name = trace.trace_name.split(":")[1]
            if "Expressions" in self.props and trace_name in self.props["Expressions"]:
                trace_val = self.props["Expressions"][trace_name]
                trace_style = _props_with_default(trace_val, "Line Style")
                trace_width = _props_with_default(trace_val, "Line Width")
                trace_type = _props_with_default(trace_val, "Line Type")
                trace_color = _props_with_default(trace_val, "Color")
                symbol_show = _props_with_default(trace_val, "Show Symbols", False)
                symbol_style = _props_with_default(trace_val, "Symbol Style", None)
                symbol_arrows = _props_with_default(trace_val, "Show Arrow", None)
                symbol_fill = _props_with_default(trace_val, "Fill Symbol", False)
                symbol_color = _props_with_default(trace_val, "Symbol Color", None)
                trace.set_trace_properties(
                    trace_style=trace_style, width=trace_width, trace_type=trace_type, color=trace_color
                )
                if self.report_category in ["Eye Diagram", "Spectrum"]:
                    continue
                trace.set_symbol_properties(
                    show=symbol_show,
                    style=symbol_style,
                    show_arrows=symbol_arrows,
                    fill=symbol_fill,
                    color=symbol_color,
                )
        if "EyeMask" in self.props and self.report_category == "Eye Diagram":
            eye_xunits = _props_with_default(self.props["EyeMask"], "XUnits", "ns")
            eye_yunits = _props_with_default(self.props["EyeMask"], "YUnits", "mV")
            eye_points = _props_with_default(self.props["EyeMask"], "Points")
            eye_enable = _props_with_default(self.props["EyeMask"], "Enable Limits", False)
            eye_upper = _props_with_default(self.props["EyeMask"], "Upper Limit", 500)
            eye_lower = _props_with_default(self.props["EyeMask"], "Lower Limit", 0.3)
            eye_transparency = _props_with_default(self.props["EyeMask"], "Transparency", 0.3)
            eye_color = _props_with_default(self.props["EyeMask"], "Mask Fill Color", (0, 128, 0))
            eye_xoffset = _props_with_default(self.props["EyeMask"], "X Offset", "0ns")
            eye_yoffset = _props_with_default(self.props["EyeMask"], "Y Offset", "0V")
            self.eye_mask(
                points=eye_points,
                xunits=eye_xunits,
                yunits=eye_yunits,
                enable_limits=eye_enable,
                upper_limits=eye_upper,
                lower_limits=eye_lower,
                color=eye_color,
                transparency=eye_transparency,
                xoffset=eye_xoffset,
                yoffset=eye_yoffset,
            )
        if "LimitLines" in self.props and self.report_category not in ["Eye Diagram"]:
            for line in self.props["LimitLines"].values():
                if "Equation" in line:
                    line_start = _props_with_default(line, "Start")
                    line_stop = _props_with_default(line, "Stop")
                    line_step = _props_with_default(line, "Step")
                    line_equation = _props_with_default(line, "Equation")
                    line_axis = _props_with_default(line, "Y Axis", 1)
                    if not line_start or not line_step or not line_stop or not line_equation:
                        self._post._app.logger.error(
                            "Equation Limit Lines needs Start, Stop, Step and Equation fields."
                        )
                        continue
                    self.add_limit_line_from_equation(
                        start_x=line_start, stop_x=line_stop, step=line_step, equation=line_equation, y_axis=line_axis
                    )
                else:
                    line_x = _props_with_default(line, "XPoints")
                    line_y = _props_with_default(line, "YPoints")
                    line_xunits = _props_with_default(line, "XUnits")
                    line_yunits = _props_with_default(line, "YUnits", "")
                    line_axis = _props_with_default(line, "Y Axis", "Y1")
                    self.add_limit_line_from_points(line_x, line_y, line_xunits, line_yunits, line_axis)
                line_style = _props_with_default(line, "Line Style")
                line_width = _props_with_default(line, "Line Width")
                line_hatchabove = _props_with_default(line, "Hatch Above")
                line_viol = _props_with_default(line, "Violation Emphasis")
                line_hatchpix = _props_with_default(line, "Hatch Pixels")
                line_color = _props_with_default(line, "Color")
                self.limit_lines[-1].set_line_properties(
                    style=line_style,
                    width=line_width,
                    hatch_above=line_hatchabove,
                    violation_emphasis=line_viol,
                    hatch_pixels=line_hatchpix,
                    color=line_color,
                )
        if "Notes" in self.props:
            for note in self.props["Notes"].values():
                note_text = _props_with_default(note, "Text")
                note_position = _props_with_default(note, "Position", [0, 0])
                self.add_note(note_text, note_position[0], note_position[1])
                note_back_color = _props_with_default(note, "Back Color")
                note_background_visibility = _props_with_default(note, "Background Visibility")
                note_border_color = _props_with_default(note, "Border Color")
                note_border_visibility = _props_with_default(note, "Border Visibility")
                note_border_width = _props_with_default(note, "Border Width")
                note_font = _props_with_default(note, "Font", "Arial")
                note_font_size = _props_with_default(note, "Height", 12)
                note_italic = _props_with_default(note, "Italic")
                note_bold = _props_with_default(note, "Bold")
                note_color = _props_with_default(note, "Color", (0, 0, 0))

                self.notes[-1].set_note_properties(
                    back_color=note_back_color,
                    background_visibility=note_background_visibility,
                    border_color=note_border_color,
                    border_visibility=note_border_visibility,
                    border_width=note_border_width,
                    font=note_font,
                    font_size=note_font_size,
                    italic=note_italic,
                    bold=note_bold,
                    color=note_color,
                )
        if "General" in self.props:
            if "Show Rectangular Plot" in self.props["General"] and self.report_category == "Eye Diagram":
                eye_rectangular = _props_with_default(self.props["General"], "Show Rectangular Plot", True)
                self.rectangular_plot(eye_rectangular)
            if "Legend" in self.props["General"]:
                legend = self.props["General"]["Legend"]
                legend_sol_name = _props_with_default(legend, "Show Solution Name", True)
                legend_var_keys = _props_with_default(legend, "Show Variation Key", True)
                leend_trace_names = _props_with_default(legend, "Show Trace Name", True)
                legend_color = _props_with_default(legend, "Background Color", (255, 255, 255))
                legend_font_color = _props_with_default(legend, "Font Color", (0, 0, 0))
                self.edit_legend(
                    show_solution_name=legend_sol_name,
                    show_variation_key=legend_var_keys,
                    show_trace_name=leend_trace_names,
                    back_color=legend_color,
                    font_color=legend_font_color,
                )
            if "Grid" in self.props["General"]:
                grid = self.props["General"]["Grid"]
                grid_major_color = _props_with_default(grid, "Major grid line color", (200, 200, 200))
                grid_minor_color = _props_with_default(grid, "Minor grid line color", (230, 230, 230))
                grid_enable_major_x = _props_with_default(grid, "Show major X grid", True)
                grid_enable_major_y = _props_with_default(grid, "Show major Y grid", True)
                grid_enable_minor_x = _props_with_default(grid, "Show minor X grid", True)
                grid_enable_minor_y = _props_with_default(grid, "Show minor Y grid", True)
                grid_style_minor = _props_with_default(grid, "Minor grid line style", "Solid")
                grid_style_major = _props_with_default(grid, "Major grid line style", "Solid")
                self.edit_grid(
                    minor_x=grid_enable_minor_x,
                    minor_y=grid_enable_minor_y,
                    major_x=grid_enable_major_x,
                    major_y=grid_enable_major_y,
                    minor_color=grid_minor_color,
                    major_color=grid_major_color,
                    style_minor=grid_style_minor,
                    style_major=grid_style_major,
                )
            if "Appearance" in self.props["General"]:
                general = self.props["General"]["Appearance"]
                general_back_color = _props_with_default(general, "Back Color", (255, 255, 255))
                general_plot_color = _props_with_default(general, "Plot Area Color", (255, 255, 255))
                enable_y_stripes = _props_with_default(general, "Enable Y Axis Stripes", True)
                general_field_width = _props_with_default(general, "Field Width", 4)
                general_precision = _props_with_default(general, "Precision", 4)
                general_use_scientific_notation = _props_with_default(general, "Use Scientific Notation", True)
                self.edit_general_settings(
                    background_color=general_back_color,
                    plot_color=general_plot_color,
                    enable_y_stripes=enable_y_stripes,
                    field_width=general_field_width,
                    precision=general_precision,
                    use_scientific_notation=general_use_scientific_notation,
                )
            if "Header" in self.props["General"]:
                header = self.props["General"]["Header"]
                company_name = _props_with_default(header, "Company Name", "")
                show_design_name = _props_with_default(header, "Show Design Name", True)
                header_font = _props_with_default(header, "Font", "Arial")
                header_title_size = _props_with_default(header, "Title Height", 12)
                header_subtitle_size = _props_with_default(header, "Sub Title Height", 12)
                header_italic = _props_with_default(header, "Italic", False)
                header_bold = _props_with_default(header, "Bold", False)
                header_color = _props_with_default(header, "Color", (0, 0, 0))
                self.edit_header(
                    company_name=company_name,
                    show_design_name=show_design_name,
                    font=header_font,
                    title_size=header_title_size,
                    subtitle_size=header_subtitle_size,
                    italic=header_italic,
                    bold=header_bold,
                    color=header_color,
                )

            for i in list(self.props["General"].keys()):
                if "Axis" in i:
                    axis = self.props["General"][i]
                    axis_font = _props_with_default(axis, "Font", "Arial")
                    axis_size = _props_with_default(axis, "Height", 12)
                    axis_italic = _props_with_default(axis, "Italic", False)
                    axis_bold = _props_with_default(axis, "Bold", False)
                    axis_color = _props_with_default(axis, "Color", (0, 0, 0))
                    axis_label = _props_with_default(axis, "Label")
                    axis_linear_scaling = (
                        True if _props_with_default(axis, "Axis Scaling", "Linear") == "Linear" else False
                    )
                    axis_min_scale = _props_with_default(axis, "Min")
                    axis_max_scale = _props_with_default(axis, "Max")
                    axis_min_trick_div = _props_with_default(axis, "Minor Tick Divs", 5)
                    specify_spacing = _props_with_default(axis, "Specify Spacing", True)
                    if not specify_spacing:
                        axis_min_spacing = None
                    else:
                        axis_min_spacing = _props_with_default(axis, "Spacing")
                    axis_units = _props_with_default(axis, "Units")
                    if i == "AxisX":
                        self.edit_x_axis(
                            font=axis_font,
                            font_size=axis_size,
                            italic=axis_italic,
                            bold=axis_bold,
                            color=axis_color,
                            label=axis_label,
                        )
                        if self.report_category in ["Eye Diagram"]:
                            continue
                        self.edit_x_axis_scaling(
                            linear_scaling=axis_linear_scaling,
                            min_scale=axis_min_scale,
                            max_scale=axis_max_scale,
                            minor_tick_divs=axis_min_trick_div,
                            min_spacing=axis_min_spacing,
                            units=axis_units,
                        )
                    else:
                        self.edit_y_axis(
                            font=axis_font,
                            font_size=axis_size,
                            italic=axis_italic,
                            bold=axis_bold,
                            color=axis_color,
                            label=axis_label,
                        )
                        if self.report_category in ["Eye Diagram"]:
                            continue
                        self.edit_y_axis_scaling(
                            linear_scaling=axis_linear_scaling,
                            min_scale=axis_min_scale,
                            max_scale=axis_max_scale,
                            minor_tick_divs=axis_min_trick_div,
                            min_spacing=axis_min_spacing,
                            units=axis_units,
                            axis_name=i.replace("Axis", ""),
                        )

    @property
    def limit_lines(self):
        """Return the list of available limit lines in the report.

        .. note::
            This property works in version 2022 R1 and later. However, It works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        list of :class:`pyaedt.modules.report_templates.LimitLine`
        """
        _traces = []
        oo_names = self._post._app.get_oo_name(self._post.oreportsetup, self.plot_name)
        for el in oo_names:
            if "LimitLine" in el:
                _traces.append(LimitLine(self._post.oreportsetup, "{}:{}".format(self.plot_name, el)))

        return _traces

    @property
    def notes(self):
        """Return the list of available notes in the report.

        .. note::
            This property works in version 2022 R1 and later. However, It works only in
            non-graphical mode in version 2022 R2 and later.

        Returns
        -------
        List of :class:`pyaedt.modules.report_templates.Note`
        """
        _notes = []
        try:
            oo_names = self._post.oreportsetup.GetChildObject(self.plot_name).GetChildNames()
        except:
            return _notes
        for el in oo_names:
            if "Note" in el:
                _notes.append(Note(self._post.oreportsetup, "{}:{}".format(self.plot_name, el)))

        return _notes

    @property
    def plot_name(self):
        """Set/Get the Plot Name.

        Returns
        -------
        str
        """
        return self.props["Plot Name"]

    @plot_name.setter
    def plot_name(self, name):
        self.props["Plot Name"] = name
        self._is_created = False

    @property
    def variations(self):
        """Get and Set the Variations.

        Returns
        -------
        str
        """
        return self.props["Context"]["Variations"]

    @variations.setter
    def variations(self, value):
        self.props["Context"]["Variations"] = value

    @property
    def primary_sweep(self):
        """Return the Report Primary Sweep.

        Returns
        -------
        str
        """
        return self.props["Context"]["Primary Sweep"]

    @primary_sweep.setter
    def primary_sweep(self, val):
        if val == self.props["Context"].get("Secondary Sweep", None):
            self.props["Context"]["Secondary Sweep"] = self.props["Context"]["Primary Sweep"]
        self.props["Context"]["Primary Sweep"] = val
        if val == "Time":
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif val == "Freq":
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def secondary_sweep(self):
        """Return the Report (optional) Secondary Sweep.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Secondary Sweep", None)

    @secondary_sweep.setter
    def secondary_sweep(self, val):
        if val == self.props["Context"]["Primary Sweep"]:
            self.props["Context"]["Primary Sweep"] = self.props["Context"]["Secondary Sweep"]
        self.props["Context"]["Secondary Sweep"] = val
        if val == "Time":
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif val == "Freq":
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @property
    def primary_sweep_range(self):
        """Return the Report Primary Sweep Range.

        Returns
        -------
        str
        """
        return self.props["Context"]["Primary Sweep Range"]

    @primary_sweep_range.setter
    def primary_sweep_range(self, val):
        self.props["Context"]["Primary Sweep Range"] = val

    @property
    def secondary_sweep_range(self):
        """Return the Report Secondary Sweep Range.

        Returns
        -------
        str
        """
        return self.props["Context"]["Secondary Sweep Range"]

    @secondary_sweep_range.setter
    def secondary_sweep_range(self, val):
        self.props["Context"]["Secondary Sweep Range"] = val

    @property
    def _context(self):
        return []

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            expr = self.expressions
        else:
            expr = [self.expressions]
        arg = ["X Component:=", self.primary_sweep, "Y Component:=", expr]
        if self.report_type in ["3D Polar Plot", "3D Spherical Plot"]:
            arg = [
                "Phi Component:=",
                self.primary_sweep,
                "Theta Component:=",
                self.secondary_sweep,
                "Mag Component:=",
                expr,
            ]
        elif self.report_type == "Radiation Pattern":
            arg = ["Ang Component:=", self.primary_sweep, "Mag Component:=", expr]
        elif self.report_type in ["Smith Chart", "Polar Plot"]:
            arg = ["Polar Component:=", expr]
        elif self.report_type == "Rectangular Contour Plot":
            arg = [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self.secondary_sweep,
                "Z Component:=",
                expr,
            ]
        return arg

    @property
    def domain(self):
        """Get/Set the Plot Domain.

        Returns
        -------
        str
        """
        return self.props["Context"]["Domain"]

    @domain.setter
    def domain(self, domain):
        self.props["Context"]["Domain"] = domain
        if self._post._app.design_type in ["Maxwell 3D", "Maxwell 2D"]:
            return
        if self.primary_sweep == "Freq" and domain == "Time":
            self.primary_sweep = "Time"
            self.variations.pop("Freq", None)
            self.variations["Time"] = ["All"]
        elif self.primary_sweep == "Time" and domain == "Sweep":
            self.primary_sweep = "Freq"
            self.variations.pop("Time", None)
            self.variations["Freq"] = ["All"]

    @pyaedt_function_handler()
    def _convert_dict_to_report_sel(self, sweeps):
        if not sweeps:
            return []
        sweep_list = []
        if self.primary_sweep:
            sweep_list.append(self.primary_sweep + ":=")
            if self.primary_sweep_range == ["All"] and self.primary_sweep in self.variations:
                sweep_list.append(self.variations[self.primary_sweep])
            else:
                sweep_list.append(self.primary_sweep_range)
        if self.secondary_sweep:
            sweep_list.append(self.secondary_sweep + ":=")
            if self.secondary_sweep_range == ["All"] and self.secondary_sweep in self.variations:
                sweep_list.append(self.variations[self.primary_sweep])
            else:
                sweep_list.append(self.secondary_sweep_range)
        for el in sweeps:
            if el in [self.primary_sweep, self.secondary_sweep]:
                continue
            sweep_list.append(el + ":=")
            if type(sweeps[el]) is list:
                sweep_list.append(sweeps[el])
            else:
                sweep_list.append([sweeps[el]])
        for el in list(self._post._app.available_variations.nominal_w_values_dict.keys()):
            if el not in sweeps:
                sweep_list.append(el + ":=")
                sweep_list.append(["Nominal"])
        return sweep_list

    @pyaedt_function_handler()
    def create(self, plot_name=None):
        """Create a new Report.

        Parameters
        ----------
        plot_name : str, optional
            Set optionally the plot name

        Returns
        -------
        Bool
        """
        if not plot_name:
            if self._is_created:
                self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = plot_name
        if self.setup not in self._post._app.existing_analysis_sweeps and "AdaptivePass" not in self.setup:
            self._post._app.logger.error("Setup doesn't exist in this design.")
            return False
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
        )
        self._post.plots.append(self)
        self._is_created = True
        return True

    @pyaedt_function_handler()
    def get_solution_data(self):
        """Get the Report solution Data.

        Returns
        -------
        :class:`pyaedt.modules.PostProcessor.SolutionData`
            `Solution Data object.
        """
        solution_data = self._post.get_solution_data_per_variation(
            self.report_category, self.setup, self._context, self.variations, self.expressions
        )
        if self.primary_sweep:
            solution_data.primary_sweep = self.primary_sweep
        if not solution_data:
            self._post._app.logger.error("No Data Available. Check inputs")
            return False
        return solution_data

    @pyaedt_function_handler()
    def add_limit_line_from_points(self, x_list, y_list, x_units="", y_units="", y_axis="Y1"):  # pragma: no cover
        """Add a Cartesian Limit Line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        x_list : list
            List of float inputs.
        y_list : list
            List of float y values.
        x_units : str
            x list units.
        y_units : str
            y list units.
        y_axis : int, optional
            Y axis. Default is `"Y1"`.

        Returns
        -------
        bool
        """
        x_list = [GeometryOperators.parse_dim_arg(str(i) + x_units) for i in x_list]
        y_list = [GeometryOperators.parse_dim_arg(str(i) + y_units) for i in y_list]
        if self.plot_name and self._is_created:
            xvals = ["NAME:XValues"]
            xvals.extend(x_list)
            yvals = ["NAME:YValues"]
            yvals.extend(y_list)
            self._post.oreportsetup.AddCartesianLimitLine(
                self.plot_name,
                [
                    "NAME:CartesianLimitLine",
                    xvals,
                    "XUnits:=",
                    x_units,
                    yvals,
                    "YUnits:=",
                    y_units,
                    "YAxis:=",
                    y_axis,
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_limit_line_from_equation(
        self, start_x, stop_x, step, equation="x", units="GHz", y_axis=1
    ):  # pragma: no cover
        """Add a Cartesian Limit Line from point lists. This method works only in graphical mode.

        Parameters
        ----------
        start_x : float
            Start X value.
        stop_x : float
            Stop X value.
        step : float
            X step value.
        equation : str
            Y equation to apply. Default is Y=X.
        units : str
            X axis units. Default is "GHz".
        y_axis : str, int, optional
            Y axis. Default is `1`.

        Returns
        -------
        bool
        """
        if self.plot_name and self._is_created:
            self._post.oreportsetup.AddCartesianLimitLineFromEquation(
                self.plot_name,
                [
                    "NAME:CartesianLimitLineFromEquation",
                    "YAxis:=",
                    int(str(y_axis).replace("Y", "")),
                    "Start:=",
                    self._post._app.value_with_units(start_x, units),
                    "Stop:=",
                    self._post._app.value_with_units(stop_x, units),
                    "Step:=",
                    self._post._app.value_with_units(step, units),
                    "Equation:=",
                    equation,
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_note(self, text, x_position=0, y_position=0):  # pragma: no cover
        """Add a note at position.

        Parameters
        ----------
        text : string
            The text of the note.
        x_position : float
            x position of the note.
        y_position : float
            y position of the note.
        note_name : string
            internal name of the note (optional).

        Returns
        -------
        bool
        """
        noteName = generate_unique_name("Note", n=3)
        if self.plot_name and self._is_created:
            self._post.oreportsetup.AddNote(
                self.plot_name,
                [
                    "NAME:NoteDataSource",
                    [
                        "NAME:NoteDataSource",
                        "SourceName:=",
                        noteName,
                        "HaveDefaultPos:=",
                        True,
                        "DefaultXPos:=",
                        x_position,
                        "DefaultYPos:=",
                        y_position,
                        "String:=",
                        text,
                    ],
                ],
            )
            return True
        return False

    @pyaedt_function_handler()
    def add_cartesian_x_marker(self, val, name=None):  # pragma: no cover
        """Add a cartesian X Marker. This method works only in graphical mode.

        Parameters
        ----------
        val : str
            Value to apply with units.
        name : str, optional
            Marker Name

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MX")
            self._post.oreportsetup.AddCartesianXMarker(self.plot_name, name, GeometryOperators.parse_dim_arg(val))
            return name
        return ""

    @pyaedt_function_handler()
    def add_cartesian_y_marker(self, val, name=None, y_axis=1):  # pragma: no cover
        """Add a cartesian Y Marker. This method works only in graphical mode.

        Parameters
        ----------
        val : str, float
            Value to apply with units.
        name : str, optional
            Marker Name
        y_axis : str, optional
            Y axis. Default is `"Y1"`.

        Returns
        -------
        str
            Marker name if created.
        """
        if not name:
            name = generate_unique_name("MY")
            self._post.oreportsetup.AddCartesianYMarker(
                self.plot_name, name, "Y{}".format(y_axis), GeometryOperators.parse_dim_arg(val), ""
            )
            return name
        return ""

    @pyaedt_function_handler()
    def _change_property(self, tabname, property_name, property_val):
        if not self._is_created:
            self._post._app.logger.error("Plot has not been created. Create it and then change the properties.")
            return False
        arg = [
            "NAME:AllTabs",
            ["NAME:" + tabname, ["NAME:PropServers", "{}:{}".format(self.plot_name, property_name)], property_val],
        ]
        self._post.oreportsetup.ChangeProperty(arg)
        return True

    @pyaedt_function_handler()
    def edit_grid(
        self,
        minor_x=True,
        minor_y=True,
        major_x=True,
        major_y=True,
        style_minor="Solid",
        style_major="Solid",
        minor_color=(0, 0, 0),
        major_color=(0, 0, 0),
    ):
        """Edit Plot Grid Settings.

        Parameters
        ----------
        minor_x : bool, optional
            Enable or Disable Minor X Grid. Default is `True`.
        minor_y : bool, optional
            Enable or Disable Minor Y Grid. Default is `True`.
        major_x : bool, optional
            Enable or Disable Major X Grid. Default is `True`.
        major_y : bool, optional
            Enable or Disable Major Y Grid. Default is `True`.
        style_minor : str, optional
            Minor Grid Style. Default is `"Solid"`.
        style_major : str, optional
            Major Grid Style. Default is `"Solid"`.
        minor_color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
        major_color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
        Returns
        -------
        bool
        """
        props = ["NAME:ChangedProps"]
        props.append(["NAME:Show minor X grid", "Value:=", minor_x])
        props.append(["NAME:Show minor Y grid", "Value:=", minor_y])
        props.append(["NAME:Show major X grid", "Value:=", major_x])
        props.append(["NAME:Show major Y grid", "Value:=", major_y])
        props.append(["NAME:Minor grid line style", "Value:=", style_minor])
        props.append(["NAME:Major grid line style", "Value:=", style_major])
        props.append(
            ["NAME:Minor grid line color", "R:=", minor_color[0], "G:=", minor_color[1], "B:=", minor_color[2]]
        )
        props.append(
            ["NAME:Major grid line color", "R:=", major_color[0], "G:=", major_color[1], "B:=", major_color[2]]
        )
        return self._change_property("Grid", "Grid", props)

    @pyaedt_function_handler()
    def edit_x_axis(self, font="Arial", font_size=12, italic=False, bold=False, color=(0, 0, 0), label=None):
        """Edit X Axis  Settings.

        Parameters
        ----------
        font : str, optional
            Font Name. Default is `"Arial"`.
        font_size : int, optional
            Font title size. Default is `12`.
        italic : bool, optional
            Enable or Disable italic. Default is `True`.
        bold : bool, optional
            Enable or Disable bold. Default is `True`.
        color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
        label : str, optional
            Axis plot name.

        Returns
        -------
        bool
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Text Font",
                "Height:=",
                -1 * font_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
        ]
        if label:
            props.append(["NAME:Name", "Value:=", label])
        props.append(["NAME:Axis Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property("Axis", "AxisX", props)

    @pyaedt_function_handler()
    def edit_x_axis_scaling(
        self, linear_scaling=True, min_scale=None, max_scale=None, minor_tick_divs=5, min_spacing=None, units=None
    ):
        """Edit X Axis Scaling Settings.

        Parameters
        ----------
        linear_scaling : bool, optional
            Either if Linear or Log Scale will be used. Default is `True`.
        min_scale : str, optional
            Minimum scale value with units.
        max_scale : str, optional
            Maximum scale value with units.
        minor_tick_divs : int, optional
            Min Tick division. Default 5.
        min_spacing : str, optional
            Min spacing with units.
        units :str, optional
            Units in plot.

        Returns
        -------
        bool
        """
        if linear_scaling:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Linear"]]
        else:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Log"]]
        if min_scale:
            props.append(["NAME:Min", "Value:=", min_scale])
        if max_scale:
            props.append(["NAME:Max", "Value:=", max_scale])
        if minor_tick_divs:
            props.append(["NAME:Minor Tick Divs", "Value:=", str(minor_tick_divs)])
        if min_spacing:
            props.append(["NAME:Spacing", "Value:=", min_spacing])
        if units:
            props.append(["NAME:Units", "Value:=", units])
        return self._change_property("Scaling", "AxisX", props)

    @pyaedt_function_handler()
    def edit_legend(
        self,
        show_solution_name=True,
        show_variation_key=True,
        show_trace_name=True,
        back_color=(255, 255, 255),
        font_color=(0, 0, 0),
    ):
        """Edit the plot Legend.

        Parameters
        ----------
        show_solution_name : bool, optional
            Either if Show or hide the Solution Name.
        show_variation_key : bool, optional
            Either if Show or hide the Variation key.
        show_trace_name : bool, optional
            Either if Show or hide the Trace Name.
        back_color : tuple, optional
            Legend Background Color.
        font_color : tuple, optional
            Legend Font Color.
        Returns
        -------

        """
        props = [
            "NAME:ChangedProps",
            ["NAME:Show Solution Name", "Value:=", show_solution_name],
            ["NAME:Show Variation Key", "Value:=", show_variation_key],
            ["NAME:Show Trace Name", "Value:=", show_trace_name],
            ["NAME:Back Color", "R:=", back_color[0], "G:=", back_color[1], "B:=", back_color[2]],
            ["NAME:Font", "R:=", font_color[0], "G:=", font_color[1], "B:=", font_color[2]],
        ]
        return self._change_property("Legend", "Legend", props)

    @pyaedt_function_handler()
    def edit_y_axis(
        self, axis_name="Y1", font="Arial", font_size=12, italic=False, bold=False, color=(0, 0, 0), label=None
    ):
        """Edit Y Axis Settings.

        Parameters
        ----------
        axis_name : str, optional
            Name of Axis. Default is `"Y1"` main Y axis.
        font : str, optional
            Font Name. Default is `"Arial"`.
        font_size : int, optional
            Font title size. Default is `12`.
        italic : bool, optional
            Enable or Disable italic. Default is `True`.
        bold : bool, optional
            Enable or Disable bold. Default is `True`.
        color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
                linear_scaling : bool, optional
            Either if Linear or Log Scale will be used. Default is `True`.
        label : str, optional
            Y axis label.
        Returns
        -------
        bool
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Text Font",
                "Height:=",
                -1 * font_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
        ]
        if label:
            props.append(["NAME:Name", "Value:=", label])
        props.append(["NAME:Axis Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property("Axis", "Axis" + axis_name, props)

    @pyaedt_function_handler()
    def edit_y_axis_scaling(
        self,
        axis_name="Y1",
        linear_scaling=True,
        min_scale=None,
        max_scale=None,
        minor_tick_divs=5,
        min_spacing=None,
        units=None,
    ):
        """Edit Y Axis Scaling Settings.

        Parameters
        ----------
        linear_scaling : bool, optional
            Either if Linear or Log Scale will be used. Default is `True`.
        min_scale : str, optional
            Minimum scale value with units.
        max_scale : str, optional
            Maximum scale value with units.
        minor_tick_divs : int, optional
            Min Tick division. Default 5.
        min_spacing : str, optional
            Min spacing with units.
        units :str, optional
            Units in plot.
        Returns
        -------
        bool
        """
        if linear_scaling:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Linear"]]
        else:
            props = ["NAME:ChangedProps", ["NAME:Axis Scaling", "Value:=", "Log"]]
        if min_scale:
            props.append(["NAME:Min", "Value:=", min_scale])
        if max_scale:
            props.append(["NAME:Max", "Value:=", max_scale])
        if minor_tick_divs:
            props.append(["NAME:Minor Tick Divs", "Value:=", str(minor_tick_divs)])
        if min_spacing:
            props.append(["NAME:Spacing", "Value:=", min_spacing])
        if units:
            props.append(["NAME:Units", "Value:=", units])
        return self._change_property("Scaling", "Axis" + axis_name, props)

    @pyaedt_function_handler()
    def edit_general_settings(
        self,
        background_color=(255, 255, 255),
        plot_color=(255, 255, 255),
        enable_y_stripes=True,
        field_width=4,
        precision=4,
        use_scientific_notation=True,
    ):
        """Edit Plot General Settings.

        Parameters
        ----------
        background_color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
        plot_color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).
        enable_y_stripes : bool, optional
            Enable/Disable Y Stripes.
        field_width : int, optional
            Field Width. Default is `4`.
        precision : int, optional
            Field Precision. Default is `4`.
        use_scientific_notation : bool, optional
            Either if Enable Scientific notation. Default is `True`.

        Returns
        -------
        bool
        """
        props = [
            "NAME:ChangedProps",
            ["NAME:Back Color", "R:=", background_color[0], "G:=", background_color[1], "B:=", background_color[2]],
            ["NAME:Plot Area Color", "R:=", plot_color[0], "G:=", plot_color[1], "B:=", plot_color[2]],
            ["NAME:Enable Y Axis Stripes", "Value:=", enable_y_stripes],
            ["NAME:Field Width", "Value:=", str(field_width)],
            ["NAME:Precision", "Value:=", str(precision)],
            ["NAME:Use Scientific Notation", "Value:=", use_scientific_notation],
        ]
        return self._change_property("General", "General", props)

    @pyaedt_function_handler()
    def edit_header(
        self,
        company_name="PyAEDT",
        show_design_name=True,
        font="Arial",
        title_size=12,
        subtitle_size=12,
        italic=False,
        bold=False,
        color=(0, 0, 0),
    ):
        """Edit Chart Header.

        Parameters
        ----------
        company_name : str, optional
            Company Name.
        show_design_name : bool, optional
            Either if Show Design Name in plot.
        font : str, optional
            Font Name. Default is `"Arial"`.
        title_size : int, optional
            Font title size. Default is `12`.
        subtitle_size : int, optional
            Font subtitle size. Default is `12`.
        italic : bool, optional
            Enable or Disable italic. Default is `True`.
        bold : bool, optional
            Enable or Disable bold. Default is `True`.
        color : tuple, optional
            Tuple (R, G, B) color. Every item has to be an integer in range (0,255).

        Returns
        -------
        bool
        """
        props = [
            "NAME:ChangedProps",
            [
                "NAME:Title Font",
                "Height:=",
                -1 * title_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
            [
                "NAME:Sub Title Font",
                "Height:=",
                -1 * subtitle_size - 2,
                "Width:=",
                0,
                "Escapement:=",
                0,
                "Orientation:=",
                0,
                "Weight:=",
                700 if bold else 400,
                "Italic:=",
                255 if italic else 0,
                "Underline:=",
                0,
                "StrikeOut:=",
                0,
                "CharSet:=",
                0,
                "OutPrecision:=",
                3,
                "ClipPrecision:=",
                2,
                "Quality:=",
                1,
                "PitchAndFamily:=",
                34,
                "FaceName:=",
                font,
                "R:=",
                color[0],
                "G:=",
                color[1],
                "B:=",
                color[2],
            ],
            ["NAME:Company Name", "Value:=", company_name],
            ["NAME:Show Design Name", "Value:=", show_design_name],
        ]
        return self._change_property("Header", "Header", props)


class Standard(CommonReport):
    """Provides a reporting class that fits most of the application's standard reports."""

    def __init__(self, app, report_category, setup_name):
        CommonReport.__init__(self, app, report_category, setup_name)

    @property
    def sub_design_id(self):
        """Get and Set the sub design id for Circuit and HFSS3DLayout subdesigns.

        Returns
        -------
        int
        """
        return self.props["Context"].get("Sub Design ID", None)

    @sub_design_id.setter
    def sub_design_id(self, value):
        self.props["Context"]["Sub Design ID"] = value

    @property
    def time_start(self):
        """Get and Set the time start value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["Context"]["Time Start"] = value

    @property
    def time_stop(self):
        """Get and Set the time stop value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["Context"]["Time Stop"] = value

    @property
    def _did(self):
        if self.domain == "Sweep":
            return 3
        else:
            return 1

    @property
    def _context(self):
        ctxt = []
        if self._post.post_solution_type in ["TR", "AC", "DC"]:
            ctxt = [
                "NAME:Context",
                "SimValueContext:=",
                [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0],
            ]
        elif self._post._app.design_type in ["Q3D Extractor", "2D Extractor"]:
            if not self.matrix:
                ctxt = ["Context:=", "Original"]
            else:
                ctxt = ["Context:=", self.matrix]
        elif self._post.post_solution_type in ["HFSS3DLayout"]:
            if self.differential_pairs:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [
                        self._did,
                        0,
                        2,
                        0,
                        False,
                        False,
                        -1,
                        1,
                        0,
                        1,
                        1,
                        "",
                        0,
                        0,
                        "EnsDiffPairKey",
                        False,
                        "1",
                        "IDIID",
                        False,
                        "1",
                    ],
                ]
            else:
                ctxt = [
                    "NAME:Context",
                    "SimValueContext:=",
                    [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"],
                ]
        elif self._post.post_solution_type in ["NexximLNA", "NexximTransient"]:
            ctxt = ["NAME:Context", "SimValueContext:=", [self._did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0]]
            if self.sub_design_id:
                ctxt_temp = ["NUMLEVELS", False, "1", "SUBDESIGNID", False, str(self.sub_design_id)]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.differential_pairs:
                ctxt_temp = ["USE_DIFF_PAIRS", False, "1"]
                for el in ctxt_temp:
                    ctxt[2].append(el)
            if self.domain == "Time":
                if self.time_start:
                    ctxt[2].extend(["WS", False, self.time_start])
                if self.time_stop:
                    ctxt[2].extend(["WE", False, self.time_stop])
        elif self.differential_pairs:
            ctxt = ["Diff:=", "Differential Pairs", "Domain:=", self.domain]
        else:
            ctxt = ["Domain:=", self.domain]
        return ctxt


class AntennaParameters(Standard):
    """Provides a reporting class that fits Antenna Parameters reports in HFSS plot."""

    def __init__(self, app, report_category, setup_name, far_field_sphere=None):
        Standard.__init__(self, app, report_category, setup_name)
        self.far_field_sphere = far_field_sphere

    @property
    def far_field_sphere(self):
        """Get and Set the Far Field Sphere name.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Far Field Sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self.props["Context"]["Far Field Sphere"] = value

    @property
    def _context(self):
        ctxt = ["Context:=", self.far_field_sphere]
        return ctxt


class Fields(CommonReport):
    """General Fields Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
        self.polyline = None
        self.point_number = 1001
        self.primary_sweep = "Distance"

    @property
    def point_number(self):
        """Get and Set the number of polygon Point number.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Points Number", None)

    @point_number.setter
    def point_number(self, value):
        self.props["Context"]["Points Number"] = value

    @property
    def _context(self):
        ctxt = ["Context:=", self.polyline]
        ctxt.append("PointCount:=")
        ctxt.append(self.point_number)
        return ctxt


class NearField(CommonReport):
    """Near Field Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"

    @property
    def _context(self):
        return ["Context:=", self.near_field]

    @property
    def near_field(self):
        """Get and Set the Near Field name.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Near Field Setup", None)

    @near_field.setter
    def near_field(self, value):
        self.props["Context"]["Near Field Setup"] = value


class FarField(CommonReport):
    """FarField Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"
        self.primary_sweep = "Phi"
        self.secondary_sweep = "Theta"
        if not "Phi" in self.variations:
            self.variations["Phi"] = ["All"]
        if not "Theta" in self.variations:
            self.variations["Theta"] = ["All"]
        if not "Freq" in self.variations:
            self.variations["Freq"] = ["Nominal"]

    @property
    def far_field_sphere(self):
        """Get and Set the Far Field Sphere name.

        Returns
        -------
        str
        """
        return self.props.get("Far Field Sphere", None)

    @far_field_sphere.setter
    def far_field_sphere(self, value):
        self.props["Far Field Sphere"] = value

    @property
    def _context(self):
        return ["Context:=", self.far_field_sphere]


class EyeDiagram(CommonReport):
    """Eye Diagram Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Time"
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.unit_interval = "0s"
        self.offset = "0ms"
        self.auto_delay = True
        self.manual_delay = "0ps"
        self.auto_cross_amplitude = True
        self.cross_amplitude = "0mV"
        self.auto_compute_eye_meas = True
        self.eye_measurement_point = "5e-10s"
        self.thinning = False
        self.dy_dx_tolerance = 0.001
        self.thinning_points = 500000000

    @property
    def time_start(self):
        """Get and Set the time start value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["Context"]["Time Start"] = value

    @property
    def time_stop(self):
        """Get and Set the time stop value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["Context"]["Time Stop"] = value

    @property
    def unit_interval(self):
        """Get and Set the unit interval value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Unit Interval", None)

    @unit_interval.setter
    def unit_interval(self, value):
        self.props["Context"]["Unit Interval"] = value

    @property
    def offset(self):
        """Get and Set the offset value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Offset", None)

    @offset.setter
    def offset(self, value):
        self.props["Context"]["Offset"] = value

    @property
    def auto_delay(self):
        """Get and Set the autodelay flag.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Auto Delay", None)

    @auto_delay.setter
    def auto_delay(self, value):
        self.props["Context"]["Auto Delay"] = value

    @property
    def manual_delay(self):
        """Get and Set the manual delay value in case auto_delay is set to False.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Manual Delay", None)

    @manual_delay.setter
    def manual_delay(self, value):
        self.props["Context"]["Manual Delay"] = value

    @property
    def auto_cross_amplitude(self):
        """Get and Set the auto cross ampltiude flag

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Auto Cross Amplitude", None)

    @auto_cross_amplitude.setter
    def auto_cross_amplitude(self, value):
        self.props["Context"]["Auto Cross Amplitude"] = value

    @property
    def cross_amplitude(self):
        """Get and Set the cross amplitude value in case auto_cross_amplitude flag is set to False.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Cross Amplitude", None)

    @cross_amplitude.setter
    def cross_amplitude(self, value):
        self.props["Context"]["Cross Amplitude"] = value

    @property
    def auto_compute_eye_meas(self):
        """Get and Set the  flag is to automatically compute eye measurements.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Auto Compute Eye Measurements", None)

    @auto_compute_eye_meas.setter
    def auto_compute_eye_meas(self, value):
        self.props["Context"]["Auto Compute Eye Measurements"] = value

    @property
    def eye_measurement_point(self):
        """Get and Set the eye measurement point.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Eye Measurements Point", None)

    @eye_measurement_point.setter
    def eye_measurement_point(self, value):
        self.props["Context"]["Eye Measurements Point"] = value

    @property
    def thinning(self):
        """Get and Set the thinning flag.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Thinning", None)

    @thinning.setter
    def thinning(self, value):
        self.props["Context"]["Thinning"] = value

    @property
    def dy_dx_tolerance(self):
        """Get and DY DX tolerance.

        Returns
        -------
        float
        """
        return self.props["Context"].get("DY DX Tolerance", None)

    @dy_dx_tolerance.setter
    def dy_dx_tolerance(self, value):
        self.props["Context"]["DY DX Tolerance"] = value

    @property
    def thinning_points(self):
        """Get and Set the number of thinning points.

        Returns
        -------
        float
        """
        return self.props["Context"].get("Thinning Points", None)

    @thinning_points.setter
    def thinning_points(self, value):
        self.props["Context"]["Thinning Points"] = value

    @property
    def _context(self):
        if self.thinning:
            val = "1"
        else:
            val = "0"
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                1,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "DE",
                False,
                val,
                "DP",
                False,
                str(self.thinning_points),
                "DT",
                False,
                str(self.dy_dx_tolerance),
                "NUMLEVELS",
                False,
                "0",
                "WE",
                False,
                self.time_stop,
                "WM",
                False,
                "200ns",
                "WN",
                False,
                "0ps",
                "WS",
                False,
                self.time_start,
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return ["Component:=", self.expressions]
        else:
            return ["Component:=", [self.expressions]]

    @pyaedt_function_handler()
    def create(self, plot_name=None):
        """Create a new Eye Diagram Report.

        Parameters
        ----------
        plot_name : str, optional
            Optional Plot name.

        Returns
        -------
        bool
        """
        if not plot_name:
            if self._is_created:
                self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = plot_name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            self.report_category,
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            self._trace_info,
            [
                "Unit Interval:=",
                self.unit_interval,
                "Offset:=",
                self.offset,
                "Auto Delay:=",
                self.auto_delay,
                "Manual Delay:=",
                self.manual_delay,
                "AutoCompCrossAmplitude:=",
                self.auto_cross_amplitude,
                "CrossingAmplitude:=",
                self.cross_amplitude,
                "AutoCompEyeMeasurementPoint:=",
                self.auto_compute_eye_meas,
                "EyeMeasurementPoint:=",
                self.eye_measurement_point,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True

        return True

    @pyaedt_function_handler()
    def eye_mask(
        self,
        points,
        xunits="ns",
        yunits="mV",
        enable_limits=False,
        upper_limits=500,
        lower_limits=-500,
        color=(0, 255, 0),
        xoffset="0ns",
        yoffset="0V",
        transparency=0.3,
    ):
        """Create an eye diagram in the plot.

        Parameters
        ----------
        points : list
            Points of the eye mask in the format [[x1,y1,],[x2,y2],...].
        xunits : str, optional
            X points units. Default is `"ns"`.
        yunits :  str, optional
            Y points units. Default is `"mV"`.
        enable_limits : bool, optional
            Enable/Disable the upper and lower limits. Default is `False`.
        upper_limits float, optional
            Upper Limit if enabled. Default is `500"`.
        lower_limits str, optional
            Lower Limit if enabled. Default is `-500`.
        color : tuple, optional
            Mask color in (r,g,b) int.
        xoffset : str, optional
            Mask Time offset with units. Default is `"0ns"`.
        yoffset : str, optional
            Mask Value offset with units. Default is `"0V"`.
        transparency : float, optional
            Mask Transparency.  Default is `0.3`.

        Returns
        -------
        bool
        """
        props = [
            "NAME:AllTabs",
            ["NAME:Mask", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
        ]
        arg = [
            "NAME:Mask",
            "Version:=",
            1,
            "ShowLimits:=",
            enable_limits,
            "UpperLimit:=",
            upper_limits if upper_limits else 1,
            "LowerLimit:=",
            lower_limits if lower_limits else 0,
            "XUnits:=",
            xunits,
            "YUnits:=",
            yunits,
        ]
        mask_points = ["NAME:MaskPoints"]
        for point in points:
            mask_points.append(point[0])
            mask_points.append(point[1])
        arg.append(mask_points)
        args = ["NAME:ChangedProps", arg]
        args.append(["NAME:Mask Fill Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        args.append(["NAME:X Offset", "Value:=", xoffset])
        args.append(["NAME:Y Offset", "Value:=", yoffset])
        args.append(["NAME:Mask Trans", "Transparency:=", transparency])
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler()
    def rectangular_plot(self, value=True):
        """Enable/disable the rectangular plot on the chart.

        Parameters
        ----------
        value : bool
            `True` to enable the rectangular plot. `False` to disable. it

        Returns
        -------
        bool
        """
        props = [
            "NAME:AllTabs",
            ["NAME:Eye", ["NAME:PropServers", "{}:EyeDisplayTypeProperty".format(self.plot_name)]],
        ]
        args = ["NAME:ChangedProps", ["NAME:Rectangular Plot", "Value:=", value]]
        props[1].append(args)
        self._post.oreportsetup.ChangeProperty(props)

        return True

    @pyaedt_function_handler()
    def add_all_eye_measurements(self):
        """Add all Eye measurements to the plot.

        Returns
        -------
        bool
        """
        self._post.oreportsetup.AddAllEyeMeasurements(self.plot_name)
        return True

    @pyaedt_function_handler()
    def clear_all_eye_measurements(self):
        """Clear all the Eye measurements from the plot.

        Returns
        -------
        bool
        """
        self._post.oreportsetup.ClearAllTraceCharacteristics(self.plot_name)
        return True

    @pyaedt_function_handler()
    def add_trace_characteristics(self, trace_name, arguments=None, range=None):
        """Add a trace characteristic to the plot.

        Parameters
        ----------
        trace_name : str
            Name of the trace Characteristics.
        arguments : list, optional
            Arguments if exists.
        range : list, optional
            Output range. Default is Full range.

        Returns
        -------
        bool
        """
        if not arguments:
            arguments = []
        if not range:
            range = ["Full"]
        self._post.oreportsetup.AddTraceCharacteristics(self.plot_name, trace_name, arguments, range)
        return True

    @pyaedt_function_handler()
    def export_mask_violation(self, out_file=None):
        """Export the Eye Diagram mask violations to a tab file.

        Parameters
        ----------
        out_file : str, optional
            Full path to the export file (.tab). Default is `None` to export in working_directory.

        Returns
        -------
        str
            Output file path if created.
        """
        if not out_file:
            out_file = os.path.join(self._post._app.working_directory, "{}_violations.tab".format(self.plot_name))
        self._post.oreportsetup.ExportEyeMaskViolation(self.plot_name, out_file)
        return out_file


class Emission(CommonReport):
    """Emission Report Class."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Sweep"


class Spectral(CommonReport):
    """Spectral Report from Transient data."""

    def __init__(self, app, report_type, setup_name):
        CommonReport.__init__(self, app, report_type, setup_name)
        self.domain = "Spectrum"
        self.algorithm = "FFT"
        self.time_start = "0ns"
        self.time_stop = "200ns"
        self.window = "Rectangular"
        self.kaiser_coeff = 0
        self.adjust_coherent_gain = True
        self.max_freq = "10MHz"
        self.plot_continous_spectrum = False
        self.primary_sweep = "Spectrum"

    @property
    def time_start(self):
        """Get and Set the time start value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Start", None)

    @time_start.setter
    def time_start(self, value):
        self.props["Context"]["Time Start"] = value

    @property
    def time_stop(self):
        """Get and Set the time stop value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Time Stop", None)

    @time_stop.setter
    def time_stop(self, value):
        self.props["Context"]["Time Stop"] = value

    @property
    def window(self):
        """Get and Set the windowing value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Window", None)

    @window.setter
    def window(self, value):
        self.props["Context"]["Window"] = value

    @property
    def kaiser_coeff(self):
        """Get and Set the kaiser value.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Kaiser Coefficient", None)

    @kaiser_coeff.setter
    def kaiser_coeff(self, value):
        self.props["Context"]["Kaiser Coefficient"] = value

    @property
    def adjust_coherent_gain(self):
        """Get and Set the coherent gain flag.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Adjust Choerent Gain", None)

    @adjust_coherent_gain.setter
    def adjust_coherent_gain(self, value):
        self.props["Context"]["Adjust Choerent Gain"] = value

    @property
    def plot_continous_spectrum(self):
        """Get and Set the continuous spectrum flag.

        Returns
        -------
        bool
        """
        return self.props["Context"].get("Plot Continuous Spectrum", None)

    @plot_continous_spectrum.setter
    def plot_continous_spectrum(self, value):
        self.props["Context"]["Plot Continuous Spectrum"] = value

    @property
    def max_frequency(self):
        """Get and Set the max spectrum  frequency.

        Returns
        -------
        str
        """
        return self.props["Context"].get("Maximum Frequency", None)

    @max_frequency.setter
    def max_frequency(self, value):
        self.props["Context"]["Maximum Frequency"] = value

    @property
    def _context(self):
        if self.algorithm == "FFT":
            it = "1"
        elif self.algorithm == "Fourier Integration":
            it = "0"
        else:
            it = "2"
        WT = {
            "Rectangular": "0",
            "Bartlett": "1",
            "Blackman": "2",
            "Hamming": "3",
            "Hanning": "4",
            "Kaiser": "5",
            "Welch": "6",
            "Weber": "7",
            "Lanzcos": "8",
        }
        wt = WT[self.window]
        arg = [
            "NAME:Context",
            "SimValueContext:=",
            [
                2,
                0,
                2,
                0,
                False,
                False,
                -1,
                1,
                0,
                1,
                1,
                "",
                0,
                0,
                "CP",
                False,
                "1" if self.plot_continous_spectrum else "0",
                "IT",
                False,
                it,
                "MF",
                False,
                self.max_freq,
                "NUMLEVELS",
                False,
                "0",
                "TE",
                False,
                self.time_stop,
                "TS",
                False,
                self.time_start,
                "WT",
                False,
                wt,
                "WW",
                False,
                "100",
                "KP",
                False,
                str(self.kaiser_coeff),
                "CG",
                False,
                "1" if self.adjust_coherent_gain else "0",
            ],
        ]
        return arg

    @property
    def _trace_info(self):
        if isinstance(self.expressions, list):
            return self.expressions
        else:
            return [self.expressions]

    @pyaedt_function_handler()
    def create(self, plot_name=None):
        """Create a new Eye Diagram Report.

        Parameters
        ----------
        plot_name : str, optional
            Optional Plot name.

        Returns
        -------
        bool
        """
        if not plot_name:
            if self._is_created:
                self.plot_name = generate_unique_name("Plot")
        else:
            self.plot_name = plot_name
        self._post.oreportsetup.CreateReport(
            self.plot_name,
            "Standard",
            self.report_type,
            self.setup,
            self._context,
            self._convert_dict_to_report_sel(self.variations),
            [
                "X Component:=",
                self.primary_sweep,
                "Y Component:=",
                self._trace_info,
            ],
        )
        self._post.plots.append(self)
        self._is_created = True
        return True
