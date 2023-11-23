import bpy
import os
from ..Data import *
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
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):
            for original_material, upgraded_material in Materials.items():
                if original_material in material.name.lower():
                    append_materials(upgraded_material, selected_object, i)

#Fix materials
def fix_world():
    image_texture_node = None
    principled_bsdf_node = None
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            
            for keyword in Backface_Culling_Materials:
                if keyword in material.name.lower():
                    material.use_backface_culling = True
                
            for keyword in Alpha_Blend_Materials:
                if keyword in material.name.lower():
                    material.blend_method = 'BLEND'
                else:
                    material.blend_method = 'HASHED'
            
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = material.node_tree.nodes[node.name]
                    material.node_tree.nodes[node.name].interpolation = "Closest" 
            
            if material.node_tree.nodes.get("Principled BSDF") != None:
                principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")

            if (image_texture_node and principled_bsdf_node) != None:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])
                if material.name == Emissive_Materials:
                    material.node_tree.links.new(image_texture_node.outputs["Color"], principled_bsdf_node.inputs[27])

            if material.node_tree.nodes.get("Image Texture.001"):
                material.node_tree.nodes.remove(material.node_tree.nodes["Image Texture.001"])

                

    selected_object.data.update()

def fix_materials():
    image_texture_node = None
    principled_bsdf_node = None
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            material.blend_method = 'HASHED'

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = material.node_tree.nodes[node.name]
                    material.node_tree.nodes[node.name].interpolation = "Closest" 
            
            if material.node_tree.nodes.get("Principled BSDF") != None:
                principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")

            if (image_texture_node and principled_bsdf_node) != None:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])
                
        selected_object.data.update()

#