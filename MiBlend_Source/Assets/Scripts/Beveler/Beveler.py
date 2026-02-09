import bpy


def simple_scale_uv(scale_factor, all_uv_layers = False):
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH' or not obj.data.uv_layers:
            continue
        
        uv_layers = obj.data.uv_layers if all_uv_layers else [obj.data.uv_layers.active]
        
        for uv_layer in uv_layers:
            if not uv_layer:
                continue
                
            for poly in obj.data.polygons:
                center_x = center_y = 0
                count = len(poly.loop_indices)
                
                for loop_idx in poly.loop_indices:
                    center_x += uv_layer.data[loop_idx].uv[0]
                    center_y += uv_layer.data[loop_idx].uv[1]
                
                center_x /= count
                center_y /= count
                
                for loop_idx in poly.loop_indices:
                    uv = uv_layer.data[loop_idx].uv
                    uv[0] = center_x + (uv[0] - center_x) * scale_factor
                    uv[1] = center_y + (uv[1] - center_y) * scale_factor


fix_uv: bool = properties.get("Fix UV")
use_node: bool = properties.get("Use Node")
amount: float = properties.get("Amount/Radius")
segments: int = properties.get("Segments/Samples")

for selected_object in bpy.context.selected_objects:
    if selected_object.type != "MESH":
        continue
    
    bevel_modifier = next((mod for mod in selected_object.modifiers if mod.type == "BEVEL"), None)
    if use_node and selected_object.material_slots:
        for material in selected_object.data.materials:
            if not material or not material.use_nodes:
                continue

            pbsdf_node = find_node(material, "BSDF_PRINCIPLED")
            
            if not pbsdf_node:
                continue

            bevel_node = find_node(material, "BEVEL")
            if not bevel_node:
                bevel_node = material.node_tree.nodes.new(type='ShaderNodeBevel')
                bevel_node.location = (pbsdf_node.location.x - 180, pbsdf_node.location.y - 132)

            inject_node(material, bevel_node, pbsdf_node, "Normal")
            bevel_node.samples = clamp(2, segments, 128)
            bevel_node.inputs[0].default_value = clamp(0, amount, 1000.0)
        
        if bevel_modifier:
            selected_object.modifiers.remove(bevel_modifier)
    else:
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                if not material or not material.use_nodes:
                    continue

                bevel_node = find_node(material, "BEVEL")
                dissolve_node(material, bevel_node, "Normal")

        bevel_modifier = add_modifier(selected_object, "BEVEL", "Bevel")
        bevel_modifier.width = amount
        bevel_modifier.segments = segments
        simple_scale_uv(0.999)