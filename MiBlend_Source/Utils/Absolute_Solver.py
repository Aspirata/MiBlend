from ..Data import *
from ..Utils.Translator import translate
import bpy, time

def Call_AS(code: str, tech_things: str = "", data: str = ""):
    Preferences = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences
    
    # Store calls in a queue
    if not hasattr(Call_AS, 'call_queue'):
        Call_AS.call_queue = []
        Call_AS.last_call_time = 0
        Call_AS.is_processing = False
    
    current_time = time.time()
    
    # Add current call to queue
    Call_AS.call_queue.append((code, data))
    
    # Process queue if enough time has passed or this is the first call
    if (current_time - Call_AS.last_call_time >= 5.0) and not Call_AS.is_processing:
        Call_AS.is_processing = True

        type = code[0]
        number = str(code[1:])

        call_data = []
        try:
            with open(os.path.join(utils_directory, "absolute_solver_list.json"), "r") as file:
                data_json = json.load(file)
                critical_error_name = data_json.get("errors", {}).get("00", {}).get("Name", "Critical Error")
                critical_error_description = translate(data_json.get("errors", {}).get("00", {}).get("Description", "Unknown error occurred: {Data}"))

                for code, d in Call_AS.call_queue:
                    type = code[0]
                    number = str(code[1:])
                    if type == "w":
                        if not Preferences.show_warnings:
                            continue
                        name = data_json.get("warnings", {}).get(number, {}).get("Name")
                        description = data_json.get("warnings", {}).get(number, {}).get("Description")
                        solutions = data_json.get("errors", {}).get(number, {}).get("Solutions", "")
                    elif type == "e":
                        name = data_json.get("errors", {}).get(number, {}).get("Name")
                        description = data_json.get("errors", {}).get(number, {}).get("Description")
                        solutions = data_json.get("errors", {}).get(number, {}).get("Solutions", "")
                    elif type == "n":
                        name = data_json.get("null", {}).get(number, {}).get("Name")
                        description = data_json.get("null", {}).get(number, {}).get("Description")

                    description = translate(description)

                    if name and description:
                        call_data.append({"Code": code, "Name": name, "Description": description.format(Data=d), "Solutions": solutions, "Tech_Things": tech_things})
                    else:
                        call_data.append({"Code": "e00", "Name": critical_error_name, "Description": critical_error_description.format(Data=code), "Tech_Things": f"Code not found: {code}"})
        
        except Exception:
            call_data.append({"Code": "e00", "Name": critical_error_name, "Description": critical_error_description.format(Data=code), "Tech_Things": str(traceback.format_exc())})

        if call_data:
            bpy.ops.special.absolute_solver('INVOKE_DEFAULT', **call_data[-1])

        # Update time and reset processing state
        Call_AS.call_queue.clear()
        Call_AS.last_call_time = current_time
        Call_AS.is_processing = False

class AbsoluteSolverPanel(bpy.types.Operator):
    bl_label = "Absolute Solver"
    bl_idname = "special.absolute_solver"
    bl_options = {'REGISTER', 'UNDO'}

    Code: bpy.props.StringProperty()
    Name: bpy.props.StringProperty()
    Description: bpy.props.StringProperty()
    Solutions: bpy.props.StringProperty()
    Tech_Things: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"{translate('Code')}: {self.Code}")
    
        row = sbox.row()
        row.label(text=f"{translate('Name')}: {(translate(self.Name))}")

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"{translate('Description')}: {self.Description}")

        if self.Solutions != "":
            sbox = box.box()
            row = sbox.row()
            row.label(text=f"{translate('Solutions')}:")
            for solution_operator in self.Solutions.split("; "):
                if solution_operator == "":
                    continue
                row = sbox.row()
                solution = row.operator(solution_operator)
                if hasattr(solution, "description"):
                    solution.description = self.Description

        if self.Tech_Things != "":
            sbox = box.box()
            row = sbox.row()
            row.operator("special.open_console")

            row = sbox.row()
            copy_to_clipboard = row.operator("special.copy_to_clipboard", text=translate("Copy Tech Things to Clipboard"))
            copy_to_clipboard.text = self.Tech_Things

            # Print the error to the console
            print(f"\033[33mAbsolute Solver Report: \033[31m\n{self.Tech_Things}\033[0m")

    def execute(self, context):
        return {'FINISHED'}
