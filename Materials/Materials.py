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
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):

            if "water_still" in material.name.lower():
                append_materials("Upgraded Water Still", selected_object, i)
                
            if "water_flow" in material.name.lower():
                append_materials("Upgraded Water Flow", selected_object, i)

            if "sculk" in material.name.lower():
                append_materials("Upgraded Sculk", selected_object, i)
            
            if "glow_lichen" in material.name.lower():
                append_materials("Upgraded Glow Lichen", selected_object, i)

            if "stone" in material.name.lower():
                append_materials("Upgraded Stone", selected_object, i)

            if "sand" in material.name.lower():
                append_materials("Upgraded Sand", selected_object, i)

            if "bricks" in material.name.lower():
                append_materials("Upgraded Bricks", selected_object, i)

            if "iron_block" in material.name.lower():
                append_materials("Upgraded Iron Block", selected_object, i)

            if "gold_block" in material.name.lower():
                append_materials("Upgraded Gold Block", selected_object, i)

            if "diamond_ore" in material.name.lower():
                append_materials("Upgraded Diamond Ore", selected_object, i)

            if "lantern" in material.name.lower():
                append_materials("Upgraded Lantern", selected_object, i)

            if "soul_lantern" in material.name.lower():
                append_materials("Upgraded Soul Lantern", selected_object, i)

            if "obsidian" in material.name.lower():
                append_materials("Upgraded Obsidian", selected_object, i)

#Fix materials
def fix_world():
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