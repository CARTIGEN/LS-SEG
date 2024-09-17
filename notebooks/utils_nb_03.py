#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name        : util.nb_03.py
# Description : Useful functions for data loading and visualization.
#               (Notebook No. 3)
# Authors     : William A. Romero R.     <william.romero@umontpellier.fr>
#                                        <contact@waromero.com>
#-------------------------------------------------------------------------------
import SimpleITK as sitk
import numpy as np

import plotly.graph_objects as go
import plotly.colors as colours 
from   plotly.subplots import make_subplots

# import plotly.io as pio
# pio.renderers.default='browser'


def load_image_from(input_file, NP_ARRAY=False):
    """
    [I/O] Load images
    """
    image = None

    try:            
        image = sitk.Cast(sitk.ReadImage( input_file ), sitk.sitkUInt16 )
        
        if NP_ARRAY:
            imageArray = np.flip( sitk.GetArrayFromImage(image), 1 )
            # imageArray = sitk.GetArrayFromImage(image)

            return imageArray
        
        else:
            return image
        
    except Exception as exception:
        print("[LS-Seg Notebooks::load_image_from] %s" % str(exception))

        
colour_scale= [ [0,   'rgb(  0,   0,   0)'],
                [0.16,'rgb(255, 190,  11)'],
                [0.33,'rgb(251,  86,   7)'],
                [0.48,'rgb(255,   0, 110)'],
                [0.64,'rgb(131,  56, 236)'],
                [1,   'rgb(58,  134, 255)'] ]


def flip_point(point, axis, reference):
    """
    [VISUALISATION] Flip a point across an axis.
    """
    x, y, z = point    
    if axis == 1:
        flipped_x = 2 * reference - x
        return [flipped_x, y, z]
    
    elif axis == 2:
        flipped_y = 2 * reference - y
        return [x, flipped_y, z]
    
    elif axis == 3:
        flipped_z = 2 * reference - z
        return [x, y, flipped_z]
    
    else:
        print("[LS-Seg Notebooks::flip_point] Invalid axis! Choose '1=X', '2=Y', or '3=Z'.")


def display_images( image:np.array,
                    segmentation:np.array,
                    xv_coords:np.array = None,
                    yv_coords:np.array = None,
                    xca_coords:np.array = None,
                    yca_coords:np.array = None ) -> None:
    """
    [VISUALISATION] Plot image and segmentation.
    """
    output = make_subplots( rows=1, cols=2, 
                            shared_xaxes=True,
                            shared_yaxes=True,
                            vertical_spacing=0.009,
                            horizontal_spacing=0.009,
                            subplot_titles=("Image", "Segmentation"))    

    img = go.Heatmap( name="IMAGE",
                      z = image,
                      colorscale = colours.sequential.Greys_r,
                      zsmooth = 'best',
                      showscale=False,
                      hovertemplate = 'Row: %{y}, Col: %{x}, Value: %{z:}' )
    
    seg = go.Heatmap( name="SEGMENTATION",
                      z = segmentation,
                      showscale=False,
                      opacity=0.63,
                      colorscale=colour_scale,
                      hovertemplate = 'Row: %{y}, Col: %{x}, Label: %{z}' )    

    if xv_coords is not None:
        points = go.Scatter( x=xv_coords,
                             y=yv_coords,
                             mode="markers",
                             marker=dict( size=8,
                                          color=['red', 'green', 'blue', 'orange'] ),
                             name="Vertices"
                            )
        
    if xca_coords is not None:
        angle = go.Scatter( x=xca_coords,
                            y=yca_coords,
                            mode="lines",
                            line=dict(  width=3,
                                        color='lime' ),
                            name="Cobb Angle"
                            )

    output.add_trace(img, row=1, col=1)

    if xv_coords is not None:
        output.add_trace(points, row=1, col=1)

    output.add_trace(img, row=1, col=2)
    output.add_trace(seg, row=1, col=2)

    if xca_coords is not None:
        output.add_trace(angle, row=1, col=2)    
    
    output.update_yaxes( scaleanchor="x", 
                         scaleratio=1,
                         showticklabels = False, 
                         showgrid = False )
    
    output.update_xaxes( scaleanchor="y", 
                         scaleratio=1,
                         showticklabels = False, 
                         showgrid = False )

    output.update_layout( dict( margin=dict(l=1, r=1, t=27, b=1),
                                plot_bgcolor='black') )    

    output.show()
    

def display_bboxes( x_uv, y_uv, z_uv,
                    x_lv, y_lv, z_lv ) -> None:
    """
    [VISUALISATION] Plot bounding boxes.
    """
    output = make_subplots( rows=1, cols=2, 
                            vertical_spacing=0.009,
                            horizontal_spacing=0.009,
                            subplot_titles=("Upper Vertebra Oriented Bounding Box", 
                                            "Lower Vertebra Oriented Bounding Box"),
                            specs=[ [{'type': 'scene'}, {'type': 'scene'}] ] 
                          )    


    #---------------------------
    # UPPER VERTEBRA, vertices.
    # Bottom plane vertices(bpv)
    #---------------------------    
    uv_bpv = go.Scatter3d( x=x_uv[0:4],
                           y=y_uv[0:4],
                           z=z_uv,
                           mode="markers",
                           name="Upper Vertebra (BPV)",
                           marker=dict( size=8,
                                        color=['red', 'green', 'blue', 'orange'] ) 
                         )

    #---------------------------
    # UPPER VERTEBRA, 3D Mesh.
    # Upper plane.
    #---------------------------        
    i, j, k, l = 0, 1, 2, 3
    uv_bp = go.Mesh3d( x=x_uv,
                       y=y_uv,
                       z=z_uv,
                       i=[0, 1],
                       j=[1, 5],
                       k=[4, 4],
                       opacity=0.5,
                       color='lightblue' )

    
    #---------------------------
    # UPPER VERTEBRA, vertices.
    # Upper plane vertices(upv)
    #---------------------------    
    uv_upv = go.Scatter3d( x=x_uv[4:8],
                           y=y_uv[4:8],
                           z=z_uv[4:8],
                           mode='markers',
                           name="Upper Vertebra (UPV)",
                           marker=dict( size=8,
                                        color=['red', 'green', 'blue', 'orange'] ) 
                         )

    #---------------------------
    # UPPER VERTEBRA, 3D Mesh.
    # lower plane.
    # Sequence to form a plane:
    #   [0, 1, 2], [0, 2, 3]
    #---------------------------        
    i, j, k, l = 4, 5, 6, 7
    uv_up = go.Mesh3d( x=x_uv,
                       y=y_uv,
                       z=z_uv,
                       i=[2, 3],
                       j=[3, 7],
                       k=[6, 6],
                       opacity=0.5,
                       color='lightblue' )    
    
#     # Create the figure and add both scatter and plane traces
#     fig = go.Figure(data=[scatter, plane])   

    #---------------------------
    # LOWER VERTEBRA, vertices.
    # Bottom plane vertices(bpv)
    #---------------------------    
    lv_bpv = go.Scatter3d( x=x_lv[0:4],
                           y=y_lv[0:4],
                           z=z_lv[0:4],
                           mode='markers',
                           name="Lower Vertebra (BPV)",                          
                           marker=dict( size=8,
                                        color=['red', 'green', 'blue', 'orange'] ) 
                         )

    #---------------------------
    # LOWER VERTEBRA, 3D Mesh.
    # Bottom plane.
    # Sequence to form a plane:
    #   [0, 1, 2], [0, 2, 3]
    #---------------------------        
    i, j, k, l = 0, 1, 2, 3
    lv_bp = go.Mesh3d( x=x_lv,
                       y=y_lv,
                       z=z_lv,
                       i=[0, 1],
                       j=[1, 5],
                       k=[4, 4],
                       opacity=0.5,
                       color='lightblue' )

    
    #---------------------------
    # LOWER VERTEBRA, vertices.
    # Upper plane vertices(upv)
    #---------------------------    
    lv_upv = go.Scatter3d( x=x_lv[4:8],
                           y=y_lv[4:8],
                           z=z_lv[4:8],
                           mode='markers',
                           name="Lower Vertebra (UPV)",                          
                           marker=dict( size=8,
                                        color=['red', 'green', 'blue', 'orange'] ) 
                         )

    #---------------------------
    # LOWER VERTEBRA, 3D Mesh.
    # Upper plane.
    # Sequence to form a plane:
    #   [0, 1, 2], [0, 2, 3]
    #---------------------------        
    i, j, k, l = 4, 5, 6, 7
    lv_up = go.Mesh3d( x=x_lv,
                       y=y_lv,
                       z=z_lv,
                       i=[2, 3],
                       j=[3, 7],
                       k=[6, 6],
                       opacity=0.5,
                       color='lightblue' )    
 


    output.add_trace(uv_bpv, row=1, col=1)
    output.add_trace(uv_bp,  row=1, col=1)

    output.add_trace(uv_upv, row=1, col=1)
    output.add_trace(uv_up,  row=1, col=1)    

    output.add_trace(lv_bpv, row=1, col=2)
    output.add_trace(lv_bp,  row=1, col=2)

    output.add_trace(lv_upv, row=1, col=2)
    output.add_trace(lv_up,  row=1, col=2)        
    

    output.update_layout( scene1=dict( xaxis=dict(showticklabels=False),
                                      yaxis=dict(showticklabels=False),
                                      zaxis=dict(showticklabels=False) ),
                         scene2=dict( xaxis=dict(showticklabels=False),
                                      yaxis=dict(showticklabels=False),
                                      zaxis=dict(showticklabels=False) )
                        )
        
    output.show()

