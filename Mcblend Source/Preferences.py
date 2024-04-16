from .Data import *
from bpy.types import AddonPreferences
from .Translator import Availible_Translations

class McblendPreferences(AddonPreferences):
    bl_idname = "Mcblend"

    transparent_ui: BoolProperty(
        name="Transparent UI",
        default= checkconfig("transparent_ui"),
    )

    enable_warnings: BoolProperty(
        name="Enable Warnings",
        default=True
    )

    current_language: EnumProperty(
        items=[(name, name, "") for name, data in Availible_Translations.items()],
        description="",
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        if bpy.app.version >= (4, 1, 0):
            row = box.row()
            row.prop(self, "transparent_ui")
        else:
            self.transparent_ui = False

        row = box.row()
        row.prop(self, "enable_warnings")
    