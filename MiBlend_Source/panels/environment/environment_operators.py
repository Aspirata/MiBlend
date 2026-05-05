import bpy
from . import environment_logic
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty


class MIBLEND_OT_recreate_environment(Operator):
    bl_label = "Recreate Environment"
    bl_idname = "miblend.recreate_env"
    bl_description = "Recreates the Environment with Options for Sky, Fog, and Clouds"
    bl_options = {'REGISTER', 'UNDO'}
    
    reset_settings: BoolProperty(
        name="Reset Settings",
        description="Resets the sky settings",
        default=False
    )

    create_sky: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Sky', 'Create Sky', 'Reuses Already Imported Sky Material'), 
            ('Recreate Sky', 'Recreate Sky', 'Reappends Sky Material')],
        name="create_sky",
        description="Options for reusing imported sky assets or reimporting them",
        default='None'
    )

    create_fog: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Fog', 'Create Fog', 'Reuses Already Imported Fog Material'), 
            ('Recreate Fog', 'Recreate Fog', 'Reappends Fog Material')],
        name="create_fog",
        description="Options for reusing imported fog assets or reimporting them",
        default='None'
    )
    
    create_clouds: EnumProperty(
        items=[('None', 'None', ''),
            ('Create Clouds', 'Create Clouds', 'Reuses Already Imported Cloud Material'), 
            ('Recreate Clouds', 'Recreate Clouds', 'Reappends Cloud Material')],
        name="create_clouds",
        description="Options for reusing imported cloud assets or reimporting them",
        default='None'
    )

    def execute(self, context):
        environment_logic.recreate_env(self)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)
    
    def draw(self, context):
        layout = self.layout
        world = bpy.context.scene.world
            
        box = layout.box()
        row = box.row()

        if world is not None:
            for node in world.node_tree.nodes:
                if node.type == 'GROUP':
                    if "MiBlend Sky" in node.node_tree.name:
                        row.prop(self, "reset_settings")
                        row = box.row()

        row.prop(self, "create_sky", text='create_sky', expand=True)
        row = box.row()
        row.prop(self, "create_fog", text='create_fog', expand=True)
        row = box.row()
        row.prop(self, "create_clouds", text='create_clouds', expand=True)


class MIBLEND_OT_create_environment(Operator):
    bl_idname = "miblend.create_env"
    bl_label = "Create Environment"
    bl_description = "Creates a New Environment"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        environment_logic.create_env()
        return {'FINISHED'}