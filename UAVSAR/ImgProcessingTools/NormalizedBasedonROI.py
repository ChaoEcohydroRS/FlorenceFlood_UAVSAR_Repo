# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 14:14:52 2020

@author: wayne
"""

import cv2
import numpy as np

path = r'C:\Workstation\PreviousProject\LidarCHMProject\ForestDisturbance\Run3dForestFragPR\ortho.tif'
# Load image as grayscale and crop ROI
image = cv2.imread(path)
x, y, w, h = 384, 615, 315, 169
ROI = image[y:y+h, x:x+w]

# Calculate mean and STD
mean, STD  = cv2.meanStdDev(ROI)

# Clip frame to lower and upper STD
offset = 0.2
clipped = np.clip(image, mean - offset*STD, mean + offset*STD).astype(np.uint8)

# Normalize to range
result = cv2.normalize(clipped, clipped, 0, 255, norm_type=cv2.NORM_MINMAX)

cv2.imshow('image', image)
cv2.imshow('ROI', ROI)
cv2.imshow('result', result)
cv2.waitKey()
