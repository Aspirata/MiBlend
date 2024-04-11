from .Data import *

class AddonPreferences(AddonPreferences):
    bl_idname = "Mcblend"

    transparent_ui: BoolProperty(
        name="Transparent UI",
        default=False
    )

    enable_warnings: BoolProperty(
        name="Enable Warnings",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "transparent_ui")
        layout.prop(self, "enable_warnings")
