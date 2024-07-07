from bpy.types import AddonPreferences
from .MCB_API import blender_version
from .Translator import Availible_Translations
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)

class McblendPreferences(AddonPreferences):
    bl_idname = __package__

    transparent_ui: BoolProperty(
        name="Transparent UI",
        default=False,
    )

    enable_warnings: BoolProperty(
        name="Enable Warnings",
        default=True
    )

    as_mode: EnumProperty(
        items=[('None', 'None', 'No Errors will be Displayed'),
            ('Smart', 'Smart', 'Only Critical Errors will be Displayed (For Smart People)'),
            ('Full', 'Full', 'All Errors will be Displayed')],
        name="as_mode",
        default='Full'
    )

    dev_tools: BoolProperty(
        name="Dev Tools",
        default=False
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
        row = box.row()
        row.label(text="UI:")

        if blender_version(">= 4.1.0"):
            row = box.row()
            row.prop(self, "transparent_ui")
        else:
            self.transparent_ui = False

        row = box.row()
        row.prop(self, "enable_warnings")

        box = layout.box()
        row = box.row()
        row.label(text="Algorithms:")

        row = box.row()
        row.label(text="Absolute Solver Mode:")
        row = box.row()
        row.prop(self, "as_mode", text='as_mode', expand=True)

        row = box.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")
        row = box.row()
        row.prop(self, "emissiondetection", text='emissiondetection', expand=True)

        row = box.row()
        row.prop(self, "dev_tools")