from bpy.types import Operator
from . import world_logic
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver_on_error


class MIBLEND_OT_fix_world(Operator):
    bl_idname = "miblend.fix_world"
    bl_label = "Fix World"
    bl_description = "Fixes the World's Problems After Import"
    bl_options = {'REGISTER', 'UNDO'}

    @trigger_absolute_solver_on_error("Fix World")
    def execute(self, context):
        world_logic.FixWorld().fix_world()
        return {'FINISHED'}
