import bpy

if bpy.app.version < (4, 1, 0):
    for selected_object in bpy.data.objects:
        if selected_object.type == 'MESH':    
            for modifier in selected_object.modifiers:
                if modifier.type == 'NODES' and "Smooth" in modifier.node_group.name:
                    selected_object.data.use_auto_smooth = True
                    selected_object.data.auto_smooth_angle = modifier["Input_1"]
                    break