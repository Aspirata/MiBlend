from bpy.types import Operator
from . import world_logic


class MIBLEND_OT_fix_world(Operator):
    bl_idname = "miblend.fix_world"
    bl_label = "Fix World"
    bl_description = "Fixes the World's Problems After Import"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        world_logic.FixWorld().fix_world()
        return {'FINISHED'}