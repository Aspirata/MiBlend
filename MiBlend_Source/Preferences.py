from bpy.types import AddonPreferences
from .MIB_API import blender_version
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)

class MiBlendPreferences(AddonPreferences):
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

    mc_instances_path: StringProperty(
        name="Minecraft Instances Folder",
        subtype="DIR_PATH"
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

    dev_tools: BoolProperty(
        name="Dev Tools",
        default=False
    )

    dprint: BoolProperty(
        name="dprint",
        default=True
    )

    perf_time: BoolProperty(
        name="Perf_Time",
        default=False
    )

    debug_tools: BoolProperty(
        name="Debug Tools",
        default=False
    )

    uas_debug_mode: BoolProperty(
        name="UAS v2 Debug Mode",
        default=False
    )

    experimental_features: BoolProperty(
        name="Experimental Features",
        default=False
    )

    open_console_on_start: BoolProperty(
        name="Open Console On Start",
        default=False
    )

    dev_packs_path: StringProperty(
        name="Dev Resource Packs Folder",
        subtype="DIR_PATH"
    )

    enable_custom_packs_path: BoolProperty(
        name="Enable Resource Packs Folder",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="UI:")                                                          # UI

        if blender_version(">= 4.1.0"):
            row = box.row()
            row.prop(self, "transparent_ui")
        else:
            self.transparent_ui = False

        row = box.row()
        row.prop(self, "enable_warnings")

        box = layout.box()
        row = box.row()
        row.label(text="Algorithms:")                                                  # Algorithms

        row = box.row()
        row.label(text="Absolute Solver Mode:")
        row = box.row()
        row.prop(self, "as_mode", text='as_mode', expand=True)

        row = box.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")
        row = box.row()
        row.prop(self, "emissiondetection", text='emissiondetection', expand=True)

        box = layout.box()
        row = box.row()
        row.label(text="Other:")                                                       # Other

        row = box.row()
        row.prop(self, "mc_instances_path")
        
        box = layout.box()
        row = box.row()
        row.prop(self, "dev_tools", text="")
        row.label(text="Dev Tools:")                                                   # Dev Tools

        if self.dev_tools:
            row = box.row()
            row.prop(self, "dprint", toggle=True)

            row = box.row()
            row.prop(self, "perf_time", toggle=True)
            
            row = box.row()
            row.prop(self, "debug_tools", toggle=True)

            row = box.row()
            row.prop(self, "uas_debug_mode", toggle=True)

            row = box.row()
            row.prop(self, "experimental_features", toggle=True)

            row = box.row()
            row.prop(self, "open_console_on_start", toggle=True)

            row = box.row()
            row.prop(self, "dev_packs_path")
            row.prop(self, "enable_custom_packs_path", text="")
        else:
            row = box.row()
            row.label(text="Dev Tools Disabled")