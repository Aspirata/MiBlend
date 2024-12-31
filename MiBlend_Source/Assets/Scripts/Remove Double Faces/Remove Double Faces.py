import bpy

convert_to_quads = properties.get("Convert to Quads")

for selected_object in bpy.context.selected_objects:
    if selected_object and selected_object.type == 'MESH':
        bpy.ops.object.editmode_toggle()
        
        bpy.ops.mesh.select_all(action='SELECT')
        
        if convert_to_quads:
            bpy.ops.mesh.tris_convert_to_quads()
            
        bpy.ops.mesh.edge_split(type='VERT')
        bpy.ops.mesh.remove_doubles()

        bpy.ops.object.editmode_toggle()