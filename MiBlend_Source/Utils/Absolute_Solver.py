from ..Data import *
import bpy, time

def Call_AS(code: str, tech_things: str ="", data: str =""):
    Preferences = bpy.context.preferences.addons[str(__package__).split(".")[0]].preferences
    
    # Store calls in a queue
    if not hasattr(Call_AS, 'call_queue'):
        Call_AS.call_queue = []
        Call_AS.last_call_time = 0
    
    current_time = time.time()
    
    # Add current call to queue
    Call_AS.call_queue.append((code, data))
    
    # Process queue if 5 seconds passed or this is first call
    if current_time - Call_AS.last_call_time >= 5.0 or len(Call_AS.call_queue) == 1:
        type = code[0]
        number = "".join(code[1:])
            
        # Process all queued calls
        for code, d in Call_AS.call_queue:
            with open(os.path.join(utils_directory, "absolute_solver_list.json"), "r") as file:
                data = json.load(file)
                critical_error_name = data.get("errors", {}).get("00", {}).get("name", None)
                critical_error_description = data.get("errors", {}).get("00", {}).get("description", None)

                if type == "w":
                    name = data.get("warnings", {}).get(number, {}).get("name", None)
                    description = data.get("warnings", {}).get(number, {}).get("description", None)
                elif type == "e":
                    if not Preferences.show_warnings:
                        continue
                    name = data.get("errors", {}).get(number, {}).get("name", None)
                    description = data.get("errors", {}).get(number, {}).get("description", None)
                elif type == "n":
                    name = data.get("null", {}).get(number, {}).get("name", None)
                    description = data.get("null", {}).get(number, {}).get("description", None)

            if name and description:
                try:
                    bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Code = code, Name = name, Description = description.format(Data=d), Tech_Things = tech_things)
                except Exception as error:
                    bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Code = "e00", Name = critical_error_name, Description = critical_error_description.format(Data=code), Tech_Things = error)
            else:
                print(f"Error: {code} {name} {description}")
                bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Code = "e00", Name = critical_error_name, Description = critical_error_description.format(Data=code), Tech_Things = f"{code} {name} {description}")
        
        # Clear queue and update time
        Call_AS.call_queue = []
        Call_AS.last_call_time = current_time

class AbsoluteSolverPanel(bpy.types.Operator):
    bl_label = "Absolute Solver"
    bl_idname = "special.absolute_solver"
    bl_options = {'REGISTER', 'UNDO'}

    Code: bpy.props.StringProperty()
    Name: bpy.props.StringProperty()
    Description: bpy.props.StringProperty()
    Tech_Things: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"Code: {self.Code}")
    
        row = sbox.row()
        row.label(text=f"Name: {self.Name}")

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"Description: {self.Description}")

        if self.Tech_Things != "":
            sbox = box.box()
            row = sbox.row()
            row.operator("special.open_console")

            row = sbox.row()
            copy_to_clipboard = row.operator("special.copy_to_clipboard", text="Copy Tech Things to Clipboard")
            copy_to_clipboard.text = self.Tech_Things

            # Print the error to the console
            print(f"\033[33mAbsolute Solver Report: \033[31m\n{self.Tech_Things}\033[0m")

    def execute(self, context):
        return {'FINISHED'}
