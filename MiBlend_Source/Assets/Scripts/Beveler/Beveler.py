import bpy

use_node = properties.get("Use Node")
amount = properties.get("Amount")
segments = properties.get("Segments")

for selected_object in bpy.context.selected_objects:
    if use_node:
        bevel_node = None
        PBSDF = None
        if not selected_object.material_slots:
            continue

        for material in selected_object.data.materials:
            if material is None or not material.use_nodes:
                continue

            for node in material.node_tree.nodes:
                if node.type == "BEVEL":
                    bevel_node = node
                elif node.type == "BSDF_PRINCIPLED":
                    PBSDF = node
            
            if bevel_node == None:
                bevel_node = material.node_tree.nodes.new(type='ShaderNodeBevel')
                bevel_node.location = (PBSDF.location.x - 180, PBSDF.location.y - 132)

            bevel_node.samples = clamp(2, segments, 128)
            bevel_node.inputs[0].default_value = clamp(0, amount, 1000.0)

            try:
                if GetConnectedSocketTo("Normal", PBSDF).node != bevel_node:
                    material.node_tree.links.new(GetConnectedSocketTo("Normal", PBSDF), bevel_node.inputs["Normal"])
            except:
                pass
            
            material.node_tree.links.new(bevel_node.outputs[0], PBSDF.inputs["Normal"])

    else:
        if selected_object.modifiers.get("Bevel") == None: 
            bevel_modifier = selected_object.modifiers.new('Bevel', type='BEVEL')
        else:
            bevel_modifier = selected_object.modifiers.get("Bevel")
        
        bevel_modifier.width = amount
        bevel_modifier.segments = segments