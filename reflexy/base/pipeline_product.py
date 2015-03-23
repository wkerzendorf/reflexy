try:
    import numpy
    import pyfits
except ImportError:
    pass


class PipelineProduct:

    def __init__(self, fits_file):
        self.fits_file = fits_file
        self.all_hdu = self.hdulist()

    def hdulist(self):
        return pyfits.open(self.fits_file.name)

    def readImage(self, fits_extension=0):
        self.image = self.all_hdu[fits_extension].data

    def readLinearWCS(self, fits_extension=0):
        try:
            self.crval1 = self.all_hdu[fits_extension].header['CRVAL1']
            self.crpix1 = self.all_hdu[fits_extension].header['CRPIX1']
            if 'CD1_1' in self.all_hdu[fits_extension].header :
                self.cdelt1 = self.all_hdu[fits_extension].header['CD1_1']
            else :
                self.cdelt1 = self.all_hdu[fits_extension].header['CDELT1']
            self.type1 = self.all_hdu[fits_extension].header['CTYPE1']
        except KeyError:
            self.crval1 = None
            self.crpix1 = None
            self.cdelt1 = None
            self.type1 = None

    def read2DLinearWCS(self, fits_extension=0):
        try:
            self.crval1 = self.all_hdu[fits_extension].header['CRVAL1']
            self.crpix1 = self.all_hdu[fits_extension].header['CRPIX1']
            if 'CD1_1' in self.all_hdu[fits_extension].header :
                self.cdelt1 = self.all_hdu[fits_extension].header['CD1_1']
            else :
                self.cdelt1 = self.all_hdu[fits_extension].header['CDELT1']
            self.type1 = self.all_hdu[fits_extension].header['CTYPE1']
            self.crval2 = self.all_hdu[fits_extension].header['CRVAL2']
            self.crpix2 = self.all_hdu[fits_extension].header['CRPIX2']
            if 'CD1_1' in self.all_hdu[fits_extension].header :
                self.cdelt2 = self.all_hdu[fits_extension].header['CD2_2']
            else :
                self.cdelt2 = self.all_hdu[fits_extension].header['CDELT2']
            self.type2 = self.all_hdu[fits_extension].header['CTYPE2']
        except KeyError:
            self.crval1 = None
            self.crpix1 = None
            self.cdelt1 = None
            self.type1 = None
            self.crval2 = None
            self.crpix2 = None
            self.cdelt2 = None
            self.type2 = None

    def readTableXYColumns(self, fits_extension, xcolname, ycolname):
        self.x_column = self.all_hdu[fits_extension].data.field(xcolname)
        self.y_column = self.all_hdu[fits_extension].data.field(ycolname)

    def readTableColumn(self, fits_extension, colname):
        self.column = self.all_hdu[fits_extension].data.field(colname)
        return self.column

    def getTableNcols(self, fits_extension):
        return len(self.all_hdu[fits_extension].columns)

    def getTableNrows(self, fits_extension):
        return self.all_hdu[fits_extension].data.shape[0]

    def readSpectrum(self, fits_extension=0):
        self.flux = self.all_hdu[fits_extension].data
        self.crval1 = self.all_hdu[fits_extension].header['CRVAL1']
        self.crpix1 = self.all_hdu[fits_extension].header['CRPIX1']
        self.cdelt1 = self.all_hdu[fits_extension].header['CDELT1']
        self.type1 = self.all_hdu[fits_extension].header['CTYPE1']
        self.bunit = self.all_hdu[fits_extension].header['BUNIT']
        self.nwave = len(self.flux)
        self.start_wave = self.crval1 + (+1-self.crpix1) * self.cdelt1
        self.end_wave = self.crval1 + (
            self.nwave-self.crpix1) * self.cdelt1
        self.wave = numpy.arange(1, self.nwave+1, 1)
        self.wave = (
            self.wave - self.crpix1) * self.cdelt1 + self.crval1

    def readKeyword(self, keyName, fits_extension=0):
        return self.all_hdu[fits_extension].header[keyName]
