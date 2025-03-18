import bpy
from ..MIB_API import * 
from ..Resource_Packs import update_default_pack
from bpy.types import Operator
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, PointerProperty)

class FixCompatibility(Operator):
    bl_idname = "as_solutions.fix_compatibility"
    bl_label = "Fix Compatibility"
    bl_options = {'REGISTER', 'UNDO'}

    description: StringProperty(
        name="Description",
        default=""
    )

    def execute(self, context):
        if bpy.context.scene.get("resource_packs"):
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()

        with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
            new_node_groups_list = [node_group for node_group in data_from.node_groups]
            old_node_groups_list = bpy.data.node_groups
            has_old_node_groups = any(node_group for node_group in data_from.node_groups if node_group in old_node_groups_list)

            if not has_old_node_groups:
                return
            
            for node_group in new_node_groups_list:
                if node_group in old_node_groups_list:
                    old_node_groups_list.remove(node_group)
                    data_to.node_groups = [node_group]
                    
        return {'FINISHED'}