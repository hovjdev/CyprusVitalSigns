import os
import sys
import random
import bpy
from bpy import context, data, ops
from math import cos, pi, sin, tan
from random import TWOPI, randint, uniform
import numpy as np

from mathutils import Vector


DIRNAME = os.path.dirname(bpy.data.filepath)
PATH_LOCAL_SETTINGS_SETTINGS=os.path.join(DIRNAME, '..', '..')
#raise Exception(PATH_LOCAL_SETTINGS_SETTINGS)
sys.path.append(PATH_LOCAL_SETTINGS_SETTINGS)
from local_settings import BLENDER_RESOLUTION_PCT

print(f"BLENDER_RESOLUTION_PCT: {BLENDER_RESOLUTION_PCT}")
bpy.context.scene.render.resolution_percentage = 25
bpy.context.scene.render.resolution_percentage = BLENDER_RESOLUTION_PCT


DATA_FILE = os.path.join(os.path.dirname(bpy.data.filepath), "files", "data.npy")
X=None

if os.path.exists(DATA_FILE):
    X = np.load(DATA_FILE)
    X=X[~np.isnan(X)]
    X=X[:50000]
else:
    print(f"Did not find file: {DATA_FILE}")
    print(f"Will not create neon curve representing the data")


def create_curve(X, bevel_depth=0.05,
        material_name="Material_neon_inside",
        x_min=0, x_max=1, z_min=0, z_max=1):

    # create the Curve Datablock
    curveData = bpy.data.curves.new('myCurve', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 2

    # map coords to spline
    polyline = curveData.splines.new('POLY')
    polyline.points.add(len(X)-1)
    for i, coord in enumerate(X):
        x = i/len(X)
        y= 0
        z = X[i]*(1+i/500)*(1+i/500)
        polyline.points[i].co = (x, y, z, 1)
        if x_min is None or x < x_min:  x_min=x
        if x_max is None or x > x_max:  x_max=x
        if z_min is None or z < z_min:  z_min=z
        if z_max is None or z > z_max:  z_max=z


    # create Object
    curveOB = bpy.data.objects.new('myCurve', curveData)
    curveData.bevel_depth = bevel_depth

    scn = bpy.context.scene
    bpy.context.collection.objects.link(curveOB)

    material = bpy.data.materials[material_name]
    curveOB.active_material = material
    
    curveOB.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')


    return curveOB, x_min, x_max, z_min, z_max

def create_neon_curve(X):

    x_min=None
    x_max=None
    z_min=None
    z_max=None

    curve, x_min, x_max, z_min, z_max = create_curve(X, bevel_depth=0.004,
            material_name="Material_neon_inside",
            x_min=x_min, x_max=x_max, z_min=z_min, z_max=z_max)

    width=20
    height=9
    depth=9

    rotation_0=-np.pi/2
    rotation_1=0
    rotation_2=0
    curve.scale[0] = width / (x_max-x_min)
    curve.scale[2] = height / (z_max-z_min)
    curve.location[0] = 0
    curve.location[1] = depth
    curve.location[2] = .1
    curve.rotation_euler[0] = rotation_0
    curve.rotation_euler[1] = rotation_1
    curve.rotation_euler[2] = rotation_2
    curve.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


    curve, x_min, x_max, z_min, z_max = create_curve(X, bevel_depth=0.01,
            material_name="Material_neon_outside",
            x_min=x_min, x_max=x_max, z_min=z_min, z_max=z_max)
            
    curve.scale[0] = width / (x_max-x_min)
    curve.scale[2] = height / (z_max-z_min)
    curve.location[0] = 0
    curve.location[1] = depth
    curve.location[2] = .1
    curve.rotation_euler[0] = rotation_0
    curve.rotation_euler[1] = rotation_1
    curve.rotation_euler[2] = rotation_2
    curve.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def show_object(name, hide=False):
    for o in bpy.context.scene.objects:
        if name in o.name:
            o.hide_render = hide
            o.hide_set(hide)
            return True
    return False

def set_rotation(name, rotation):
    for o in bpy.context.scene.objects:
        if name in o.name:
            o.rotation_euler[2] = rotation
            return True
    return False

            
def set_position(name, x, y):
    for o in bpy.context.scene.objects:
        if name in o.name:
            o.location[0] = x
            o.location[1] = y            
            return True
    return False

deco = ['aphrodite', 
        'tree', 
        'cyprus', 
        'skydancer', 
        'furniture',
        'tubes',
        'human']
for d in deco: 
    show_object(d, hide=True)


set_rotation('fig_1.001', 0)
set_position('fig_1.001', 0, 20)      
    
if X is not None:
    create_neon_curve(X) 
else:
    random.seed(1587)
    C = random.choice([1,2,3,4,5,6,7])
        
    if C==1:
        name='aphrodite'
        b=show_object(name)
        if b:
            set_rotation('fig_1.001', .15)
            set_position('fig_1.001', -10, 23)
    if C==2:
        name='tree'
        b=show_object(name)
        if b:        
            set_rotation('fig_1.001', -.15)
            set_position('fig_1.001', 10, 23)        
    if C==3:
        name='cyprus'
        b=show_object(name)
        if b:
            set_rotation('fig_1.001', 0)
            set_position('fig_1.001', 0, 20)        
    if C==4:
        name='skydancer'
        b=show_object(name)
        if b:        
            set_rotation('fig_1.001', .15)
            set_position('fig_1.001', -10, 23)            
    if C==5:
        name='furniture'
        b=show_object(name)
        if b:        
            set_rotation('fig_1.001', -.15)
            set_position('fig_1.001', 10, 23)        
    if C==6:
        name='tubes'
        b=show_object(name)
        if b:        
            set_rotation('fig_1.001', .15)
            set_position('fig_1.001', -10, 23)      
    if C==7:
        name='human'
        b=show_object(name)
        if b:        
            set_rotation('fig_1.001', -.15)
            set_position('fig_1.001', 10, 23)                       