import bpy
import random

#bpy.context.scene.render.resolution_percentage = 50
bpy.context.scene.render.resolution_percentage = 200



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
