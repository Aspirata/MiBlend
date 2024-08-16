if "Cracks Overlay" not in bpy.data.node_groups:
    try:
        with bpy.data.libraries.load(os.path.dirname(os.path.abspath(__file__)), link=False) as (data_from, data_to):
            data_to.node_groups = ["Cracks Overlay"]
    except:
        #Absolute_Solver("004", "Materials", traceback.format_exc())
        dprint("Placeholder | Cracks.py")

for selected_object in bpy.context.selected_objects:
        slot = 0
        if selected_object.material_slots:
            for material in selected_object.data.materials:
                slot += 1
                if material is not None and material.use_nodes:
                    PBSDF = None
                    co_node = None

                    for node in material.node_tree.nodes:

                        if node.type == "BSDF_PRINCIPLED":
                            PBSDF = node
                        
                        if node.type == "GROUP":
                            if "Cracks Overlay" == node.node_tree.name:
                                co_node = node

                    if co_node is None:    
                        co_node = material.node_tree.nodes.new(type='ShaderNodeGroup')
                        co_node.node_tree = bpy.data.node_groups["Cracks Overlay"]
                        co_node.location = (PBSDF.location.x - 170, PBSDF.location.y)

                    if GetConnectedSocketTo("Base Color", PBSDF).node != co_node:
                        material.node_tree.links.new(GetConnectedSocketTo("Base Color", PBSDF), co_node.inputs["Color"])
                            
                    material.node_tree.links.new(co_node.outputs[0], PBSDF.inputs["Base Color"])
                else:
                    Absolute_Solver("m002", slot)
        else:
            Absolute_Solver("m003", selected_object)