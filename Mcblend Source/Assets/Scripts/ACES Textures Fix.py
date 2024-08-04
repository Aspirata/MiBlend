import bpy
for selected_object in bpy.context.selected_objects:
    if selected_object.material_slots:
        for material in selected_object.data.materials:
            if material is not None and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        node.image.colorspace_settings.name = "Output - sRGB"