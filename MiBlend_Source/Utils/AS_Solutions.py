import bpy
from ..MIB_API import * 
from ..Resource_Packs import update_default_pack
from bpy.types import Operator
from bpy.props import StringProperty

class FixCompatibility(Operator):
    bl_idname = "as_solutions.fix_compatibility"
    bl_label = "Fix Compatibility"
    bl_options = {'REGISTER', 'UNDO'}

    description: StringProperty(
        name="Description",
        default=""
    )

    def execute(self, context):
        # Очистка resource_packs
        if "resource_packs" in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()

        # Проверка наличия файла
        if not nodes_file:
            self.report({'ERROR'}, "nodes_file is not defined")
            return {'CANCELLED'}

        with bpy.data.libraries.load(nodes_file, link=False) as (data_from, data_to):
            new_node_groups = {name: None for name in data_from.node_groups}  # Используем словарь для хранения имен
            old_node_groups = {node_group.name: node_group for node_group in bpy.data.node_groups}
            
            # Сохранение значений входов старых групп
            input_values = {}
            for name, old_group in old_node_groups.items():
                if name in new_node_groups:
                    input_values[name] = {socket.name: socket.default_value for socket in old_group.inputs if hasattr(socket, 'default_value')}
            
            # Заменяем "Better Animate Texture" на "Procedurally Animated Better Emission"
            if "Better Animate Texture" in old_node_groups:
                old_node_groups["Procedurally Animated Better Emission"] = old_node_groups.pop("Better Animate Texture")
            
            # Определяем, есть ли старые группы
            common_groups = set(new_node_groups.keys()) & set(old_node_groups.keys())
            if not common_groups:
                self.report({'INFO'}, "No outdated node groups found")
                return {'FINISHED'}
            
            # Удаляем старые группы
            for name in common_groups:
                bpy.data.node_groups.remove(old_node_groups[name])
            
            # Импортируем новые группы
            data_to.node_groups = list(new_node_groups.keys())
            
            # Восстановление значений входов в новых группах
            for name, new_group in bpy.data.node_groups.items():
                if name in input_values:
                    for socket in new_group.inputs:
                        if socket.name in input_values[name] and hasattr(socket, 'default_value'):
                            socket.default_value = input_values[name][socket.name]
        
        self.report({'INFO'}, "Node groups updated successfully with input values restored and replacements applied")
        return {'FINISHED'}
