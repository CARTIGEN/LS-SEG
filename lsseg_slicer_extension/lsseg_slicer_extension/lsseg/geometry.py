#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name        : geometry.py
# Description : The computational geometry functions module.
# Authors     : William A. Romero R.     <william.romero@umontpellier.fr>
#                                        <contact@waromero.com>
#               Susana Uribe Velásquez   <susana.uribe7@eia.edu.co>
#               Daniel Restrepo Quiñones <daniel.restrepo53@eia.edu.co>
#-------------------------------------------------------------------------------
import scipy.optimize
import SimpleITK as sitk
import numpy as np


class GeometryException(Exception):
    """
    Default exception from segmentation execution.
    """
    pass


class CobbAngleCalculator(object):
    """
    Calculate the Cobb angle between two vertebrae.
    """
    def __init__( self, 
                  image:sitk.Image,
                  label_map:sitk.Image,
                  uv_label_index = 0, 
                  lv_label_index = 0 ):
        """
        Default constructor
        """
        self.description = "Cobb Angle Calculator Class."
        self.image = image
        self.label_map = label_map
        self.lv_label_index = lv_label_index
        self.uv_label_index = uv_label_index

        self.dimension = image.GetDimension()

        self.uv_oriented_bbox_vertices = None
        self.lv_oriented_bbox_vertices = None

        self.uv_p1 = None
        self.uv_p2 = None
        self.lv_p1 = None
        self.lv_p2 = None

        self.intersection_point = None

        self.cobb_angle = 0


    def __str__(self):
        """
        Default human-readable description of the class.
        """
        output_str = "\n{description}\n\n".format(description = self.description)
        output_str += "\tImage dimension: {}\n".format(self.dimension)         
        output_str += "\tLower vertebra label index: {}\n".format(self.lv_label_index) 
        output_str += "\tUpper vertebra label index: {}\n\n".format(self.uv_label_index) 

        if self.image is not None:
            output_str += str(self.image)

        if self.label_map is not None:
            output_str += str(self.label_map)

        return output_str


    def __calc_uv_bbox_vertices(self):
        """
        Calculate UV oriented bounding box vertices.
        """
        lshape_stats_filter = sitk.LabelShapeStatisticsImageFilter()
        lshape_stats_filter.SetBackgroundValue(0)       
        lshape_stats_filter.ComputeOrientedBoundingBoxOn()
        lshape_stats_filter.Execute(self.label_map)
        
        bounding_box_vertices = lshape_stats_filter.GetOrientedBoundingBoxVertices(self.uv_label_index)

        # bbox_direction_vect = lshape_stats_filter.GetOrientedBoundingBoxDirection(self.uv_label_index)
        
        # bbox_direction_mat = [ bbox_direction_vect[0], bbox_direction_vect[3], bbox_direction_vect[6],
        #                        bbox_direction_vect[1], bbox_direction_vect[4], bbox_direction_vect[7],
        #                        bbox_direction_vect[2], bbox_direction_vect[5], bbox_direction_vect[8] ]


        if( len(bounding_box_vertices) == 24 ):            
            self.uv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(8,3)

            # #___DEBUG___
            # uv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(8,3)            
            # T = sitk.Similarity3DTransform()
            # T.SetMatrix(bbox_direction_mat)
            # T.SetCenter(lshape_stats_filter.GetOrientedBoundingBoxOrigin(self.uv_label_index))

            # self.uv_oriented_bbox_vertices = np.zeros_like(uv_oriented_bbox_vertices)
            # for i, j in enumerate(uv_oriented_bbox_vertices):
            #     self.uv_oriented_bbox_vertices[i] = T.TransformPoint(j)
            # #___END___
            
        if( len(bounding_box_vertices) == 8 ):
            self.uv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(4,2)

 
    def __calc_lv_bbox_vertices(self):
        """
        Calculate LV oriented bounding box vertices.
        """
        lshape_stats_filter = sitk.LabelShapeStatisticsImageFilter()
        lshape_stats_filter.ComputeOrientedBoundingBoxOn()
        lshape_stats_filter.SetBackgroundValue(0)
        lshape_stats_filter.Execute(self.label_map)
        
        bounding_box_vertices = lshape_stats_filter.GetOrientedBoundingBoxVertices(self.lv_label_index)

        # bbox_direction_vect = lshape_stats_filter.GetOrientedBoundingBoxDirection(self.lv_label_index)
        
        # bbox_direction_mat = [ bbox_direction_vect[0], bbox_direction_vect[3], bbox_direction_vect[6],
        #                        bbox_direction_vect[1], bbox_direction_vect[4], bbox_direction_vect[7],
        #                        bbox_direction_vect[2], bbox_direction_vect[5], bbox_direction_vect[8] ]
        
        if( len(bounding_box_vertices) == 24 ): 
            self.lv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(8,3)

            # #___DEBUG___
            # lv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(8,3)
            # T = sitk.Similarity3DTransform()
            # T.SetMatrix(bbox_direction_mat)
            # T.SetCenter(lshape_stats_filter.GetOrientedBoundingBoxOrigin(self.lv_label_index))

            # self.lv_oriented_bbox_vertices = np.zeros_like(lv_oriented_bbox_vertices)
            # for i, j in enumerate(lv_oriented_bbox_vertices):
            #     self.lv_oriented_bbox_vertices[i] = T.TransformPoint(j)   
            # #___DEBUG___    
            
        if( len(bounding_box_vertices) == 8 ):
            self.lv_oriented_bbox_vertices = np.array(bounding_box_vertices).reshape(4,2)


    def __set_bbox_tan_line_points(self):
        """
        Set the two points for the tangent  line to the upper  plane /
        upper vertebra  bounding box  and two  points for  the tangent
        line to the lower plane / lower vertebra bounding box.
        """
        if( self.uv_oriented_bbox_vertices.size == 24 ):
            
            self.uv_p1 = [ self.uv_oriented_bbox_vertices[0,0],
                           self.uv_oriented_bbox_vertices[0,1],
                           self.uv_oriented_bbox_vertices[0,2] ]

            self.uv_p2 = [ self.uv_oriented_bbox_vertices[1,0], 
                           self.uv_oriented_bbox_vertices[1,1], 
                           self.uv_oriented_bbox_vertices[1,2] ]

            self.lv_p1 = [ self.lv_oriented_bbox_vertices[6,0], 
                           self.lv_oriented_bbox_vertices[6,1], 
                           self.lv_oriented_bbox_vertices[6,2] ]

            self.lv_p2 = [ self.lv_oriented_bbox_vertices[7,0], 
                           self.lv_oriented_bbox_vertices[7,1], 
                           self.lv_oriented_bbox_vertices[7,2] ]

            return self.uv_p1, self.uv_p2, self.lv_p1, self.lv_p2


        if( self.uv_oriented_bbox_vertices.size == 8 ):
            
            self.uv_p1 = [ self.uv_oriented_bbox_vertices[0,0],
                           self.uv_oriented_bbox_vertices[0,1] ]

            self.uv_p2 = [ self.uv_oriented_bbox_vertices[1,0], 
                           self.uv_oriented_bbox_vertices[1,1] ]

            self.lv_p1 = [ self.lv_oriented_bbox_vertices[2,0], 
                           self.lv_oriented_bbox_vertices[2,1] ]

            self.lv_p2 = [ self.lv_oriented_bbox_vertices[3,0], 
                           self.lv_oriented_bbox_vertices[3,1] ]
        

            return self.uv_p1, self.uv_p2, self.lv_p1, self.lv_p2


    def __calc_angle_between_lines(self):
        """
        Calculates the angle between two lines:
            line1 = { (p1x, p1y, p1z), (p2x, p2y, p2z) }
            line2 = { (q1x, q1y, q1z), (q2x, q2y, q2z) }    
        """
        p1 = np.array(self.uv_p1)
        p2 = np.array(self.uv_p2)
        q1 = np.array(self.lv_p1)
        q2 = np.array(self.lv_p2)

        # Direction vectors.
        line1 = p2 - p1
        line2 = q2 - q1

        dot_product = np.dot(line1, line2)

        # Magnitudes (norms).
        norm_line1 = np.linalg.norm(line1)
        norm_line2 = np.linalg.norm(line2)

        cos_theta = dot_product / (norm_line1 * norm_line2)

        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        theta_rad = np.arccos(cos_theta)

        # Convert the angle to degrees
        theta_deg = np.degrees(theta_rad)

        return theta_deg

    
    def __calc_intersection(self):
        """
        Calculate the intersection point between:
        (p1p2) and (q1q2).
        """
        p1 = np.array(self.uv_p1)
        p2 = np.array(self.uv_p2)
        q1 = np.array(self.lv_p1)
        q2 = np.array(self.lv_p2)

        def errFunc(estimates):
            s, t = estimates
            x = p1 + s * (p2 - p1) - (q1 + t * (q2 - q1))
            return x

        estimates = [1, 1]

        sols = scipy.optimize.least_squares(errFunc, estimates)
        s,t = sols.x

        x1 = p1[0] + s * (p2[0] - p1[0])
        x2 = q1[0] + t * (q2[0] - q1[0])
        y1 = p1[1] + s * (p2[1] - p1[1])
        y2 = q1[1] + t * (q2[1] - q1[1])
        z1 = p1[2] + s * (p2[2] - p1[2])
        z2 = q1[2] + t * (q2[2] - q1[2])

        x = (x1 + x2) / 2  
        y = (y1 + y2) / 2  
        z = (z1 + z2) / 2  

        self.intersection_point = [x, y, z]


    def execute(self):
        """
        Main public method for executing the method.
        """
        self.__calc_uv_bbox_vertices()
        self.__calc_lv_bbox_vertices()

        self.__set_bbox_tan_line_points()

        self.cobb_angle = self.__calc_angle_between_lines()

        self.__calc_intersection()

        
    def get_uv_oriented_bbox_vertices(self):
        """
        Return upper vertebra oriented bounding box vertices.
        """
        return self.uv_oriented_bbox_vertices


    def get_lv_oriented_bbox_vertices(self):
        """
        Return lower vertebra oriented bounding box vertices.
        """
        return self.lv_oriented_bbox_vertices


    def get_uv_oriented_bbox_indices(self):
        """
        Return upper vertebra oriented bounding box vertices.
        """
        vertices_img_indices = np.zeros_like(self.uv_oriented_bbox_vertices)
        for i, j in enumerate(self.uv_oriented_bbox_vertices):
            vertices_img_indices[i] = self.label_map.TransformPhysicalPointToIndex(j)

        return vertices_img_indices


    def get_lv_oriented_bbox_indices(self):
        """
        Return lower vertebra oriented bounding box vertices.
        """
        vertices_img_indices = np.zeros_like(self.lv_oriented_bbox_vertices)
        for i, j in enumerate(self.lv_oriented_bbox_vertices):
            vertices_img_indices[i] = self.label_map.TransformPhysicalPointToIndex(j)

        return vertices_img_indices
    
    
    def get_cobb_angle(self):
        """
        Return the value of the Cobb angle.
        """
        return self.cobb_angle    


    def get_intersection_point_index(self):
        """
        Return the intersection point between uv and lv.
        """
        intersection_point = self.image.TransformPhysicalPointToIndex((self.intersection_point[0],
                                                                       self.intersection_point[1],
                                                                       self.intersection_point[2]))

        return intersection_point

    
    def get_angle_indices(self):
        """
        Return the 3-Point of the Cobb angle.
        """
        ca_p1 = self.image.TransformPhysicalPointToIndex((self.uv_p1[0],
                                                          self.uv_p1[1],
                                                          self.uv_p1[2]))

        ca_p2 = self.image.TransformPhysicalPointToIndex((self.intersection_point[0],
                                                          self.intersection_point[1],
                                                          self.intersection_point[2]))        
        
        ca_p3 = self.image.TransformPhysicalPointToIndex((self.lv_p1[0],
                                                          self.lv_p1[1],
                                                          self.lv_p1[2]))


        return ca_p1, ca_p2, ca_p3

