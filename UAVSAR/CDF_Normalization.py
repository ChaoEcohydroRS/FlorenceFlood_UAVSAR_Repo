# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:36:47 2019

@author: wayne
"""



import numpy as np
import imageio
import sys



def histeq(im,nbr_bins=256,normed=True):

   #get image histogram
   imhist,bins = np.histogram(im.flatten(),nbr_bins,normed=True)
   cdf = imhist.cumsum() #cumulative distribution function
   
#   cdf = 255 * cdf / cdf[-1] #normalize
   
#   cdf = cdf * imhist.max()/ cdf.max().astype('uint8')
   
   cdf_m = np.ma.masked_equal(cdf,0)
   cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
   cdf = np.ma.filled(cdf_m,0).astype('uint8')

   #use linear interpolation of cdf to find new pixel values
#   im2 = np.interp(im.flatten(),bins[:-1],cdf)
   im2 = cdf[im]

   return im2.reshape(im.shape), cdf



#def get_histogram(img):
#  '''
#  calculate the normalized histogram of an image
#  '''
#  height, width,channel = img.shape
#  hist = [0.0] * 256
#  for c in range(channel):
#      for i in range(height):
#        for j in range(width):
#          hist[img[i, j, c]]+=1
#  return np.array(hist)/(height*width)
#
#def get_cumulative_sums(hist):
#  '''
#  find the cumulative sum of a numpy array
#  '''
#  return [sum(hist[:i+1]) for i in range(len(hist))]
#
#def normalize_histogram(img,nbr_bins=256):
#  # calculate the image histogram
#  #imhist = get_histogram(img)
#  
#  #get image histogram
#  imhist,bins = np.histogram(im.flatten(),nbr_bins,normed=True)
#  
#  # get the cumulative distribution function
#  cdf = np.array(get_cumulative_sums(imhist))
#  
#  #cumulative distribution function
#  #cdf = imhist.cumsum() 
#  
#  # determine the normalization values for each unit of the cdf
#  sk = np.uint8(255 * cdf)
#  
#  # normalize the normalization values
#  height, width = img.shape
#  Y = np.zeros_like(img)
#  for i in range(0, height):
#    for j in range(0, width):
#      Y[i, j] = sk[img[i, j]]
#  # optionally, get the new histogram for comparison
#  new_hist = get_histogram(Y)
#  # return the transformed image
#  return Y


inputFile=r'C:\Workstation\PreviousProject\LidarCHMProject\ForestDisturbance\LidarLasFile\Download\PR_11March2017_FIA12\photography\orthomosaic\Shadow.tif'
outputFolder='C:\\Workstation\\PreviousProject\\LidarCHMProject\\ForestDisturbance\\Run3dForestFragPR\\'
#img = imread(sys.argv[1])
img = imageio.imread(inputFile)
#normalized = normalize_histogram(img,256)

normalized,cdf =histeq(img,256,normed=True)

imageio.imwrite(outputFolder + 'UrbanShadow_normalized.tif', normalized)
