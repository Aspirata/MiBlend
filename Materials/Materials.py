import bpy
import os
#Replace Materials

script_directory = os.path.dirname(os.path.realpath(__file__))
blend_file_path = os.path.join(script_directory, "Materials.blend")
print(blend_file_path)

def upgrade_materials():
    selected_object = bpy.context.active_object
    #Andesite
    for i, material in enumerate(selected_object.data.materials):
        if material == bpy.data.materials.get("water_still"):
            
            if "Upgraded water still" not in bpy.data.materials:
                with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
                    data_to.materials = [material_name]
            appended_material = bpy.data.materials[material_name]
            
            selected_object.data.materials[i] = bpy.data.materials.get("Upgraded water still")
                
        if material == bpy.data.materials.get("water_flow"):
            selected_object.data.materials[i] = bpy.data.materials.get("Upgraded water flow")
    #

    #Water
    for i, material in enumerate(selected_object.data.materials):
        if material == bpy.data.materials.get("water_still"):
            selected_object.data.materials[i] = bpy.data.materials.get("Upgraded water still")
                
        if material == bpy.data.materials.get("water_flow"):
            selected_object.data.materials[i] = bpy.data.materials.get("Upgraded water flow")
    #
    

    
#

#Fix materials
def fix_world():
    selected_object = bpy.context.active_object
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):
            material.blend_method = 'HASHED'
            matching_materials = []
            
            for material in bpy.data.materials:
                if "water".lower() in material.name.lower():
                    matching_materials.append(material)
                for material in matching_materials:
                    material.blend_method = 'BLEND'
                
            if material.node_tree.nodes.get("Image Texture.001"):
                material.node_tree.nodes.remove(material.node_tree.nodes["Image Texture.001"])
                
            image_texture_node = material.node_tree.nodes.get("Image Texture")
            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                
            if bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[21])
                if material == bpy.data.materials.get("lantern") or material == bpy.data.materials.get("glow_lichen"):
                    material.node_tree.links.new(image_texture_node.outputs["Color"], principled_bsdf_node.inputs[19])
            else:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])
                if material == bpy.data.materials.get("lantern") or material == bpy.data.materials.get("glow_lichen"):
                    material.node_tree.links.new(image_texture_node.outputs["Color"], principled_bsdf_node.inputs[27])

            material.node_tree.nodes["Image Texture"].interpolation = 'Closest'
    selected_object.data.update()

def fix_materials():
    selected_object = bpy.context.active_object
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):
            material.blend_method = 'HASHED'
                
            image_texture_node = material.node_tree.nodes.get("Image Texture")
            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                
            if bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[21])
            else:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])

            material.node_tree.nodes["Image Texture"].interpolation = 'Closest'
    selected_object.data.update()

#