# import the needed modules
try:
    import reflex
    import pipeline_product
    import pipeline_display
    import_sucess = True

# NOTE for developers:
# -If you want to modify the current script to cope
#  with different parameters, this is the function to modify:
#  setInteractiveParameters()
# -If you want to modify the current script to read different data from
#  the input FITS, this is the function to modify:
#  readFitsData()                  (from class DataPlotterManager)
# -If you want to modify the current script to modify the plots (using the same
#  data),  this is the function to modify:
#  plotProductsGraphics()          (from class DataPlotterManager)
# -If you want to modify the text that appears in the "Help" button,
#  this is the function to modify:
#  setWindowHelp()
# -If you want to modify the tittle of the window, modify this function:
#  setWindowTitle()
# -Do not modify anything else apart from these methods.

# FIXME:
# Redesign the thing:
# A function init() that will be called with fitsFiles and sof (the information to be conveyed to the dataplotmanager
# and then the functions setInteractiveParameters readFitsData plotProductsGraphics setWindowHelp and setWindowHelp
# Maybe figure can also be passed to the init

    # This class deals with the specific details of data reading and final
    # plotting.
    class DataPlotterManager:
        # This function will read all the columns, images and whatever is needed
        # from the products. The variables , self.plot_x, self.plot_y, etc...
        # are used later in function plotProductsGraphics().
        # Add/delete these variables as you need (only that plotProductsGraphics()
        # has to use the same names).
        # You can also create some additional variables (like statistics) after
        # reading the files.
        # If you use a control variable (self.xxx_found), you can modify
        # later on the layout of the plotting window based on the presence of
        # given input files.
        # sof contains all the set of frames
        # TODO: Add in_sop here, because it is needed to plot some of the
        # parameters

        def readFitsData(self, fitsFiles):
            # Control variable to check if the interesting files where at the
            # input
            self.science_found = False
            self.merge_found = False
            self.lineguess_found = False
            self.flat_found = False
            self.bpm_found = False
            # Read all the products
            frames = dict()
            for frame in fitsFiles:
                if frame == '':
                    continue
                category = frame.category
                frames[category] = frame

            if 'RED_SCI_POINT_BLUE' in frames:
                self.science_found = True
                self.science = pipeline_product.PipelineProduct(
                    frames["RED_SCI_POINT_BLUE"])

            if 'SCI_SLIT_MERGE1D_NIR' in frames:
                self.merge_found = True
                self.merge = pipeline_product.PipelineProduct(
                    frames["SCI_SLIT_MERGE1D_NIR"])

            if 'LINE_GUESS_TAB_BLUE' in frames:
                self.lineguess_found = True
                self.lineguess = pipeline_product.PipelineProduct(
                    frames["LINE_GUESS_TAB_BLUE"])

            if 'FLAT_IM' in frames:
                self.flat_found = True
                self.flat = pipeline_product.PipelineProduct(frames["FLAT_IM"])

            if 'BPM' in frames:
                self.bpm_found = True
                self.bpm = pipeline_product.PipelineProduct(frames["BPM"])

            if 'SCI_SLIT_MERGE2D_VIS' in frames:
                self.specimage = pipeline_product.PipelineProduct(
                    frames["SCI_SLIT_MERGE2D_VIS"])

            if 'RED_SCI_POINT_BLUE_BIS' in frames:
                self.scipoint = pipeline_product.PipelineProduct(
                    frames["RED_SCI_POINT_BLUE_BIS"])

            if 'ERROR_RED_SCI_POINT_BLUE_BIS' in frames:
                self.scipointerr = pipeline_product.PipelineProduct(
                    frames["ERROR_RED_SCI_POINT_BLUE_BIS"])

        # This function creates all the subplots. It is responsible for the plotting
        # layouts.
        # There can different layouts, depending on the availability of data
        # Note that subplot(I,J,K) means the Kth plot in a IxJ grid
        # Note also that the last one is actually a box with text, no graphs.
        def addSubplots(self, figure):
            if self.science_found == True and self.lineguess_found == True and self.flat_found == True and self.merge_found == True:
                self.subplot_spectrum = figure.add_subplot(3, 2, 1)
                self.subplot_scatter = figure.add_subplot(3, 2, 2)
                self.subplot_image = figure.add_subplot(3, 2, 3)
                self.subplot_specimage = figure.add_subplot(3, 2, 4)
                self.subplot_two_spec = figure.add_subplot(3, 2, 5)
                self.subplot_spec_err = figure.add_subplot(3, 2, 6)
            else:
                self.subtext_nodata = figure.add_subplot(1, 1, 1)

        # This is the function that makes the plots.
        # Add new plots or delete them using the given scheme.
        # The data has been already stored in self.plot_x, self.plot_xdif, etc ...
        # It is mandatory to add a tooltip variable to each subplot.
        # One might be tempted to merge addSubplots() and plotProductsGraphics().
        # There is a reason not to do it: addSubplots() is called only once at
        # startup, while plotProductsGraphics() is called always there is a
        # resize.
        def plotProductsGraphics(self):
            if self.science_found == True and self.lineguess_found == True and self.flat_found == True and self.merge_found == True:

                # Spectrum plot
                title_spectrum = 'Spectrum plot'
                tooltip_spectrum = """Typical spectrum Plot.  """
                self.science.readSpectrum()
                specdisp = pipeline_display.SpectrumDisplay()
                specdisp.setLabels('Lambda', 'Flux ('+self.science.bunit+')')
                specdisp.display(self.subplot_spectrum,
                                 title_spectrum, tooltip_spectrum,
                                 self.science.wave, self.science.flux)

                # Scatter plot
                title_scatter = 'X Y scatter plot'
                tooltip_scatter = """Typical X Y scatter Plot.  """
                self.lineguess.readTableXYColumns(fits_extension=1,
                                                  xcolname='X', ycolname='Y')
                scatterdisp = pipeline_display.ScatterDisplay()
                scatterdisp.setLabels('X', 'Y')
                scatterdisp.display(self.subplot_scatter, title_scatter,
                    tooltip_scatter, self.lineguess.x_column,
                    self.lineguess.y_column, self.lineguess.y_column)

                # Image
                title_image = 'Image'
                tooltip_image = """This is an image."""
                self.flat.readImage(fits_extension=1)
                self.bpm.readImage(fits_extension=1)
                imgdisp = pipeline_display.ImageDisplay()
                imgdisp.setLabels('X', 'Y')
                imgdisp.setLimits((200, 1800), (50, 300))
                imgdisp.overplotScatter(self.lineguess.x_column,
                                        self.lineguess.y_column,
                                        marker='o', size=4)
                imgdisp.overplotScatter(
                    self.lineguess.x_column[self.lineguess.x_column > 1400],
                    self.lineguess.y_column[self.lineguess.x_column > 1400],
                    marker='+', size=10, color='red')
                imgdisp.display(self.subplot_image, title_image, tooltip_image,
                                self.flat.image, self.bpm.image)

                # Image
                title_image = 'Spectral Image'
                tooltip_image = """This is an spectral image.
"""
                self.specimage.readImage(fits_extension=0)
                self.specimage.read2DLinearWCS(fits_extension=0)
                imgdisp = pipeline_display.ImageDisplay()
                imgdisp.setLabels('Wavelength', 'Y')
                imgdisp.setXLinearWCSAxis(self.specimage.crval1,
                                          self.specimage.cdelt1, self.specimage.crpix1)
                imgdisp.setYLinearWCSAxis(self.specimage.crval2,
                                          self.specimage.cdelt2, self.specimage.crpix2)
                imgdisp.display(
                    self.subplot_specimage, title_image, tooltip_image,
                    self.specimage.image)

                # Two spectrum plot
                title_two_spectrum = 'Two Spectrum plot'
                tooltip_two_spectrum = """Typical spectrum Plot.  """
                self.merge.readSpectrum()
                twospecdisp = pipeline_display.SpectrumDisplay()
                twospecdisp.setLabels('Lambda',
                                      'Flux (%s)' % self.science.bunit)
                twospecdisp.display(self.subplot_two_spec,
                                    title_two_spectrum, tooltip_two_spectrum,
                                    self.merge.wave, self.merge.flux)
                twospecdisp.overplot(self.subplot_two_spec,
                                     self.merge.wave, self.merge.flux/3.)

                # Spectrum plot with error bars
                title_spectrum_err = 'Spectrum plot with errors'
                tooltip_spectrum_err = """Typical spectrum Plot with errors. """
                self.scipoint.readSpectrum()
                self.scipointerr.readSpectrum()
                specerrdisp = pipeline_display.SpectrumDisplay()
                specerrdisp.setLabels('Lambda',
                                      'Flux (%s)' % self.science.bunit)
                specerrdisp.display(self.subplot_spec_err,
                                    title_spectrum_err, tooltip_spectrum_err,
                                    self.scipoint.wave, self.scipoint.flux, self.scipointerr.flux)

            else:
                # Data not found info
                self.subtext_nodata.set_axis_off()
                self.text_nodata = """Data not found. Input files should contain these types:
RED_SCI_POINT_BLUE
LINE_GUESS_TAB_BLUE
FLAT_IM
"""
                self.subtext_nodata.text(
                    0.1, 0.6, self.text_nodata, color='#11557c',
                    fontsize=18, ha='left', va='center', alpha=1.0)
                self.subtext_nodata.tooltip = 'Line prediction not found in the products'

        # This function specifies which are the parameters that should be presented
        # in the window to be edited.
        # Note that the parameter has to be also in the in_sop port (otherwise it
        # won't appear in the window)
        # The descriptions are used to show a tooltip. They should match one to one
        # with the parameter list
        # Note also that parameters have to be prefixed by the 'recipe name:'
        def setInteractiveParameters(self):
            paramList = list()
            paramList.append(reflex.RecipeParameter(
                "recipe_name", "param1", group="group2", description="Desc1"))
            paramList.append(reflex.RecipeParameter(
                "recipe_name", "param2", group="group1", description="Desc2"))
            paramList.append(reflex.RecipeParameter(
                "recipe_name", "param3", group="group3", description="Desc3"))
            paramList.append(reflex.RecipeParameter(
                "recipe_name", "param4", group="group2", description="Desc4"))
            paramList.append(reflex.RecipeParameter(
                "recipe_name", "param9", group="group2", description="Desc4"))
            return paramList

        def setWindowHelp(self):
            help_text = """
This is an interactive window which help asses the quality of the execution of a recipe.
"""
            return help_text

        def setWindowTitle(self):
            title = 'Pipeline Interactive Window'
            return title

except ImportError:
    import_sucess = False
    print "Error importing modules pyfits, wx, matplotlib, numpy"

# This is the 'main' function
if __name__ == '__main__':

    # import reflex modules
    import reflex_interactive_app
    import sys

    # Create interactive application
    interactive_app = reflex_interactive_app.PipelineInteractiveApp()

    # Check if import failed or not
    #  if import_sucess == False :
    #    interactive_app.setEnable('false')

    # Open the interactive window if enabled
    if interactive_app.isGUIEnabled():
        # Get the specific functions for this window
        dataPlotManager = DataPlotterManager()
        interactive_app.setPlotManager(dataPlotManager)
        interactive_app.showGUI()
    else:
        interactive_app.passProductsThrough()

    # Print outputs. This is parsed by the Reflex python actor to get the results
    # Do not remove
    interactive_app.print_outputs()

    sys.exit()
