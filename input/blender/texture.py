import os
import sys
import random
import bpy


DIRNAME = os.path.dirname(os.path.abspath(__file__))
PATH_LOCAL_SETTINGS_SETTINGS=os.path.join(DIRNAME, '..', '..')
#raise Exception(PATH_LOCAL_SETTINGS_SETTINGS)
sys.path.append(PATH_LOCAL_SETTINGS_SETTINGS)
from local_settings import BLENDER_RESOLUTION_PCT

print(f"BLENDER_RESOLUTION_PCT: {BLENDER_RESOLUTION_PCT}")
bpy.context.scene.render.resolution_percentage = 25
bpy.context.scene.render.resolution_percentage = BLENDER_RESOLUTION_PCT



obj = bpy.data.objects["Cube"]
material_slots = obj.material_slots
materials=[]
for m in material_slots:
    material = m.material.name
    print("slot", m, "material", material)
    if "Pattern" in material or "Texture" in material:
        materials.append(material)

print(f"Found {len(materials)} materials")
material = random.choice(materials)

bpy.data.objects['Cube.001'].material_slots[0].material = bpy.data.materials[material]
