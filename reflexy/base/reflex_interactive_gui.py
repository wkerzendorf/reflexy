import os
import sys
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import wx
from wx import xrc
import reflex_navigation_toolbar
matplotlib.interactive(False)

# This class presents the wx application interface


class ReflexInteractiveWxApp(wx.App):

    def __init__(self, interactive_app, dataPlotManager):
        self.inter_app = interactive_app
        self.dataPlotManager = dataPlotManager

        # Initialize wx GUI application
        wx.App.__init__(self, 0)

    def OnInit(self):
        'Create the main window and insert the custom frame'
        if hasattr(self.dataPlotManager, 'xrc_file') and \
           self.dataPlotManager.xrc_file != None:
            respath = self.dataPlotManager.xrc_file
        else:
            respath = os.path.join(os.path.dirname(__file__),
                                   'reflex_interactive_gui.xrc')
        self.res = xrc.XmlResource(respath)

        self.frame = self.res.LoadFrame(None, 'ReflexInteractiveWxApp')
        self.setXrcObjects()
        self.bindXrcObjects()
        self.setFitsFiles()
        self.setWindowTitle()
        self.setDatasetInfoText()
        self.setupParameters()
        self.createPlotsArea()
        self.connectPlottingWidgets()
        self.frame.Show(True)
        return True

    def setXrcObjects(self):
        self.plotPanel = xrc.XRCCTRL(self.frame, 'plotPanel')
        self.statusBar = xrc.XRCCTRL(self.frame, 'statusBar')
        self.parameterNotebook = xrc.XRCCTRL(self.frame, 'parameterNotebook')
        self.datasetInfoText = xrc.XRCCTRL(self.frame, 'datasetInfoText')
        self.setDisableCheck = xrc.XRCCTRL(self.frame, 'setDisableCheck')
        self.setInitSopCheck = xrc.XRCCTRL(self.frame, 'setInitSopCheck')
        if(not self.inter_app.is_init_sop_enable()):
            self.setInitSopCheck.Hide()

    def bindXrcObjects(self):
        self.Bind(wx.EVT_BUTTON, self.onCont, id=xrc.XRCID('contBtn'))
        self.Bind(wx.EVT_BUTTON, self.onRepeat, id=xrc.XRCID('repeatBtn'))
        self.Bind(wx.EVT_BUTTON, self.onHelp, id=xrc.XRCID('helpBtn'))
        self.Bind(wx.EVT_CHECKBOX, self.onSetDisable, self.setDisableCheck)
        if(self.inter_app.is_init_sop_enable()):
            self.Bind(wx.EVT_CHECKBOX, self.onSetInitSop, self.setInitSopCheck)

    def setWindowTitle(self):
        if not self.frame:
            raise Exception("Frame not found")

        if hasattr(self.dataPlotManager, 'setWindowTitle'):
            self.frame.SetTitle(self.dataPlotManager.setWindowTitle())

    def setupParameters(self):
        # Get the list of recipe parameter groups
        self.requestedParamList = self.dataPlotManager.setInteractiveParameters(
        )
        parameterGroups = list()
        for param in self.requestedParamList:
            if parameterGroups.count(param.group) == 0:
                parameterGroups.append(param.group)

        self.parameterGrid = {}
        self.parameterTabs = {}
        for paramGroup in parameterGroups:
            self.parameterGrid[paramGroup] = wx.FlexGridSizer(cols=2,
                                                              vgap=4, hgap=4)
            self.parameterGrid[paramGroup].AddGrowableCol(1)
            self.parameterTabs[paramGroup] = wx.Panel(self.parameterNotebook)
            self.parameterTabs[paramGroup].SetSizer(
                self.parameterGrid[paramGroup], 1)
            self.parameterNotebook.AddPage(
                self.parameterTabs[paramGroup], paramGroup)

        # The widgets for the parameters
        self.shownParam = list()
        self.shownParamWidgets = list()
        for param in self.requestedParamList:
            for param_in_sop in self.inter_app.inputs.in_sop:
                if param_in_sop.recipe == param.recipe and \
                   param_in_sop.displayName == param.displayName:
                    param.value = param_in_sop.value
                    param.name = param_in_sop.name
                    self.shownParam.append(param)
                    paramWidget = ParamWidget(
                        self.parameterTabs[param.group], param)
                    self.shownParamWidgets.append((param.group, paramWidget))

        # Pack parameter widgets
        for (paramGroup, paramWidget) in self.shownParamWidgets:
            self.parameterGrid[paramGroup].Add(paramWidget.paramLabel,
                                               flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
            self.parameterGrid[paramGroup].Add(paramWidget.paramEditText,
                                               flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT, border=5)
            

    def createPlotsArea(self):
        # Read the pipeline data
        self.dataPlotManager.readFitsData(self.all_fitsFiles)
        # The matplotlib figure
        self.figure = Figure()
        self.figureCanvas = FigureCanvasWxAgg(self.plotPanel, wx.ID_ANY,
                                              self.figure)
#    self.canvas.SetToolTip(wx.ToolTip(tip = ''))
        # Setup toolbar
        self.toolbar = reflex_navigation_toolbar.ReflexNavigationToolbar(
            self.figureCanvas)
        self.frame.SetToolBar(self.toolbar)
        # Bind actions for status bar and tooltips
        self.figureCanvas.mpl_connect('motion_notify_event', self.onMotion)
        self.figureCanvas.mpl_connect('axes_enter_event', self.onEnterAxes)
        self.figureCanvas.mpl_connect('axes_leave_event', self.onLeaveAxes)

        # Bind actions for proper size
        self.plotPanel.Bind(wx.EVT_SIZE, self.onResize)
        self.plotPanel.Bind(wx.EVT_IDLE, self.onIdle)

        self.needs_resize = False
        self.dataPlotManager.addSubplots(self.figure)
        self.dataPlotManager.plotProductsGraphics()
        self.figure.subplots_adjust(wspace=0.40, hspace=0.40,
                                    top=0.93, bottom=0.07,
                                    left=0.1, right=0.95)

    def setFitsFiles(self):
        try:
            self.in_sof_fitsFiles = self.inter_app.inputs.in_sof.files
            self.dataset = self.inter_app.inputs.in_sof.datasetName
            self.in_sof_rec_orig_fitsFiles = self.inter_app.inputs.in_sof_rec_orig.files
            self.all_fitsFiles = self.in_sof_fitsFiles + \
                self.in_sof_rec_orig_fitsFiles
            if len(self.in_sof_rec_orig_fitsFiles) == 0:
                self.purposes = 'INVALID'
            else:
                self.purposes = self.in_sof_rec_orig_fitsFiles[0].purposes
        except ValueError:
            print "Error parsing input sof."
            print "Syntax should be LOSO_NAME|file1;CATEGORY;PURPOSE,file2;..."
            sys.exit()

    def setDatasetInfoText(self):
        # The general info status bar
        datasetInfoAreaText = ''' This data belongs to dataset:
    '''+self.dataset
        self.datasetInfoText.SetLabel(datasetInfoAreaText)

    def connectPlottingWidgets(self) :
        if hasattr(self.dataPlotManager, 'plotWidgets') :
            self.widgets = self.dataPlotManager.plotWidgets()
            for widget in self.widgets :
                widget.setPostCallback(self.onPlotWidgetEvent) 

    def onPlotWidgetEvent(self, new_params = None):
        self.figureCanvas.draw()
        if new_params is not None :
            for new_param in new_params :
                for widget in self.shownParamWidgets :
                    if new_param.displayName == widget[1].parameter.displayName :
                        widget[1].paramEditText.SetValue(new_param.value)
            

    def onCont(self, event):
        self.inter_app.set_continue_mode()
        self.frame.Close(True)

    def onRepeat(self, event):
        # This will update the output parameters based on the entry boxes.
        # It also contains all the parameters that are not shown in the window
        user_edited_param = list()
        for param_in_sop in self.inter_app.inputs.in_sop:
            newParam = param_in_sop
            for (paramGroup, paramWidget) in self.shownParamWidgets:
                if param_in_sop.displayName == paramWidget.parameter.displayName and \
                        param_in_sop.recipe == paramWidget.parameter.recipe:
                    paramWidget.setValue(event=None)
                    newParam = paramWidget.parameter
            user_edited_param.append(newParam)

        self.inter_app.set_repeat_mode(user_edited_param)
        self.frame.Close(True)

    def onHelp(self, event):
        window_help_msg = self.dataPlotManager.setWindowHelp()
        general_help_msg = """

The window has several parts:\n
   1. Plot area. This area shows how good the reduction was performed
   2. Parameter area. This area shows the parameters used for the execution of the recipe. The parameters can be changed if the recipe has to be re-run with new parameters
   3. Button area. These buttons control the interactivity of the window\n
        a) Continue wkf. This button sends the current results to the next recipe in the workflow.\n
        b) Re-run recipe. This button will execute the predict recipe again with the new parameters\n
        d) Help. This button shows this help
   4. Top toolbar area. These buttons allow certain interactivity with the plots (zoom, shift, layout) as well as exporting to png
        """
        dlg = wx.MessageDialog(self.frame, window_help_msg + general_help_msg,
                               self.dataPlotManager.setWindowTitle()+" Help",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onSetDisable(self, event):
        if self.setDisableCheck.GetValue():
            self.inter_app.set_disable_next_iteration()

    def onSetInitSop(self, event):
        if self.setInitSopCheck.GetValue():
            self.inter_app.set_next_init_sop()

    def onMotion(self, event):
        if event.inaxes:
            self.statusBar.SetStatusText(event.inaxes.format_coord(event.xdata,
                                                                   event.ydata))
        else:
            self.statusBar.SetStatusText((''), 0)

    def onEnterAxes(self, event):
        if hasattr(event.inaxes, 'tooltip'):
            tip = self.figureCanvas.GetToolTip()
            if not tip:
                tip = wx.ToolTip(tip=event.inaxes.tooltip)
                self.figureCanvas.SetToolTip(tip)
            else:
                tip.SetTip(event.inaxes.tooltip)
            tip.Enable(True)

    def onLeaveAxes(self, event):
        try:
            self.figureCanvas.GetToolTip().Enable(False)
        except:
            pass

    def onResize(self, event):
        self.needs_resize = True

    def onIdle(self, event):
        if self.needs_resize:
            self.figureCanvas.SetSize(self.plotPanel.GetSize())
            self.needs_resize = False
        wx.WakeUpIdle()

# This class is used to display the label and edit box of a parameter


class ParamWidget:

    def __init__(self, parent, param):
        self.parameter = param
        self.paramLabel = wx.StaticText(parent, label=param.displayName)
        self.paramLabel.SetToolTipString(param.displayName)
        self.paramEditText = wx.TextCtrl(parent, -1,
                                         style=wx.TE_PROCESS_ENTER | wx.TE_RIGHT)
        self.paramEditText.SetValue(param.value)
        self.paramEditText.SetToolTipString(param.description)

        # This binding is unnecessary, since the OnRepeat directly access the
        # GetValue() of paramEditText. I keep it here in case that
        # the desired behaviour is that you have to press Enter to actually edit the
        # value
        self.paramEditText.Bind(wx.EVT_TEXT_ENTER, self.setValue)

    def setValue(self, event):
        self.parameter.value = self.paramEditText.GetValue()
