try:
    import matplotlib.widgets
except ImportError:
    pass

"""@package reflex_plot_widgets
This package allows easy interaction between plots using predefined widgets
"""


class CallableWidget :
    """This class is used as a base class for reflex widgets
    It will allow to add a hook to the callback function that is executed
    after the main callback functionality."""
    def __init__(self) :
        self.postcallback = None

    def setPostCallback(self, postcallback):
        self.postcallback = postcallback

    def postCallback(self, new_params):
        if(self.postcallback is not None) :
            self.postcallback(new_params)
            
class InteractiveCheckButtons(CallableWidget) :
    """This class will create a list of check buttons in a matplotlib canvas
    allowing the creator to specify a callback function to be called when
    any of the buttons is clicked or uncliked."""
    def __init__(self, axes, callback, labels, actives, title = None) :
        CallableWidget.__init__(self)
        self.cbuttons = matplotlib.widgets.CheckButtons(axes, labels, actives)
        if title is not None :
            axes.set_title(title, fontsize=12, fontweight='semibold')
        self.cbuttons.on_clicked(self.__callback)
        self.usercallback = callback        
        
    def __callback(self, label):
        new_params = self.usercallback(label)
        self.postCallback(new_params)

class InteractiveRadioButtons(CallableWidget) :
    """This class will create a list of radio buttons in a matplotlib canvas
    allowing the creator to specify a callback function to be called when
    a new radio button is selected."""
    def __init__(self, axes, callback, labels, active, 
                 textbkgcolors = None, title = None) :
        CallableWidget.__init__(self)
        if textbkgcolors is not None :
            if len(labels) != len(textbkgcolors) :
                raise Exception('Labels and and background colors sizes do not match')
            textlabels = list()
            for label, bkg in zip(labels, textbkgcolors) :
                text = matplotlib.text.Text(text=label, color = 'blue')
                textlabels.append(text)
        else:
            textlabels = labels
        if title is not None :
            axes.set_title(title, fontsize=12, fontweight='semibold')
        self.rbuttons = matplotlib.widgets.RadioButtons(axes, 
                                                        textlabels, active)
        self.rbuttons.on_clicked(self.__callback)
        self.usercallback = callback        
        
    def __callback(self, label):
        new_params = self.usercallback(label)
        self.postCallback(new_params)

class InteractiveClickableSubplot(CallableWidget) :
    """This class will create a widget that allows to click with the
       middle button of the mouse in an image and return the coordinates
       in a callback."""

    class AxesWidget(matplotlib.widgets.Widget):
        """NOTE: This class has been copied from matplotlib code 1.2.1 directly.
        matplotlib.widgets.AxesWidget was introduced in version 1.2.
        Once there is no reason to maintain versions of matplotlib older
        than 1.2, matplotlib.widgets.AxesWidget should be used directly.

        Widget that is connected to a single :class:`~matplotlib.axes.Axes`.

        Attributes:

        *ax* : :class:`~matplotlib.axes.Axes`
            The parent axes for the widget
        *canvas* : :class:`~matplotlib.backend_bases.FigureCanvasBase` subclass
            The parent figure canvas for the widget.
        *active* : bool
            If False, the widget does not respond to events.
        """
        def __init__(self, ax):
            self.ax = ax
            self.canvas = ax.figure.canvas
            self.cids = []
            self.active = True

        def connect_event(self, event, callback):
            """Connect callback with an event.

            This should be used in lieu of `figure.canvas.mpl_connect` since this
            function stores call back ids for later clean up.
            """
            cid = self.canvas.mpl_connect(event, callback)
            self.cids.append(cid)

        def disconnect_events(self):
            """Disconnect all events created by this widget."""
            for c in self.cids:
                self.canvas.mpl_disconnect(c)

        def ignore(self, event):
            """Return True if event should be ignored.

            This method (or a version of it) should be called at the beginning
            of any event callback.
            """
            return not self.active

    def __init__(self, axes, callback) :
        CallableWidget.__init__(self)
        #This is what should be used once the private AxesWidget is removed
        #self.axeswidget = matplotlib.widgets.AxesWidget(axes)
        self.axeswidget = self.AxesWidget(axes)
        self.axes = axes
        self.axeswidget.connect_event('button_press_event', self.__callback)
        self.usercallback = callback        

    def __callback(self, point):
        if point.button == 2 :
            if point.inaxes == self.axes : 
                new_params = self.usercallback(point)
                self.postCallback(new_params)

