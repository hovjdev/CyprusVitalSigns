from bpy import context, data, ops
from math import cos, pi, sin, tan
from random import TWOPI, randint, uniform
import numpy as np
import bpy
from mathutils import Vector

DATA_FILE = "/home/hovj/Desktop/Cyprus-Vital-Signs/Blender/scenes/d5/rainfall_waveform.npy"
X = np.load(DATA_FILE)



def create_curve(X, bevel_depth=0.05, material_name="Material_neon_inside"):

    # create the Curve Datablock
    curveData = bpy.data.curves.new('myCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 2

    # map coords to spline
    polyline = curveData.splines.new('POLY')
    polyline.points.add(len(X)-1)
    for i, coord in enumerate(X):
        x = i/500.
        y= 0
        z = X[i]*(1+i/500)*(1+i/500)
        polyline.points[i].co = (x, y, z, 1)


    # create Object
    curveOB = bpy.data.objects.new('myCurve', curveData)
    curveData.bevel_depth = 0.001

    # create Object
    curveOB = bpy.data.objects.new('myCurve', curveData)
    curveData.bevel_depth = bevel_depth

    scn = bpy.context.scene
    bpy.context.collection.objects.link(curveOB)

    material = bpy.data.materials[material_name]
    curveOB.active_material = material

    return curveOB


curve = create_curve(X, bevel_depth=0.05, material_name="Material_neon_inside")
curve.scale[2] = 0.02
curve.location[0] = -12
curve.location[1] = 5
curve.rotation_euler[2] = -0.1

curve = create_curve(X, bevel_depth=0.1, material_name="Material_neon_outside")
curve.scale[2] = 0.02
curve.location[0] = -12
curve.location[1] = 5
curve.rotation_euler[2] = -0.1
