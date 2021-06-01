# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 13:53:45 2020

@author: wayne
"""

import cv2

class BoundingBoxWidget(object):
    def __init__(self):
        # path 
        path = r'C:\Workstation\PreviousProject\LidarCHMProject\ForestDisturbance\Run3dForestFragPR\ortho.tif'
        # Using cv2.imread() method 
        self.original_image = cv2.imread(path)
        #self.original_image = cv2.resize(self.original_image, (960, 540))       # Resize image
        self.clone = self.original_image.copy()

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

        # Bounding box reference points
        self.image_coordinates = []

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]

        # Record ending (x,y) coordintes on left mouse button release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            print('top left: {}, bottom right: {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
            print('x,y,w,h : ({}, {}, {}, {})'.format(self.image_coordinates[0][0], self.image_coordinates[0][1], self.image_coordinates[1][0] - self.image_coordinates[0][0], self.image_coordinates[1][1] - self.image_coordinates[0][1]))

            # Draw rectangle 
            cv2.rectangle(self.clone, self.image_coordinates[0], self.image_coordinates[1], (36,255,12), 2)
            cv2.imshow("image", self.clone) 

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone

if __name__ == '__main__':
    boundingbox_widget = BoundingBoxWidget()
    
    while True:
        
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.imshow('image', boundingbox_widget.show_image())  # Show image
        key = cv2.waitKey(1)

        # Close program with keyboard 'q'
        if key == ord('q'):
            cv2.destroyAllWindows()
            exit(1)