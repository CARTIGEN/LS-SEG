#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name        : segmentation.py
# Description : Module of segmentation filters.  
# Authors     : William A. Romero R.     <william.romero@umontpellier.fr>
#                                        <contact@waromero.com>
#               Susana Uribe Velásquez   <susana.uribe7@eia.edu.co>
#               Daniel Restrepo Quiñones <daniel.restrepo53@eia.edu.co>
#-------------------------------------------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass

import SimpleITK as sitk
import numpy as np


def get_2D_image_from( image_3d, 
                         method='SLICE', 
                         slice_index=None, axis=2 ):
    """
    Return a 2D image from a 3D image using:

        - SLICE index, 
        - Max. Intensity Projection (MIP), or 
        - Mean Projection (MP)

    <axis> defines the axis along which to project:
        - 0=X, 1=Y and  2=Z (within MIP/MP).
    """
    if method == "SLICE":
        if slice_index is None:
            raise ValueError("slice_index must be provided for 'slice' method.")

        return image_3d[:, :, slice_index]
    
    elif method == "MIP":
        return sitk.MaximumProjection(image_3d, projectionDimension=axis)
    
    elif method == "MP":
        return sitk.MeanProjection(image_3d, projectionDimension=axis)
    
    else:
        raise ValueError("Unsupported method. Use 'SLICE', 'MIP', or 'MP'.")


class SubImageManager2DException(Exception):
    """
    Default exception from SubImageManager2D methods.
    """
    pass


class SubImageManager2D(object):
    """
    Threshold-Based Segmentation.
    """
    def __init__( self,
                  image:sitk.Image,
                  centre_col:int, 
                  centre_row:int,
                  width:int, 
                  height:int ):
        """
        Default constructor
        """
        self.description = "Sub-Image Manager (2D)"
        self.image = image
        self.centre_col = centre_col
        self.centre_row = centre_row
        self.width = width
        self.height = height

        self.start_col = 0
        self.start_row = 0

        self.end_col = 0
        self.end_row = 0        

        self.calculate_indices()


    def __str__(self):
        """
        Default human-readable description of the class.
        """
        output_str = "\n{description}\n\n".format(description = self.description)
        output_str += "\tCentre Column: {}\n".format(self.centre_col) 
        output_str += "\tCentre Row: {}\n".format(self.centre_row) 
        output_str += "\tWidth: {}\n".format(self.width) 
        output_str += "\tHeight: {}\n\n".format(self.height) 

        if self.image is not None:
            output_str += str(self.image)

        return output_str


    def calculate_indices(self):
        """
        Extract a region of interest from the image.    
        """        
        self.start_col = int(self.centre_col - self.width // 2)
        self.start_row = int(self.centre_row - self.height // 2)
        
        image_size = self.image.GetSize()
        image_width = image_size[0]
        image_height = image_size[1]
        
        self.start_col = max(0, min(self.start_col, image_width - 1))
        self.start_row = max(0, min(self.start_row, image_height - 1))
        
        self.end_col = min(self.start_col + self.width, image_width)
        self.end_row = min(self.start_row + self.height, image_height)


    def extract_roi( self ) -> sitk.Image:
        """
        Extract a region of interest from the image.    
        """ 
        try:
            roi_size = [self.end_col - self.start_col, self.end_row - self.start_row]
            roi_start_index = [self.start_col, self.start_row]

            roi = sitk.RegionOfInterest( self.image, 
                                         size = roi_size, 
                                         index = roi_start_index )
            
        except Exception as exception:
            print("[SubImageManager2D::Execution Exception] %s" % str(exception))
            raise SubImageManager2DException(str(exception))            

        return roi
    

    def get_empty_image_with(self, roi) -> sitk.Image:
        """
        Insert a region of interest back into the original image space.
        """
        output_image = sitk.Image(self.image.GetSize(), self.image.GetPixelIDValue())
        output_image.SetOrigin(self.image.GetOrigin())
        output_image.SetSpacing(self.image.GetSpacing())
        output_image.SetDirection(self.image.GetDirection())

        # Iterate through the ROI and place it into the original image
        for row in range(self.start_row, self.end_row):
            for col in range(self.start_col, self.end_col):
                output_image.SetPixel(col, row, roi.GetPixel(col - self.start_col, row - self.start_row))
        
        return sitk.Cast(output_image, sitk.sitkUInt8)        


@dataclass
class SegmentationModel:
    """
    Segmentation.
    """
    index: int = -1
    name: str = "None"
    description: str = "None"
    file_path: str = "None"


class SegmentationException(Exception):
    """
    Default exception from segmentation execution.
    """
    pass


class Segmentation(ABC):
    """
    Segmentation Abstract Class.
    """
    @abstractmethod
    def fnc(self):
        """
        Default fnc method.
        """
        pass


    @abstractmethod
    def execute(self):
        """
        Execute segmentation.
        """
        pass


class ThresholdSegmentation(Segmentation):
    """
    Threshold-Based Segmentation.
    """
    def __init__( self, 
                   image:sitk.Image, 
                   lb = 0, 
                   ub = 0 ):
        """
        Default constructor
        """
        self.description = "Threshold-Based segmentation."
        self.image = image
        self.lower_threshold = lb
        self.upper_threshold = ub

        self.__automatic_thresholds = False

        self.__bins = 27
        self.__lbp = 0.46
        self.__ubp = 0.81


    def __str__(self):
        """
        Default human-readable description of the class.
        """
        output_str = "\n{description}\n\n".format(description = self.description)
        output_str += "\tLower-Threshold: {}\n".format(self.lower_threshold) 
        output_str += "\tUpper-Threshold: {}\n\n".format(self.upper_threshold) 

        output_str += "\tHistogram bins: {}\n".format(self.__bins)
        output_str += "\tLower-Bound percentage: {}\n".format(self.__lbp)
        output_str += "\tUpper-Bound percentage: {}\n\n".format(self.__ubp)

        
        if self.image is not None:
            output_str += str(self.image)

        return output_str


    @property
    def hist_bins(self):
        """
        Histogram bins.
        """
        return self.__bins
  
    
    @property
    def sigma_lbp(self):
        """
        Set the lower-bound percentage.
        """
        return self.__lbp

    
    @property
    def sigma_ubp(self):
        """
        Set the lower-bound percentage.
        """
        return self.__ubp
        
    
    @hist_bins.setter
    def hist_bins(self, bins):
        """
        Set the number of bins.
        """
        self.__bins = bins


    @sigma_lbp.setter
    def sigma_lbp(self, perc):
        """
        Set the lower-bound percentage.
        """
        self.__lbp = perc

        
    @sigma_ubp.setter
    def sigma_ubp(self, perc):
        """
        Set the upper-bound percentage.
        """
        self.__ubp = perc
        

    def set_automatic_thresholds_ON(self):
        """
        Set automatic calculation of the lower and upper thresholds.
        """
        self.__automatic_thresholds = True


    def fnc(self):
        """
        Not required
        """
        return 0


    def calculate_thresholds(self):
        """
        Calculate lower and upper thresholds.
        """
        hthreshold_filter = sitk.HuangThresholdImageFilter()
        hthreshold_filter.SetNumberOfHistogramBins(self.__bins)
        hthreshold_filter.SetInsideValue(0)
        hthreshold_filter.SetOutsideValue(1)

        hthreshold_output = hthreshold_filter.Execute(self.image)

        stats_filter = sitk.LabelStatisticsImageFilter()
        stats_filter.Execute(self.image, hthreshold_output)

        mean =  stats_filter.GetMean(1)
        sigma = stats_filter.GetSigma(1)
        
        self.lower_threshold = np.floor(mean - (sigma*self.__lbp))
        self.upper_threshold = np.ceil(mean + (sigma*self.__ubp))


    def execute(self):
        """
        Execute segmentation.
        """
        try:

            if self.__automatic_thresholds:
                self.calculate_thresholds()

            threshold_filter = sitk.BinaryThresholdImageFilter()
            threshold_filter.SetLowerThreshold(self.lower_threshold)
            threshold_filter.SetUpperThreshold(self.upper_threshold)
            threshold_filter.SetOutsideValue(0)
            threshold_filter.SetInsideValue(1)
            threshold_output = threshold_filter.Execute(self.image)

            connected_components_filter = sitk.ConnectedComponentImageFilter()
            connected_components_filter.SetFullyConnected(False)
            connected_components = connected_components_filter.Execute(threshold_output)

            labels_stats_filters = sitk.LabelShapeStatisticsImageFilter()
            labels_stats_filters.Execute(connected_components)

            components = labels_stats_filters.GetLabels()

            max_size = 0
            max_label_index = 1

            for label_index in components:
                current_size = labels_stats_filters.GetNumberOfPixels(label_index)

                if (current_size > max_size) :
                        max_size = current_size
                        max_label_index = label_index


            threshold_filter = sitk.BinaryThresholdImageFilter()
            threshold_filter.SetLowerThreshold(max_label_index)
            threshold_filter.SetUpperThreshold(max_label_index)
            threshold_filter.SetOutsideValue(0)
            threshold_filter.SetInsideValue(1)
            max_connected_component = threshold_filter.Execute(connected_components)

            fill_filter = sitk.BinaryFillholeImageFilter()
            
            output_segmentation = fill_filter.Execute(max_connected_component)

            return output_segmentation

        except Exception as exception:
            print("[ThresholdSegmentation::Execution Exception] %s" % str(exception))
            raise SegmentationException(str(exception))


class ModelBasedSegmentation(Segmentation):
    """
    Threshold-Based Segmentation.
    """
    def __init__( self, 
                  inputImage:sitk.Image, 
                  inputModel:SegmentationModel ) -> sitk.Image:
        """
        Default constructor
        """
        self.description = "Model-Based segmentation."
        self.image = inputImage
        self.model = inputModel

        self.__loadModel


    def __str__(self):
        """
        Default human-readable description of the class.
        """
        output_str = "\n{description}\n\n".format(description = self.description)

        if self.image is not None:
            output_str += str(self.image)

        return output_str


    def fnc(self):
        """
        Not required
        """
        return 0


    def execute(self):
        """
        Execute segmentation.
        """
        try:
            #---------------------------
            # TODO: Segmentation.
            #---------------------------

            segmentation_output = None

            return segmentation_output

        except Exception as exception:
            print("[ModelBasedSegmentation::Execution Exception] %s" % str(exception))
            raise SegmentationException(str(exception))


