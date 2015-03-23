try:
    import matplotlib
    matplotlib.use('WXAgg')
    import numpy
    from matplotlib.pyplot import cm
    import types
    numpy.seterr(invalid='ignore')
except ImportError:
    pass

"""@package pipeline_display
This package allows easy plotting of pipeline data (images, spectra, tables)
with a few class method calls.
It is assumed that the plotting is done in a subplot of a Figure matplotlib
object
(http://matplotlib.sourceforge.net/api/axes_api.html#matplotlib.axes.Axes)
"""


class Plot:

    """This class contains basic functionality that is used by other plotting
    classes to perform some common tasks. It shouldn't be used directly"""

    def finalSetup(self, subplot, title, tooltip):
        """Perform some final tasks, like plotting the graph title and
        setting the tooltip"""

        subplot.grid(True)
        subplot.set_title(title, fontsize=12, fontweight='semibold')
        subplot.tooltip = tooltip


class ScatterPlottingDataset:

    """This class contains the data and configuration to plot a scatter dataset"""

    def __init__(self, x, y, marker='o', pointSize=1.4, color='blue'):
        self.x = x
        self.y = y
        self.marker = marker
        self.pointSize = pointSize
        self.color = color


class ScatterDisplay(Plot):

    """This class allows to plot a scatter graph, X vs Y.
    The basic usage is as follows:
    scadsp = ScatterDisplay()
    scadsp.display(subplot, title, tooltip, x, y)
    where x and y have the same lenght.
    Do not reuse an object of this class for different plots."""

    def __init__(self):
        self.pointSize = 1.4
        self.xLabel = None
        self.xLim = None
        self.color = 'blue'

    def display(self, subplot, title, tooltip, x, y, yerr = None):
        """This method is the main one, as it actually specifies what to plot.
        The subplot argument contains a subplot created with
        matplotlib.figure.add_subplot() method
        The tooltip will appear when hovering the mouse over the plot.
        The x, y inputs are actually the array of points to plot. They must have
        the same lenght.
        """
        if yerr is not None:
            subplot.errorbar(x, y, yerr=yerr, fmt='o')
        subplot.scatter(x, y, self.pointSize, color=self.color)
        if self.xLim is None:
            subplot.set_autoscale_on(True)
            subplot.autoscale_view(tight=None, scalex=True, scaley=True)
        else:
            subplot.set_xlim(self.xLim)
            subplot.set_ylim(self.yLim)
        if self.xLabel is not None:
            subplot.set_xlabel(self.xLabel, style='italic')
            subplot.set_ylabel(self.yLabel, style='italic')
        self.finalSetup(subplot, title, tooltip)

    def setPointSize(self, size):
        """Method to change the point size. It should be called before the
         display() method"""
        self.pointSize = size


    def setLabels(self, xLabel, yLabel):
        """This method sets the labels to use for the X and Y axes. It should be
         called before the display method()"""
        self.xLabel = xLabel
        self.yLabel = yLabel

    def setLimits(self, xMin, xMax, yMin, yMax):
        """This method specifies the limits of the axes in the plot. If the method
        is not called, then an autoscaling algorithm is applied. It should be
         called before the display method()"""
        self.xLim = xMin, xMax
        self.yLim = yMin, yMax

    def setColor(self, color):
        """Method to change the color. It should be called before the
         display() method"""
        self.color = color


class SpectrumDisplay(Plot):

    """This class allows to plot a spectrum.
    The basic usage is as follows:
    specdsp = SpectrumDisplay()
    specdsp.display(subplot, title, tooltip, wave, flux)
    where wave is the array with the wavelengths and flux contains the fluxes.
    Do not reuse an object of this class for different plots."""

    def __init__(self):
        self.x_label = None
        self.wave_lim = None
        self.flux_lim = None

    def setLabels(self, x_label, y_label):
        """This method sets the labels to use for the X and Y axes. It should be
         called before the display method()"""
        self.x_label = x_label
        self.y_label = y_label

    def display(self, subplot, title, tooltip, wave,
                flux, errorflux=None, autolimits=False):
        """This method is the main one, as it actually specifies what to plot.
        The subplot argument contains a subplot created with
        matplotlib.figure.add_subplot() method
        The tooltip will appear when hovering the mouse over the plot.
        wave is the array with the wavelengths and flux contains the fluxes. They
        must have the same length. If errorflux is provided, then the error bars
        will be plotted accordingly.
        If autolimits is set to True, then an algorithm that can choose the best
        axes limits is applied. Otherwise, the axes will span to cover the minimum
        and maximum of the wave and fluxes array values or the last applied
        limits, if any.
        """
        flux_1sigma_below = None
        flux_1sigma_above = None
        if self.x_label is not None:
            subplot.set_xlabel(self.x_label, style='italic')
            subplot.set_ylabel(self.y_label, style='italic')
        if errorflux is not None:
            flux_1sigma_below = flux - errorflux
            flux_1sigma_above = flux + errorflux
            subplot.fill_between(wave, flux_1sigma_below, flux_1sigma_above,
                                 facecolor='b', alpha=0.30)
        if self.flux_lim is None or autolimits == True:
            self.__setFluxAutoLimits(
                wave, flux, flux_1sigma_below, flux_1sigma_above)

        subplot.plot(wave, flux, color='blue')
        if self.wave_lim is None:
            self.__setWaveAutoLimits(wave)
        subplot.set_xlim(self.wave_lim)
        subplot.set_ylim(self.flux_lim)
        self.finalSetup(subplot, title, tooltip)

    def overplot(self, subplot, wave, flux, color='green'):
        """This method allows to over plot a second spectrum, but with
        all the subplot setup already created by a previous display call.
        The subplot argument contains a subplot created with
        matplotlib.figure.add_subplot() method
        """
        subplot.plot(wave, flux, color=color)

    def setWaveLimits(self, wave_limits):
        """This method sets the limits in X axes
        """
        self.wave_lim = wave_limits

    def __setWaveAutoLimits(self, wave):
        """This method will set automatically the limits for X axis
        """
        self.wave_lim = wave[0], wave[len(wave)-1]

    def __setFluxAutoLimits(self, wave, flux,
                            flux_1sigma_below=None, flux_1sigma_above=None):
        """This method performs an optimal scaling of the axes. It is only used
        internally"""
        nwave = len(flux)
        minlimwave = int(nwave*0.25)
        maxlimwave = int(nwave*0.75)
        flux_plotmin = 0
        if flux_1sigma_above is None:
            flux_plotmax = 1.2 * numpy.nanmax(
                flux[minlimwave:maxlimwave])
        else:
            flux_plotmax = 1.2 * numpy.nanmax(
                flux_1sigma_above[minlimwave:maxlimwave])
        self.flux_lim = flux_plotmin, flux_plotmax


class ImageDisplay(Plot):

    """This class allows to a 2D image.
    The basic usage is as follows:
    imadsp = ImageDisplay()
    imadsp.display(subplot, title, tooltip, image)
    where image is the 2D image to plot.
    Do not reuse an object of this class for different plots."""

    def __init__(self):
        self.x_label = None
        self.x_lim = None
        self.z_lim = None
        self.x_linwcs = None
        self.y_linwcs = None
        self.overplotScatterDataSet = None
        self.aspect = 'auto'

    def __formatCoordValue(self, data, x, y):
        (image, subplot) = data
        x_im = (int)(x-0.5)
        y_im = (int)(y-0.5)
        if self.x_linwcs is not None:
            (crval1, cdelt1, crpix1) = self.x_linwcs
            x_im = (int)((x - crval1) / cdelt1 + crpix1-0.5)
        if self.y_linwcs is not None:
            (crval2, cdelt2, crpix2) = self.y_linwcs
            y_im = (int)((y - crval2) / cdelt2 + crpix2-0.5)
        return "x=%s y=%s value=%s" % (subplot.format_xdata(x),
                                       subplot.format_ydata(y),
                                       subplot.format_xdata(image[y_im, x_im]))

    def display(self, subplot, title, tooltip, image, bpmimage=None):
        """This method is the main one, as it actually specifies what to plot.
        The subplot argument contains a subplot created with
        matplotlib.figure.add_subplot() method
        The tooltip will appear when hovering the mouse over the plot.
        The input image contains the 2D image to be plotted.
        If bpmimage is also input, then it is asumed to be a bad pixel mask and
        those values with bpmimage > 1 will be flagged in red.
        """
        # Labels
        if self.x_label is not None:
            subplot.set_xlabel(self.x_label, style='italic')
            subplot.set_ylabel(self.y_label, style='italic')

        # Limits
        if self.x_lim is not None:
            subplot.set_xlim(self.x_lim)
            subplot.set_ylim(self.y_lim)

        # Z limits
        if self.z_lim is None:
            self.setZAutoLimits(image, bpmimage)
        else:
            self.dev = (self.z_lim[1] - self.z_lim[0])
            self.avg = (self.z_lim[1] - self.z_lim[0]) / 2.

        # Store the statistics in the subplot, so that it can be accessed later
        # by the toolbar to do the scaling
        subplot.img_dev = self.dev
        subplot.img_avg = self.avg

        normalization = matplotlib.colors.Normalize(vmin=self.z_lim[0],
                                                    vmax=self.z_lim[1])

        # Overplotting of scatter
        if self.overplotScatterDataSet is not None:
            for dataset in self.overplotScatterDataSet:
                subplot.scatter(dataset.x, dataset.y, dataset.pointSize,
                                color=dataset.color, marker=dataset.marker)

        # WCS and coordinates
        if self.x_linwcs is not None:
            (crval1, cdelt1, crpix1) = self.x_linwcs
            extent_x1 = (0.5 - crpix1) * cdelt1 + crval1
            extent_x2 = (0.5 + image.shape[1] - crpix1) * cdelt1 + crval1
        else:
            extent_x1 = 0.5
            extent_x2 = 0.5 + image.shape[1]
        if self.y_linwcs is not None:
            (crval2, cdelt2, crpix2) = self.y_linwcs
            extent_y1 = (0.5 - crpix2) * cdelt2 + crval2
            extent_y2 = (0.5 + image.shape[0] - crpix2) * cdelt2 + crval2
        else:
            extent_y1 = 0.5
            extent_y2 = 0.5 + image.shape[0]

        # Displaying the image
        subplot.imshow(image, interpolation="nearest",
                       origin="lower", aspect=self.aspect,
                       cmap=matplotlib.pyplot.cm.gray,
                       norm=normalization,
                       extent=(extent_x1, extent_x2, extent_y1, extent_y2))
        # Displaying the bad pixel mask
        if bpmimage is not None:
            bpmimage_unity = bpmimage
            bpmimage_unity[bpmimage > 1] = 1
            masked_bmp = numpy.ma.masked_array(bpmimage, mask=(bpmimage == 0))
            subplot.imshow(masked_bmp, interpolation="nearest", alpha=0.8,
                           origin="lower", aspect=self.aspect,
                           extent=(extent_x1, extent_x2, extent_y1, extent_y2),
                           cmap = matplotlib.pyplot.cm.autumn)

        self.finalSetup(subplot, title, tooltip)
        subplot.format_coord = types.MethodType(self.__formatCoordValue,
                                                (image, subplot))

    def setAspect(self, aspect) :
        self.aspect = aspect

    def setLabels(self, x_label, y_label):
        """This method sets the labels to use for the X and Y axes. It should be
         called before the display method()"""
        self.x_label = x_label
        self.y_label = y_label

    def setLimits(self, x_lim, y_lim):
        """This method specifies the limits of the axes in the plot. If the method
        is not called, the whole image will be displayed. It should be
         called before the display method()"""
        self.x_lim = x_lim
        self.y_lim = y_lim

    def setZLimits(self, z_lim) :
        self.z_lim = z_lim

    def setZAutoLimits(self, image, bpmimage):
        """This method specifies computes optimal values for limits of the image
        values (z variable). It uses a sigma clipping, with a clipping of
        2 sigma, to get a better estimate of the deviation. It should be
        called before the display method()"""
        if bpmimage is not None:
            image_bpm = image[bpmimage == 0]
            self.avg = numpy.median(image_bpm[numpy.isfinite(image_bpm)])
            self.dev = 2*image_bpm[numpy.abs(
                image_bpm-self.avg) < 2*image_bpm[numpy.isfinite(image_bpm)].std()].std()
        else:
            self.avg = numpy.median(image[numpy.isfinite(image)])
            self.dev = 2*image[numpy.abs(image-self.avg) < 2*image[numpy.isfinite(image)].std()].std()

        self.z_lim = self.avg-self.dev, self.avg+self.dev

    def setXLinearWCSAxis(self, crval1, cdelt1, crpix1):
        """This method specifies a different X axis transformation than just pixels.
        It follows WCS convention for linear transformation, specifying crval1,
        cdelt1 and crpix1. The WCS value will be:
        wcs_value = (pix_position - crpix1) * cdelt1 + crval1.
        It should be called before the display method()"""
        self.x_linwcs = (crval1, cdelt1, crpix1)

    def setYLinearWCSAxis(self, crval2, cdelt2, crpix2):
        """This method specifies a different Y axis transformation than just pixels.
        It follows WCS convention for linear transformation, specifying crval2,
        cdelt2 and crpix2. The WCS value will be:
        wcs_value = (pix_position - crpix2) * cdelt2 + crval2.
        It should be called before the display method()"""
        self.y_linwcs = (crval2, cdelt2, crpix2)

    def overplotScatter(self, x, y, marker='+', size=1.4, color='blue'):
        scatterDataset = ScatterPlottingDataset(x, y, marker, size, color)
        if self.overplotScatterDataSet is None:
            self.overplotScatterDataSet = []
        self.overplotScatterDataSet.append(scatterDataset)
