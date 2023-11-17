import bpy
import os

def Camera_Culling(obj):

    script_directory = os.path.dirname(os.path.realpath(__file__))
    blend_file_path = os.path.join(script_directory, "Camera Culling.blend")
    node_tree_name = "Camera Culling"

    if node_tree_name not in bpy.data.node_groups:
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.node_groups = [node_tree_name]
    
        if node_tree_name in bpy.data.node_groups:
            appended_node_tree = bpy.data.node_groups[node_tree_name]

    geonodes_modifier = obj.modifiers.new('Camera Culling', type='NODES')
    geonodes_modifier.node_group = bpy.data.node_groups.get("Camera Culling")
    geonodes_modifier["Input_3"] = bpy.context.scene.camera

def Optimize():
    selected_objects = bpy.context.selected_objects
    scene = bpy.context.scene
    if scene.mcblend.use_camera_culling == True:
        for obj in selected_objects:
            Camera_Culling(obj)
    