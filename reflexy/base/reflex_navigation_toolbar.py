import math
import matplotlib
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg
import wx
matplotlib.interactive(False)


class ReflexNavigationToolbar(NavigationToolbar2WxAgg):

    """
    Extend the default wx toolbar to include a button to change the
    Z scale for images
    """
    ON_ZSCALE = wx.NewId()

    def __init__(self, canvas):
        NavigationToolbar2WxAgg.__init__(self, canvas)
        self.AddSeparator()
        self.AddCheckTool(
            self.ON_ZSCALE, wx.ArtProvider.GetBitmap(wx.ART_HELP_SIDE_PANEL),
            shortHelp='Change Z scale in images',
            longHelp='Change Z scale in images')
        wx.EVT_TOOL(self, self.ON_ZSCALE, self.on_zscale)

#This allows to have only one of the Pan, Zoom, Zscale buttons clicked at a time.
#However, it uses some NavigationToolbar2WxAgg internals, and therefore is not 
#portable across matplolib versions.
#    def zoom(self, *args):
#        self.ToggleTool(self.wx_ids['Pan'], False)
#        self.ToggleTool(self.ON_ZSCALE, False)
#        NavigationToolbar2WxAgg.zoom(self, *args)

#    def pan(self, *args):
#        self.ToggleTool(self.wx_ids['Zoom'], False)
#        self.ToggleTool(self.ON_ZSCALE, False)
#        NavigationToolbar2WxAgg.pan(self, *args)

    def on_zscale(self, evt):
#        self.ToggleTool(self.wx_ids['Pan'], False)
#        self.ToggleTool(self.wx_ids['Zoom'], False)
#        self._lastCursor =  self.canvas.GetCursor()
#        self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        if self._active == 'ZSCALE':
            self._active = None
        else:
            self._active = 'ZSCALE'
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.press_zscale)
            self.mode = 'zscale'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

    def press_zscale(self, event):
        if event.inaxes is None:
            return
        x_disp, y_disp = event.x, event.y
        for axes in self.canvas.figure.get_axes():
            if (x_disp is not None and y_disp is not None and axes.in_axes(event)):
                images = axes.get_images()
                if len(images) != 0:
                    image = images[0]
                    xlim = axes.get_xlim()
                    ylim = axes.get_ylim()
                    xlim_disp_min, ylim_disp_min = \
                        axes.transData.transform_point((xlim[0], ylim[0]))
                    xlim_disp_max, ylim_disp_max = \
                        axes.transData.transform_point((xlim[1], ylim[1]))

                    zlim_center =  axes.img_avg - 2 * axes.img_dev + \
                        4*axes.img_dev*(x_disp - xlim_disp_min) / (
                            xlim_disp_max - xlim_disp_min)
                    zlim_range  =  axes.img_dev * 2 * \
                        math.exp(- 3 + 6*(y_disp - ylim_disp_min) / (
                            ylim_disp_max - ylim_disp_min))
                    zmin = zlim_center - zlim_range / 2
                    zmax = zlim_center + zlim_range / 2
                    image.set_clim(zmin, zmax)
                    self.release(event)
                    axes.figure.canvas.draw_idle()
