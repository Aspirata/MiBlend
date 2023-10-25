import bpy
#selected_object = bpy.context.active_object
#Replace Materials

def upgrade_materials():
    selected_object = bpy.context.active_object
    #Andesite
    for i, material in enumerate(selected_object.data.materials):
        if material == bpy.data.materials.get("water_still"):
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
    for i, material in enumerate(selected_object.data.materials):
        for material in selected_object.data.materials:
            material.blend_method = 'HASHED'
            if material == bpy.data.materials.get("water_still") or material == bpy.data.materials.get("water_flow"):
                selected_object.data.materials["water_still"].blend_method = 'BLEND'
                selected_object.data.materials["water_flow"].blend_method = 'BLEND'
            
            if material.node_tree.nodes.get("Image Texture.001"):
                material.node_tree.nodes.remove(material.node_tree.nodes["Image Texture.001"])
            
            image_texture_node = material.node_tree.nodes.get("Image Texture")
            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
            
            if bpy.app.version < (4, 0, 0):
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[21])
            else:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], principled_bsdf_node.inputs[4])

            material.node_tree.nodes["Image Texture"].interpolation = 'Closest'
    selected_object.data.update()

def fix_materials():
    selected_object = bpy.context.active_object
    for i, material in enumerate(selected_object.data.materials):
        for material in selected_object.data.materials:
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
#selected_object.data.update()
#upgrade_materials()