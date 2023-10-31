import bpy
import os
from .Data import *
#Replace Materials

script_directory = os.path.dirname(os.path.realpath(__file__))
blend_file_path = os.path.join(script_directory, "Materials.blend")

def append_materials(upgraded_material_name, selected_object, i):
    if upgraded_material_name not in bpy.data.materials:
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.materials = [upgraded_material_name]
        appended_material = bpy.data.materials.get(upgraded_material_name)
        selected_object.data.materials[i] = appended_material
    else:
        selected_object.data.materials[i] = bpy.data.materials[upgraded_material_name]

def upgrade_materials():
    selected_object = bpy.context.active_object
    for i, material in enumerate(selected_object.data.materials):
        if material.name == "water_still":
            append_materials("Upgraded water still", selected_object, i)
            
        if material.name == "water_flow":
            append_materials("Upgraded water flow", selected_object, i)


#Fix materials
def fix_world():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            if material.name.lower() in Blend_Materials:
                material.blend_method = 'BLEND'
            else:
                material.blend_method = 'HASHED'
            
            if material.node_tree.nodes.get("Image Texture.001"):
                material.node_tree.nodes.remove(material.node_tree.nodes["Image Texture.001"])
                
            image_texture_node = material.node_tree.nodes.get("Image Texture")
            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                
            if bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[21])
                if material.name == Emissive_Materials:
                    material.node_tree.links.new(image_texture_node.outputs["Color"], principled_bsdf_node.inputs[19])
            else:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])
                if material.name == Emissive_Materials:
                    material.node_tree.links.new(image_texture_node.outputs["Color"], principled_bsdf_node.inputs[27])

            image_texture_node.interpolation = 'Closest'

    selected_object.data.update()

def fix_materials():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            material.blend_method = 'HASHED'
                
            image_texture_node = material.node_tree.nodes.get("Image Texture")
            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                
            if bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[21])
            else:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])

            image_texture_node.interpolation = 'Closest'
    selected_object.data.update()

#