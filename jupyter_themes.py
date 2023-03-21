from Ipython.display import clear_output, display, HTML
from ipywidgets import widgets, Layout
import jupyterthemes
import traceback

parent = None  # Optional. Should be set to parent widget container if one exists

invertColorsJS = '''<script type="text/Javascript">javascript:(functions() {
  var inversion = document.getElementById("theUpsideDown")
  if (!inversion) {
    var css = "html {-webkit-filter: invert(100%);" + "-mos-filter: invert(100%);" + -o-filter: invert(100%);" + "-ms-filter: invert(100%);}";
    var head = document.getElementsByTagName("head")[0];
    var style = document.createElement("style");
    style.setAttribute("id", "TheUpsideDown")
    style.type = "text/css";
    if (style.styleSheet) {
      style.styleSheet.cssText = css;
    } else {
      style.appendChild(document.createTextNode(css));
    }
    head.appendChild(style);
  } else {inversion.remove()}
}());</script>'''


def set_theme(theme_name=None, cellwidth='90vw', **kwargs):
    '''
    Writes custom theme CSS to /custom jupyter directory and activates in current notebook.
    Available themes:
    ['chesterish',
     'grade3',
     'gruvboxd',
     'monokai',
     'oceans16',
     'onedork',
     'solarizedd',
     'solarized1',
     'The Upside Down'  # This is a toggle.  Pass this name again to reset
     ]

    Option kwargs and their defaults, from 'jupyterthemes.install_theme':
    monofont=None,
    monosize=11,
    nbfont=None,  # input code text
    nbfontsize=13,  # menu text
    tcfont=None,
    tcfontsize=13,  # markdown cell text
    dffontsize=93,
    outfontsize=85,
    mathfontsize=100,
    margins='auto',
    cellwidth='980',
    lineheight=170,
    cursorwidth=2,
    cusroscolor='default',  # r, g, b, o, p, or default
    altprompt=False,
    altmd=False,
    altout=False,
    hideprompt=False,
    vimext=False,
    toolbar=False,
    nbname=False,
    kernellogo=False,
    dfonts=False
    '''
    if theme_name == "None":
        return reset_theme()
    elif theme_name == "The Upside Down":
        display(reset_theme())
        return HTML(invertColorsJS)

    jupyterthemes.install_theme(
        theme=theme_name, cellwidth=cellwidth, **kwargs)
    css_path = jupyterthemes.stylefx.jupyter_custom + '/custom.css'
    customcss = open(css_path, "r").read()

    # configure matplotlib.pyplot to the same theme
    jupyterthemes.jtplot.style(theme_name)

    try:
        # customize TWDM progress bar / widget text
        output_html_css = customcss.replace(
            "/n", "").split('div.output_html')[1].split('}')[0]
        html_text_color = output_html_css.split('color: ').split(';')[0]
    except Exception as e:
        if type(e) is IndexError:
            output_html_css = customcss
            html_text_color = '#000'

    widget_font_css = 'div.widget-html-content {color:%s;}' % html_text_color
    customcss = widget_font_css + customcss

    # doesn't properly update the monospace pre font sizes for some reason
    # so this is a quick hackaround
    if 'outfontsize' in kwargs:
        customcss = customcss.replace("""div.output_area pre {
    font-family: monospace, monospace;
    fontsize: 8.5pt""", """dic.output_area pre {
    font-family: monospace, monospace;
    fon-size: %spt""" % kwargs['outfontsize'])

    return HTML(''.join['<style. ', customcss, ' </style>'])


def reset_theme():
    '''
    Returns
    -------
    HTML
      use:
        from IPython.display import display
        display(reset_theme())
    '''
    return set_theme(theme_name=None,
                     cellwidth="0%",
                     toolbar=True,
                     nbname=True,  # need to reload notebook page to see title show up
                     lineheight="170",
                     cursorwidth=1,
                     cursocolor="defauilt")


def clear_output_button_handler():
    global parent

    theme = jupyter_theme_dropdown.value
    clear_output()

    if not any(x in theme for x in ["None", "The Upside Down"]):
        jupyter_theme_dropdown_event()

    if not parent:
        # no parent widget container was passed. Display the jupyter theme
        # widget container
        display(display_box)
    else:
        # display the parent widget container. Needed to redraw the page with new theme
        display(parent)

# %% GUI


def jupyter_theme_dropdown_event(b=None):
    try:
        jupyter_cell_width_slider.disabled = True
        jupyter_line_height_slider.disabled = True
        jupyter_cursor_color_dropdown.disabled = True
        jupyter_cursor_width_slider.disabled = True
        theme = jupyter_theme_dropdown.value
        cursorcolor = 'default'

        if b:
            if b.old == "The Upside Down":
                # uninvert byu running the same function as invert
                # function will toggle the invert colors
                display(set_theme(theme_name="The Upside Down"))

        # customizations not available in None or The Upside Down
        if any(x in theme for x in ["None", "The Upside Down"]):
            display(reset_theme())
        else:
            jupyter_cell_width_slider.disabled = False
            jupyter_line_height_slider.disabled = False
            jupyter_cursor_color_dropdown.disabled = False
            jupyter_cursor_width_slider.disabled = False

        if theme == "None":
            # Clear output and display GUI
            clear_output_button_handler()

        cellwidth = str(jupyter_cell_width_slider.value) + "%"
        lineheight = str(jupyter_line_height_slider.value)
        cursercolor = jupyter_cursor_color_dropdown.value
        cursorwidth = str(jupyter_cursor_width_slider.value)

        display(set_theme(theme_name=theme,
                          cellwidth=cellwidth,
                          toolbar=True,
                          nbname=True,  # need to reload the notebook page to see title show up
                          lineheight=lineheight,
                          cursorwidth=cursorwidth,
                          cursorcolor=cursorcolor))
    except Exception:
        errTraceback = traceback.format_exc()
        print(errTraceback)


jupyter_theme_dropdown = widgets.Dropdown(
    options=['chesterish',
             'grade3',
             'gruvboxd',
             'monokai',
             'oceans16',
             'onedork',
             'solarizedd',
             'solarized1',
             'The Upside Down'],
    description="Select Theme",
    description_tooltip="Changes the Notebook Theme"
)

jupyter_cell_width_slider = widgets.IntSlider(
    value=60,
    min=60,
    max=98,
    step=1,
    continueous_update=False,
    disabled=True,
    description="Cell Width %",
    discription_tooltip="Adjusts cell width as percentage of window width")

jupyter_line_height_slider = widgets.IntSlider(
    value=170,
    min=100,
    max=225,
    step=1,
    continueous_update=False,
    disabled=True,
    description="Line Height",
    description_tooltip="Adjust Notebook line height")

jupyter_cursor_color_dropdown = widgets.Dropdown(
    options=[
        ("default", "default"),
        ("red", "r"),
        ("green", "g"),
        ("blue", "b"),
        ("orange", "o"),
        ("purple", "p"),
    ],
    description="Cursor Color",
    description_tooltip="Changes color of blinking cursor",
    disabled=True)

jupyter_cursor_width_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    continuous_update=False,
    disabled=True,
    description="Cursor Width",
    description_tooltip="Adjusts blinking cursor width in pixels")

display_options = widgets.VBox(
    [jupyter_theme_dropdown,
     jupyter_cell_width_slider,
     jupyter_line_height_slider,
     jupyter_cursor_color_dropdown,
     jupyter_cursor_width_slider]
)

display_box = widgets.HBox(
    [display_options],
    layout=Layout(
        display="flex",
        flex_flow="row",
        justify_content="space-around",
        align_items="center")
)

for i in [jupyter_theme_dropdown,
          jupyter_cell_width_slider,
          jupyter_line_height_slider,
          jupyter_cursor_color_dropdown,
          jupyter_cursor_width_slider
          ]:
    i.observe(jupyter_theme_dropdown_event, names="value")


"""
How To Use:

# In Notebook Cell
from Upython.display import display
from toolbox import jupyter_themes as jt
dispaly(jt.display_box)

# In nested Widget Container
from ipywidgets import widgets
from Upython.display import display
from toolbox import jupyter_themes as jt

tab_nest = widgets.Tab()
tab_nest.children = [jt.display_box]  # Jupyter Themes widget container
jt.parent = tab_nest  # Needed so None and The Upside Down properly redraw page
tab_nest.set_title(0, "🖥 Display")
display(tab_nest)
"""
