import bpy

# Fix Script 
for selected_object in bpy.context.selected_objects:
    AutoSmoothed = False
    if bpy.app.version < (4, 1, 0):
        if selected_object.type == 'MESH':
            for modifier in selected_object.modifiers:
                if modifier.type == 'NODES' and modifier.node_group == bpy.data.node_groups.get("Auto Smooth"):
                    AutoSmoothed = True
                    SmoothAngle = modifier["Socket_1"]
                    break

            if AutoSmoothed == True:
                selected_object.data.use_auto_smooth = True
                selected_object.data.auto_smooth_angle = SmoothAngle
            print("Mesh Passed")
        print("Version passed")