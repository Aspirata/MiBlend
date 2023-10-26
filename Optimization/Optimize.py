import bpy
import os

file_path = "C:/Users/const/OneDrive/Документы/GitHub/Mcblend/Optimization/camera_culling.blend"
node_tree_name = "Camera Culling"  # Замените на имя вашего узла
scene = bpy.context.scene
# Append File
if node_tree_name not in bpy.data.node_groups:
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.node_groups = [node_tree_name]
    
    if node_tree_name in bpy.data.node_groups:
        appended_node_tree = bpy.data.node_groups[node_tree_name]
        print(f"Node Tree '{node_tree_name}' успешно аппенднут.")
    else:
        print(f"Не удалось аппенднуть Node Tree '{node_tree_name}'.")
#
script_directory = os.path.dirname(os.path.realpath(__file__))
print(script_directory)

def Optimize():
    selected_object = bpy.context.active_object
    if scene.mcblend.use_optimization == True:
        geonodes_modifier = selected_object.modifiers.new('Camera Culling', type='NODES')
        geonodes_modifier.node_group = bpy.data.node_groups.get("Camera Culling")
        geonodes_modifier["Input_2"] = 0.88
        geonodes_modifier["Input_3"] = bpy.context.scene.camera
        geonodes_modifier.show_render = False
Optimize()