from bpy.types import Operator
from . import procedural_pbr_logic


class MIBLEND_OT_apply_procedural_pbr(Operator):
    bl_idname = "miblend.apply_procedural_pbr"
    bl_label = "Apply Procedural PBR"
    bl_description = "Applies Procedural PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        procedural_pbr_logic.ProceduralPBR().apply_procedural_pbr()
        return {'FINISHED'}