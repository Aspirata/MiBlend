from bpy.types import Operator
from . import procedural_pbr_logic
from ..absolute_solver.absolute_solver_logic import trigger_absolute_solver_on_error


class MIBLEND_OT_apply_procedural_pbr(Operator):
    bl_idname = "miblend.apply_procedural_pbr"
    bl_label = "Apply Procedural PBR"
    bl_description = "Applies Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    @trigger_absolute_solver_on_error("Procedural PBR")
    def execute(self, context):
        procedural_pbr_logic.ProceduralPBR().apply_procedural_pbr()
        return {'FINISHED'}
