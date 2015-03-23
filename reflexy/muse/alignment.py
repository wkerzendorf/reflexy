#!/usr/bin/env python
from reflexy.base import reflex
import sys
from optparse import OptionParser
import warnings
import time

try:
    from astropy.io import fits
    import numpy as np
    from photutils import datasets
    from photutils import daofind
    from astropy.stats import median_absolute_deviation as mad
    from astropy.io import fits as pyfits
    from astropy import wcs as pywcs
#import scikit-image
    import astropy
    import scipy
#    import pywcs # WCS conversion routines NOT NEEDED ANYMORE
#    import pyfits # NOT NEEDED ANYMORE
    import copy
    import matplotlib.pyplot as plt
    import_ok = 1
#except ImportError:
except ImportError:
    import_ok = 0

def find_closest(id_,x,y,idlist,xlist,ylist,dist_max):
    distances = ((x-xlist)**2. + (y-ylist)**2.)**0.5
    indici, = np.where(distances == distances.min())
    D = distances.min()
    Dx=x-xlist[indici[0]]  #offset in X (RA) of the matched source
    Dy=y-ylist[indici[0]]  #offset in Y (DEC) of the matched source
    if D <= dist_max:
        id_sel = idlist[indici[0]]+0.
        x_sel = xlist[indici[0]]+0.
        y_sel = ylist[indici[0]]+0.
    else:
        id_sel = []    
        x_sel=[]#0./0.
        y_sel=[]#0./0.
        D=[]#0./0.
        Dx=[]#0./0.
        Dy=[]#0./0.

    return(Dx,Dy,D,x_sel,y_sel,id_sel)


def find_matches(id_,x_,y_,id_ref,x_ref,y_ref,dist_max):

    i=0
    offset_x=[0]
    offset_y=[0]
    n_matches=[0]
    id_match_test=[-1]
    id_match = [-1]
    offset_x_ =[]
    offset_y_ =[]
    while (i < len(id_)):
       search=range(len(id_ref))
       id_match_test=[-1]
       while (id_[i] != id_match_test):
          id_match_test=[-1]  
          Dx,Dy,D,x_sel,y_sel,id_sel = find_closest(id_[i],x_[i],y_[i],id_ref[search],x_ref[search],y_ref[search],dist_max)
          if id_sel == []: 
             break
            # print id_[i], ' has no matches'
             
          ind_match, = np.where(id_sel == id_ref)
          Dx_test,Dy_test,D_test,x_sel_test,y_sel_test,id_match_test = find_closest(id_ref[ind_match],x_ref[ind_match],y_ref[ind_match],id_,x_,y_,dist_max)
          if id_match_test == id_[i]:
             offset_x_.append(Dx)
             offset_y_.append(Dy)
          else:
             if len(search) == 1:
                break
             search.remove(ind_match)
       i = i+1
    
    if (offset_x_ == []):
       offset_x=[0]
       offset_y=[0]
       rms_x=[0]
       rms_y=[0]
       n_matches=0 
    else:
       offset_x = np.median(offset_x_)   # median offsets in X, considering all the matched sources
       offset_y = np.median(offset_y_)   # median offsets in Y, considering all the matched sources
       rms_x=np.std(offset_x_)
       rms_y=np.std(offset_y_)
       n_matches=len(offset_x_)
    return(offset_x,offset_y,n_matches,rms_x,rms_y)


def compute_offsets(id_,x,y,id_ref,x_ref,y_ref):
    nBIAS=31 #51
    step = 1.4#70./(nBIAS-1.) 
    max_dist_arcs = step/2.*1.6   
    max_dist=max_dist_arcs/3600.

    # ...
    ra_bias_offset=  (np.arange(nBIAS)*step -(nBIAS-1)*step/2.)/3600.0
    dec_bias_offset= (np.arange(nBIAS)*step -(nBIAS-1)*step/2.)/3600.0
    
    ncommon_matrix  = np.zeros([nBIAS,nBIAS],float)
    offset_x_matrix = np.zeros([nBIAS,nBIAS],float)
    offset_y_matrix = np.zeros([nBIAS,nBIAS],float)
    rms_ra_matrix   = np.zeros([nBIAS,nBIAS],float)
    rms_dec_matrix  = np.zeros([nBIAS,nBIAS],float)
    offset_x=0.
    offset_y=0.
    n_matches=0.
    rms_ra=-1.
    rms_dec=-1.
    id_common=0
    x_original=x+0
    y_original=y+0

    for I_RA in range(nBIAS):
        for I_DEC in range(nBIAS):

            x_ = x_original+ra_bias_offset[I_RA]
            y_ = y_original+dec_bias_offset[I_DEC]
            small_off_x,small_off_y,n_matches,rms_x,rms_y = find_matches(id_,x_,y_,id_ref,x_ref,y_ref,max_dist)
            ncommon_matrix[I_RA,I_DEC] = n_matches

            offset_x_matrix[I_RA,I_DEC]  = ra_bias_offset[I_RA]-small_off_x
            offset_y_matrix[I_RA,I_DEC]  = dec_bias_offset[I_DEC]-small_off_y
            rms_ra_matrix[I_RA,I_DEC]  = np.array(rms_x)
            rms_dec_matrix[I_RA,I_DEC]  = np.array(rms_y)
                
 
    (indxx,indyy) = np.where(ncommon_matrix == ncommon_matrix.max())

    if len(indxx) == 0:
        offset_x=0.
        offset_y=0.
        n_match=0.
        rms_ra=-1.
        rms_dec=-1.
        id_common=0
        

    
    if len(indxx) == 1:
        n_match = ncommon_matrix[indxx[0],indyy[0]]+0.
        rms_ra = rms_ra_matrix[indxx[0],indyy[0]]+0.
        rms_dec = rms_dec_matrix[indxx[0],indyy[0]]+0.
        offset_x = -offset_x_matrix[indxx[0],indyy[0]]+0.
        offset_y = -offset_y_matrix[indxx[0],indyy[0]]+0.

    if len(indxx) > 1:

        tmp_offset_x_matrix = offset_x_matrix[indxx,indyy]+0.
        tmp_offset_y_matrix = offset_y_matrix[indxx,indyy]+0.
        dist_ = (tmp_offset_x_matrix**2.+tmp_offset_y_matrix**2.)**0.5
        
        (new_indxx,new_indyy) = np.where((offset_x_matrix**2+offset_y_matrix**2)**0.5 == dist_.min() )

        n_match = ncommon_matrix[new_indxx[0],new_indyy[0]]+0.
        rms_ra = rms_ra_matrix[new_indxx[0],new_indyy[0]]+0.
        rms_dec = rms_dec_matrix[new_indxx[0],new_indyy[0]]+0.
        offset_x = -offset_x_matrix[new_indxx[0],new_indyy[0]]+0.
        offset_y = -offset_y_matrix[new_indxx[0],new_indyy[0]]+0.



    return(offset_x,offset_y,n_match,rms_ra,rms_dec)



if __name__ == '__main__':

#  from astropy.io import fits
#  import numpy as np
#  from numpy import array
#  from photutils import datasets
#  from photutils import daofind
#  from astropy.stats import median_absolute_deviation as mad
#  #import scikit-image
#  import astropy
#  import scipy
#  import pywcs # WCS conversion routines
#  import pyfits
#  import copy 
#  import matplotlib.pyplot as plt
#  import time

  
#   MAIN MODULE --- to be interfaced with REFLEX ---
  warnings.filterwarnings("ignore")
 #getting the inputs and defyning the outputs
  parser = reflex.ReflexIOParser()
  parser.add_option("-i", "--in_sof", dest="in_sof")
#  parser.add_option("-j", "--in_dir", dest="in_dir")
  parser.add_output("-o", "--out_sof", dest="out_sof")
  parser.add_output("-p", "--messages", dest="messages")
  inputs  = parser.get_inputs()
  outputs = parser.get_outputs()
  in_sof = inputs.in_sof#reflex.parseSofJson(json.loads(inputs.in_sof))
  files=in_sof.files
  images=[]
  tables=[]
  if import_ok == 0:
     # print 'bu'
     # time.sleep(6)
      #raw_input("Press enter to continue")
#      time.sleep(6)
      outputs.out_sof = inputs.in_sof
      outputs.messages = ('Warning: Failing in importing some required Python modules.\n Check software requirements at:\n '
            ' https://www.eso.org/sci/software/pipelines/reflex_workflows/#software_prerequisites\n'
            ' or in the MUSE Reflex tutorial.\n\n '
            'Coordinates in the header will be used for alignment.\n')

      parser.write_outputs()
      sys.exit()
 
  for file in files:
 
      if file.category == 'IMAGE_FOV':
          images.append(str(file.name))
      if file.category == 'PIXTABLE_REDUCED':    
          tables.append(str(file.name))

# GETTING THE CATALOGUES, SORTING THE IMAGES IN TIME, COMPUTING 2D DISTANCE MATRIX
  sources = []
  RA=np.zeros(len(images),float)
  DEC=np.zeros(len(images),float)
  MJD=np.zeros(len(images),float)
  MJD_tbl=np.zeros(len(images),float)
  FLAGS=np.zeros(len(images),float)
  FLAGS[0] = 1.
  OFFSETS_RA=np.zeros(len(images),float)
  OFFSETS_DEC=np.zeros(len(images),float)
  distances=np.zeros([len(images),len(images)],float)

  for i in range(len(images)):
     # print images[i], tables[i]
      hdu  = pyfits.open(images[i])
      image = hdu[1].data 
  
      # REPLACE NaN values with 0
      where_are_NaNs = np.isnan(image)
      image[where_are_NaNs] = 0.
  
      header = hdu[0] 
      RA[i] = header.header['RA']
      DEC[i] = header.header['DEC']
      MJD[i] = header.header['MJD-OBS']
      wcs = pywcs.WCS(hdu[0].header)

      hdu_tbl  = pyfits.open(tables[i])
      header_tbl = hdu_tbl[0] 
      MJD_tbl[i] = header_tbl.header['MJD-OBS']

    
      thr = 15.
      junk =  daofind(image, fwhm=5.0, threshold=thr) 
      len_junk = len(junk)
      while len_junk > 80:
          thr=thr+5.
          junk =  daofind(image, fwhm=5.0, threshold=thr) 
          len_junk = len(junk)
        
      if len(junk) <= 5: 
         junk =  daofind(image, fwhm=5.0, threshold=10.) 
      if len(junk) <= 5: 
         junk =  daofind(image, fwhm=5.0, threshold=5.) 

      try:
          x=np.array(junk['xcentroid'])
          y=np.array(junk['ycentroid'])
          id_=np.array(junk['id'])
 #         sky = wcs.wcs_pix2sky(x,y,1)
          sky = wcs.wcs_pix2world(x,y,1)
          sources.append([id_,sky[0],sky[1]])
      except KeyError:
          sources.append([np.array([-1]),np.array([-999]),np.array([-999])])

  sorted=np.argsort(MJD)
  sorted_tbl=np.argsort(MJD_tbl)
  RA_sorted=RA[sorted]
  DEC_sorted=DEC[sorted]
  MJD_sorted=MJD[sorted]
  MJD_tbl_sorted=MJD_tbl[sorted_tbl]
  images_array = np.array(images)
  tables_array=np.array(tables)
  images_array_sorted=images_array[sorted]
  tables_array_sorted=tables_array[sorted_tbl]
  images_sorted = np.ndarray.tolist(images_array_sorted)
  tables_sorted = np.ndarray.tolist(tables_array_sorted)
 

  for i in range(len(images)):
      for j in range(len(images)):
          distances[i,j] = ((RA_sorted[i] - RA_sorted[j])**2. + (DEC_sorted[i] - DEC_sorted[j])**2.)**0.5


  # SELECTION OF WHICH CATALOGUE (of an image whose offsets are unknown) NEEDS TO BE COMPARED TO WHICH CATALOGUE (of an image whose offsets are known)
  # THE REFERENCE IMAGE (OLDEST) HAS KNOWN OFFSETS (0,0)


  offsets_to_the_reference_RA = np.zeros(len(images))
  offsets_to_the_reference_DEC = np.zeros(len(images))

  for i in range(1,len(images),1):
    #  print FLAGS
      processed, = np.where(FLAGS == 1.)
      not_processed, = np.where(FLAGS == 0.)

      replace = distances*0-1.


      for k1 in processed:
          for k2 in not_processed:
              replace[k1,k2] = distances[k1,k2]
            

 
      MIN_dist = distances[processed][:,[not_processed]].min()
      (ic,jc) = np.where((replace == MIN_dist) & (replace >= 0) )


      sel_i = ic[0]   # sel_i is the index of an image with known offsets, that I will use as reference to compute the offsets for the image(sel_j)
      sel_j = jc[0]   # sel_j is the index of a non processed image, which has a minimum distance from the images that have known offsets
                    # the comparison will be done between the catalogues sel_i (reference) and sel_j.

      #  Cross matching catalogues (i: unknown offsets; j known offsets / reference image)
      offset_x,offset_y,n_match,rms_ra,rms_dec = compute_offsets(sources[sel_i][0],sources[sel_i][1],sources[sel_i][2],sources[sel_j][0],sources[sel_j][1],sources[sel_j][2])

     # print

      FLAGS[sel_j] = 1.  # now I know the offsets of the image sel_j-th image, and I can consider it as processed
      #print sel_i, sel_j, images[sel_j],offset_x,offset_y
      offsets_to_the_reference_RA[sel_j]  = offsets_to_the_reference_RA[sel_i]  + offset_x
      offsets_to_the_reference_DEC[sel_j] = offsets_to_the_reference_DEC[sel_i] + offset_y

     # print 'reference: ' , images_sorted[0]
     # print 'image to align:', images_sorted[sel_j],'; using ', images_sorted[sel_i]
     # print 'RA_off, DEC_off',offsets_to_the_reference_RA[sel_j], offsets_to_the_reference_DEC[sel_j]


      hdu = pyfits.open(tables_sorted[sel_j],mode='update')
      hdu[0].header['RA'] = hdu[0].header['RA'] + offsets_to_the_reference_RA[sel_j]
      hdu[0].header['DEC'] = hdu[0].header['DEC'] + offsets_to_the_reference_DEC[sel_j]
      hdu[0].header['HIERARCH REFLEX ALIGNED'] = 1
      hdu[0].header['HIERARCH REFLEX APPOFFRA'] = (offsets_to_the_reference_RA[sel_j],'Median offset in RA (deg)')
      hdu[0].header['HIERARCH REFLEX APPOFFDEC'] = (offsets_to_the_reference_DEC[sel_j],'Median offset in DEC (deg)')
      hdu[0].header['HIERARCH REFLEX RMSOFFRA'] = (rms_ra,'STDDEV of RA offset [deg]')
      hdu[0].header['HIERARCH REFLEX RMSOFFDEC'] = (rms_dec,'STDDEV of DEC offset [deg]')
      hdu[0].header['HIERARCH REFLEX NUMSTARS'] = (n_match,'N. of sources used for alignment')
      hdu.flush() 
  #  tables_sorted[sel_j] ToDo
      hdu = pyfits.open(images_sorted[sel_j],mode='update')
      hdu[0].header['CRVAL1'] = hdu[0].header['CRVAL1'] + offsets_to_the_reference_RA[sel_j]
      hdu[0].header['CRVAL2'] = hdu[0].header['CRVAL2'] + offsets_to_the_reference_DEC[sel_j]
      hdu[0].header['HIERARCH REFLEX ALIGNED'] = 1
      hdu[0].header['HIERARCH REFLEX APPOFFRA'] = (offsets_to_the_reference_RA[sel_j],'Median offset in RA (deg)')
      hdu[0].header['HIERARCH REFLEX APPOFFDEC'] = (offsets_to_the_reference_DEC[sel_j],'Median offset in DEC (deg)')
      hdu[0].header['HIERARCH REFLEX RMSOFFRA'] = (rms_ra,'STDDEV of RA offset [deg]')
      hdu[0].header['HIERARCH REFLEX RMSOFFDEC'] = (rms_dec,'STDDEV of DEC offset [deg]')
      hdu[0].header['HIERARCH REFLEX NUMSTARS'] = (n_match,'N. of sources used for alignment')
      hdu.flush()


#      fig1 = plt.figure()
#      plt.plot(sources[sel_i][1], sources[sel_i][2],'bs',sources[sel_j][1],sources[sel_j][2],'g^')
#      plt.show()
#      plt.plot(sources[sel_i][1], sources[sel_i][2],'bs',sources[sel_j][1]+offset_x,sources[sel_j][2]+offset_y,'g^')
#      plt.show()
   

  #for i in range(1,len(images),1):
  #  print tables_sorted[i], offsets_to_the_reference_RA[i], offsets_to_the_reference_DEC[i] #
#  for i in range(len(images)):
#      print images_sorted[i], tables_sorted[i],MJD_sorted[i],MJD_tbl_sorted[i]

#  raw_input("Press enter to continue")
  outputs.out_sof = inputs.in_sof
  parser.write_outputs()
  sys.exit()
 


