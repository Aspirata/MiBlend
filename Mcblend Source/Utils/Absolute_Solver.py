from ..Data import *
import bpy, re, traceback

Absolute_Solver_Errors = {

    # Quick Tip
    # m - Materials Error
    # u - User's Mistake

    "LoL": {
        "Error Name": "Zero Settings",
        "Description": "You disabled all {Data} settings, so it did nothing LoL",
        "Mode": "Full"
    },

    "000": {
        "Error Name": "Absolute Solver Error",
        "Description": "Absolute Solver Can't Display This Error - {Data}",
    },

    "001": {
        "Error Name": "Unknown",
        "Description": "An Unknown Error",
    },

    "m002": {
        "Error Name": "Empty Material Slot",
        "Description": "Material doesn't exist on slot {Data}",
        "Mode": "Full"
    },

    "m003": {
        "Error Name": "Object has no Materials",
        "Description": 'Object "{Data.name}" has no materials',
        "Mode": "Full"
    },

    "004": {
        "Error Name": ".blend File Not Found",
        "Description": "{Data}.blend not found",
    },

    "005": {
        "Error Name": "Internal Function Error",
        "Description": "Something is wrong in {Data}",
    },

    "u006": {
        "Error Name": "Color Space Not Found",
        "Description": "You have custom color manager that doesn't have {Data}",
    },

    "007": {
        "Error Name": "Create Thing Doesn't Exists in the File",
        "Description": "Create feature uses alredy imported asset to your file, so if you see this message then your file doesn't have {Data} and you should probably use recreate feature instead",
        "Mode": "Full"
    },
}

def Absolute_Solver(error_code="None", data=None, tech_things="None", error_name="None", description=None, mode=None):
    Preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences
    try:
        def GetASText(error_code, text):
            try:
                return Absolute_Solver_Errors[error_code][text]
            except:
                return None
        
        if error_code is not None:
            error_name = GetASText(error_code, "Error Name")
        
        if description is None:
            description = GetASText(error_code, 'Description')

            mode = "Full" if "Mode" in Absolute_Solver_Errors[error_code] else "Smart"

        if (mode == Preferences.as_mode or mode == "Full") and Preferences.as_mode != "None":
            bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Error_Code = error_code, Error_Name = error_name, Description = description.format(Data=data), Tech_Things = str(tech_things))
    except:
        bpy.ops.special.absolute_solver('INVOKE_DEFAULT', Error_Code = "000", Error_Name = GetASText("000", "Error Name"), Description = GetASText("000", 'Description'), Tech_Things = str(traceback.format_exc()))

class AbsoluteSolver(bpy.types.Operator):
    bl_label = "Absolute Solver"
    bl_idname = "special.absolute_solver"
    bl_options = {'REGISTER', 'UNDO'}

    Error_Code: bpy.props.StringProperty()
    Error_Name: bpy.props.StringProperty()
    Description: bpy.props.StringProperty()
    Tech_Things: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
            
        box = layout.box()
        sbox = box.box()
        if self.Error_Code != "None":
            row = sbox.row()
            row.label(text=f"Error Code: {self.Error_Code}")
        
        row = sbox.row()
        row.label(text=f"Error Name: {self.Error_Name}")

        sbox = box.box()
        row = sbox.row()
        row.label(text=f"Description: {self.Description}")

        if self.Tech_Things != "None":
            sbox = box.box()
            row = sbox.row()
            row.label(text="Tech Things:")

            split_tech_things = re.split(r'  |: ', self.Tech_Things)
            for part in split_tech_things:
                sbox.label(text=part)

            print(f"\033[33mAbsolute Solver Error Report: \033[31m\n{self.Tech_Things}\033[0m")
            sbox = box.box()
            row = sbox.row()
            row.operator("special.open_console")
    
    def execute(self, context):
        return {'FINISHED'}
