import bpy

use_node = properties.get("Use Node")
amount = properties.get("Amount")
segments = properties.get("Segments")

for selected_object in bpy.context.selected_objects:
    if use_node:
        if not selected_object.material_slots:
            continue

        for material in selected_object.data.materials:
            if material is None or not material.use_nodes:
                continue
    else:
        if selected_object.modifiers.get("Bevel") == None: 
            bevel_modifier = selected_object.modifiers.new('Bevel', type='BEVEL')
        else:
            bevel_modifier = selected_object.modifiers.get("Bevel")
        
        bevel_modifier.width = amount
        bevel_modifier.segments = segments