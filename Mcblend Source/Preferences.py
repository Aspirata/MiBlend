import bpy
from .MCB_API import *
from bpy.types import AddonPreferences
from .Translator import Availible_Translations

class McblendPreferences(AddonPreferences):
    bl_idname = __package__

    transparent_ui: BoolProperty(
        name="Transparent UI",
        default=checkconfig("transparent_ui"),
    )

    enable_warnings: BoolProperty(
        name="Enable Warnings",
        default=checkconfig("enable_warnings")
    )

    as_mode: EnumProperty(
        items=[('None', 'None', 'No Errors will be Displayed'),
            ('Smart', 'Smart', 'Only Critical Errors will be Displayed (For Smart People)'),
            ('Full', 'Full', 'All Errors will be Displayed')],
        name="as_mode",
        default='Full'
    )

    def emissiondetectionfix():
        if blender_version("3.6.x"):
            default='Manual'
        else:
            default='Automatic & Manual'
        return default

    emissiondetection: EnumProperty(
        items=[('Automatic', 'Automatic', ''), 
            ('Automatic & Manual', 'Both', ''),
            ('Manual', 'Manual', '')],
        name="emissiondetection",
        default=emissiondetectionfix()
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

        row = box.row()
        row.label(text="Absolute Solver Mode:")
        row = box.row()
        row.prop(self, "as_mode", text='as_mode', expand=True)

        row = box.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")
        row = box.row()
        row.prop(self, "emissiondetection", text='emissiondetection', expand=True)