import bpy, os, time, json, traceback
from ..Data import utils_directory
from ..Utils.Translator import translate

def Call_AS(code: str, tech_things: str = "", data: str = ""):
    Preferences = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences
    
    if not hasattr(Call_AS, 'call_queue'):
        Call_AS.call_queue = []
        Call_AS.last_call_time = 0
        Call_AS.is_processing = False
    
    current_time = time.time()
    
    Call_AS.call_queue.append((code, data))
    
    if (current_time - Call_AS.last_call_time >= 0.1) and not Call_AS.is_processing:
        Call_AS.is_processing = True

        call_data = {}
        try:
            with open(os.path.join(utils_directory, "absolute_solver_list.json"), "r") as file:
                data_json = json.load(file)
                critical_error_name = data_json.get("errors", {}).get("00", {}).get("Name", "Critical Error")
                critical_error_description = translate(data_json.get("errors", {}).get("00", {}).get("Description", "Unknown error occurred: {Data}"))

                for code, d in Call_AS.call_queue:
                    if code in call_data or code in bpy.context.scene.miblend_properties.absolute_solver_properties.ignored_codes.split():
                        continue
                    
                    type = code[0]
                    number = str(code[1:])
                    
                    if type == "w":
                        if not Preferences.show_warnings:
                            continue
                        name = data_json.get("warnings", {}).get(number, {}).get("Name")
                        description = data_json.get("warnings", {}).get(number, {}).get("Description")
                        solutions = data_json.get("warnings", {}).get(number, {}).get("Solutions", "")
                    elif type == "e":
                        name = data_json.get("errors", {}).get(number, {}).get("Name")
                        description = data_json.get("errors", {}).get(number, {}).get("Description")
                        solutions = data_json.get("errors", {}).get(number, {}).get("Solutions", "")
                    elif type == "n":
                        name = data_json.get("null", {}).get(number, {}).get("Name")
                        description = data_json.get("null", {}).get(number, {}).get("Description")
                        solutions = ""
                    
                    description = translate(description)
                    
                    if name and description:
                        call_data[code] = f"{code}:::{name}:::{description.format(Data=d)}:::{solutions}:::{tech_things}"
                    else:
                        call_data[code] = f"e00:::{critical_error_name}:::{critical_error_description.format(Data=code)}::::Code not found: {code}"
        
        except Exception:
            call_data["e00"] = f"e00:::Critical Error:::Failed to load error data::::{traceback.format_exc()}"
        
        if call_data:
            result = bpy.ops.special.absolute_solver('INVOKE_DEFAULT', call_data="|||".join(call_data.values()))
            if 'CANCELLED' in result:
                raise Exception("Cancelled by user")
        
        Call_AS.call_queue.clear()
        Call_AS.last_call_time = current_time
        Call_AS.is_processing = False

class AbsoluteSolverPanel(bpy.types.Operator):
    bl_label = "Absolute Solver"
    bl_idname = "special.absolute_solver"
    bl_options = {'REGISTER', 'UNDO'}

    call_data: bpy.props.StringProperty()

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
        return context.window_manager.invoke_popup(self, width=600)
    
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
            row.label(text=f"{translate('Code')}: {error['Code']}")
        
            row = sbox.row()
            row.label(text=f"{translate('Name')}: {translate(error['Name'])}")

            row = sbox.row()
            row.label(text=f"{translate('Description')}: {error['Description']}")

            if error["Solutions"]:
                sbox = box.box()
                row = sbox.row()
                row.label(text=f"{translate('Solutions')}:")
                for solution_operator in error["Solutions"].split("; "):
                    row = sbox.row()
                    solution = row.operator(solution_operator)
                    if hasattr(solution, "description"):
                        solution.description = error["Description"]

            if error["Tech_Things"]:
                sbox = box.box()
                row = sbox.row()
                row.operator("special.open_console")

                row = sbox.row()
                copy_to_clipboard = row.operator("special.copy_to_clipboard", text=translate("Copy Tech Things to Clipboard"))
                copy_to_clipboard.text = error["Tech_Things"]

                print(f"\033[33mAbsolute Solver Report: \033[31m\n{error['Tech_Things']}\033[0m")
            
            row = layout.row()
            if error["Solutions"]:
                auto_solution = row.operator(error["Solutions"].split("; ")[0], text="Auto Solve", depress=True)
                if hasattr(auto_solution, "description"):
                    auto_solution.description = error["Description"]
            ignore_operator = row.operator("special.as_ignore")
            ignore_operator.error_code = error["Code"]

    def execute(self, context):
        return {'FINISHED'}

class AbsoluteSolverIgnore(bpy.types.Operator):
    bl_idname = "special.as_ignore"
    bl_label = "Ignore"

    error_code: bpy.props.StringProperty()

    def execute(self, context):
        as_props = context.scene.miblend_properties.absolute_solver_properties
        ignored_list = as_props.ignored_codes.split()

        if self.error_code not in ignored_list:
            ignored_list.append(self.error_code)
            as_props.ignored_codes = " ".join(ignored_list)
            self.report({'INFO'}, f"{self.error_code} is being ignored now.")

        return {'FINISHED'}