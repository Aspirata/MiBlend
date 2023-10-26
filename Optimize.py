#import bpy
import os

# Получите путь к текущей директории вашего скрипта
script_directory = os.path.dirname(os.path.realpath(__file__))
print(script_directory)

#selected_object = bpy.context.active_object

#geonodes_modifier = selected_object.modifiers.new('Camera Culling', type='NODES')
#geonodes_modifier.node_group = bpy.data.node_groups.get("Camera Culling")
#geonodes_modifier["Input_2"] = 0.88
#geonodes_modifier["Input_3"] = bpy.context.scene.camera
#geonodes_modifier.show_render = False