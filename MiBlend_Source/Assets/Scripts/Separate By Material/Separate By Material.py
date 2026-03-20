import bpy


obj = bpy.context.active_object
material = bpy.data.materials.get(properties.get("Material Name"))
separate_mesh_by_material(obj, material)