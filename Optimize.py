import bpy

# Получить выбранный объект
selected_object = bpy.context.active_object
geonodes_modifier = selected_object.modifiers.new('GEONODES', type='NODES')
geonodes_modifier.node_group = bpy.data.node_groups.get("Camera Culling")
geonodes_modifier["Input_3"] = bpy.context.scene.camera