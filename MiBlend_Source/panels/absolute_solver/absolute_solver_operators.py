import platform
import shutil
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..assets.assets_logic import update_assets
from ..resource_packs.resource_packs_logic import update_default_pack
from ...mib_utils import dprint
from .absolute_solver_logic import schedule_reverse_all_changes
from ...resources.data import main_directory_path


def _close_absolute_solver_popup(context):
    window = getattr(context, "window", None)
    if window is None or window.screen is None:
        return

    window.screen = window.screen

class MIBLEND_OT_absolute_solver(Operator):
    bl_label = "Absolute Solver"
    bl_idname = "miblend.absolute_solver"

    call_data: StringProperty()

    @staticmethod
    def _add_solution_button(layout, solution_operator, description, text=None, depress=False):
        if text is None:
            try:
                text = MIBLEND_OT_absolute_solver_run_solution._get_operator(solution_operator).get_rna_type().name
            except (AttributeError, ValueError):
                text = solution_operator

        solution = layout.operator(
            "miblend.absolute_solver_run_solution", text=text,
            **({"depress": True} if depress else {})
        )
        solution.solution_operator = solution_operator
        solution.description = description

    def invoke(self, context, event):
        self.errors = []
        for entry in self.call_data.split("|||"):
            parts = entry.split(":::")
            if len(parts) == 5:
                self.errors.append({
                    "Code": parts[0],
                    "Name": parts[1],
                    "Description": parts[2],
                    "Solutions": parts[3],
                    "Tech_Things": parts[4]
                })

        width = 600
        for error in self.errors:
            error_code = error["Code"]
            if error_code == "w04":
                width = 800
            elif error_code == "e10":
                width = 700

        return context.window_manager.invoke_popup(self, width=width)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Absolute Solver", icon='ERROR')
        layout.separator()

        for error in self.errors:
            box = layout.box()
            if "e" in error["Code"]:
                box.label(text="Error !", icon='ERROR')
            elif "w" in error["Code"]:
                box.label(text="Warning !", icon='WARNING_LARGE')

            sbox = box.box()
            row = sbox.row()
            row.label(text=f"Code: {error['Code']}")
        
            row = sbox.row()
            row.label(text=f"Name: {error['Name']}")

            row = sbox.row()
            row.label(text=f"Description: {error['Description']}")

            if error["Solutions"]:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Solutions:")
                for solution_operator in filter(None, error["Solutions"].split("; ")):
                    row = sbox.row()
                    self._add_solution_button(row, solution_operator, error["Description"])

            if error["Tech_Things"]:
                sbox = box.box()
                
                if platform.system() == "Windows":
                    row = sbox.row()
                    row.operator("miblend.absolute_solver_open_console")

                row = sbox.row()
                copy_to_clipboard = row.operator("miblend.absolute_solver_copy_to_clipboard")
                copy_to_clipboard.text = error["Tech_Things"]

                print(f"\033[33mAbsolute Solver Report: \033[31m\n{error['Tech_Things']}\033[0m")
            
            row = layout.row()
            if error["Solutions"]:
                self._add_solution_button(row, error["Solutions"].split("; ")[0], error["Description"], text="Auto Solve", depress=True)
            ignore_operator = row.operator("miblend.absolute_solver_ignore")
            ignore_operator.error_code = error["Code"]

    def execute(self, context):
        return {'FINISHED'}


class MIBLEND_OT_absolute_solver_open_console(Operator):
    bl_idname = "miblend.absolute_solver_open_console"
    bl_label = "Open Console"
    bl_description = "Toggles Blender System Console"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            bpy.ops.wm.console_toggle()
        except RuntimeError:
            return {'CANCELLED'}
        return {'FINISHED'}


class MIBLEND_OT_absolute_solver_copy_to_clipboard(Operator):
    bl_idname = "miblend.absolute_solver_copy_to_clipboard"
    bl_label = "Copy Tech Things to Clipboard"
    bl_description = "Copies the Text to your Clipboard"
    bl_options = {'REGISTER', 'UNDO'}
    
    text: StringProperty()

    def execute(self, context):
        try:
            bpy.context.window_manager.clipboard = self.text
        except RuntimeError:
            return {'CANCELLED'}
        return {'FINISHED'}


class MIBLEND_OT_absolute_solver_ignore(Operator):
    bl_idname = "miblend.absolute_solver_ignore"
    bl_label = "Ignore"

    error_code: StringProperty()

    def execute(self, context):
        as_props = context.scene.miblend_properties.absolute_solver_properties
        ignored_list = as_props.ignored_codes.split()

        if self.error_code not in ignored_list:
            ignored_list.append(self.error_code)
            as_props.ignored_codes = " ".join(ignored_list)
            self.report({'INFO'}, f"{self.error_code} is being ignored now.")

        _close_absolute_solver_popup(context)
        return {'FINISHED'}


class MIBLEND_OT_absolute_solver_run_solution(Operator):
    bl_idname = "miblend.absolute_solver_run_solution"
    bl_label = "Apply Solution"
    bl_description = "Runs the selected Absolute Solver solution"
    bl_options = {'INTERNAL'}

    solution_operator: StringProperty()
    description: StringProperty()

    @staticmethod
    def _get_operator(operator_id):
        category, name = operator_id.split(".", 1)
        return getattr(getattr(bpy.ops, category), name)

    def execute(self, context):
        try:
            solution_operator = self._get_operator(self.solution_operator)
            properties = solution_operator.get_rna_type().properties
            kwargs = {"description": self.description} if "description" in properties else {}
            result = solution_operator('EXEC_DEFAULT', **kwargs)
        except (AttributeError, RuntimeError, ValueError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}

        if 'FINISHED' in result:
            _close_absolute_solver_popup(context)

        return result


class MIBLEND_OT_absolute_solver_reverse_all_changes(Operator):
    bl_idname = "miblend.absolute_solver_reverse_all_changes"
    bl_label = "Reverse All Changes"
    bl_description = "Reverses all changes made by the failed MiBlend operation"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if not schedule_reverse_all_changes(context):
            self.report({'ERROR'}, "Could not schedule rollback. Use Edit > Undo")
            return {'CANCELLED'}

        return {'FINISHED'}


class MIBLEND_OT_migrate_blend_file(Operator):
    bl_idname = "miblend.absolute_solver_migrate_blend_file"
    bl_label = "Migrate Blend File"
    bl_description = "Rebuilds MiBlend scene data and saves the migrated blend file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if "resource_packs" in bpy.context.scene:
            bpy.context.scene["resource_packs"] = {}
            update_default_pack()
        
        update_assets()

        if bpy.data.filepath == "":
            bpy.ops.wm.save_homefile()
            self.report({'INFO'}, "Default file was migrated and overwritten")
        else:
            bpy.ops.wm.save_mainfile()
            self.report({'INFO'}, "Current file was migrated and saved")
        return {'FINISHED'}


class MIBLEND_OT_delete_miblend_addon(Operator):
    bl_idname = "miblend.absolute_solver_delete_miblend_addon"
    bl_label = "Delete MiBlend Legacy Addon"

    def execute(self, context):
        miblend_addon_folder = main_directory_path.parent.parent.parent / "scripts" / "addons" / "MiBlend_Source"

        if not miblend_addon_folder.is_dir():
            dprint(miblend_addon_folder)
            self.report({'WARNING'}, "MiBlend Legacy Addon Folder not Found")
            return {'CANCELLED'}

        shutil.rmtree(miblend_addon_folder)
        self.report({'INFO'}, "MiBlend Legacy Addon Folder was Removed")
        return {'FINISHED'}
