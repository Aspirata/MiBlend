import bpy
import sys
from bpy.types import AddonPreferences
from .MIB_API import blender_version, override_setting
from bpy.props import (IntProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty)

class MiBlendPreferences(AddonPreferences):
    bl_idname = __package__

    transparent_ui: BoolProperty(
        name="Transparent UI",
        default=override_setting("transparent_ui", False),
    )

    show_warnings: BoolProperty(
        name="Show Warnings",
        default=override_setting("show_warnings", True)
    )

    enable_deprecated_features: BoolProperty(
        name="Enable Deprecated Features (Requires Restart)",
        default=override_setting("enable_deprecated_features", False)
    )

    experimental_features: BoolProperty(
        name="Experimental Features",
        default=override_setting("experimental_features", False)
    )

    mc_instances_path: StringProperty(
        name="Minecraft Instances Folder",
        subtype="DIR_PATH"
    )

    def emissiondetectionfix():
        if blender_version("3.6.x"):
            return 'Manual'
        else:
            return 'Combined'

    emissiondetection: EnumProperty(
        items=[('Automatic', 'Automatic', ''), 
            ('Combined', 'Combined', ''),
            ('Manual', 'Manual', '')],
        name="emissiondetection",
        default=override_setting("emissiondetection", emissiondetectionfix())
    )

    update_packs: BoolProperty(
        name="Update Packs",
        default=override_setting("update_packs", True)
    )

    dev_tools: BoolProperty(
        name="Dev Tools",
        default=override_setting("dev_tools", False)
    )

    dprint: BoolProperty(
        name="dprint",
        default=override_setting("dprint", True)
    )

    debug_panel: BoolProperty(
        name="Enable Debug Panel (Requires Restart)",
        default=override_setting("enable_debug_panel", False)
    )

    deep_debug: BoolProperty(
        name="Deep Debug",
        default=override_setting("deep_debug", False)
    )

    rp_debug_mode: BoolProperty(
        name="Resource Packs Debug Mode",
        default=override_setting("rp_debug_mode", False)
    )

    fw_debug_mode: BoolProperty(
        name="Fix World Debug Mode",
        default=override_setting("fw_debug_mode", False)
    )

    fm_debug_mode: BoolProperty(
        name="Fix Materials Debug Mode",
        default=override_setting("fm_debug_mode", False)
    )

    ui_debug_mode: BoolProperty(
        name="UI Debug Mode",
        default=override_setting("ui_debug_mode", False)
    )

    perf_time: BoolProperty(
        name="Perf_Time",
        default=override_setting("perf_time", False)
    )

    debug_tools: BoolProperty(
        name="Debug Tools",
        default=override_setting("debug_tools", False)
    )

    uas_debug_mode: BoolProperty(
        name="UAS v2 Debug Mode",
        default=override_setting("uas_debug_mode", False)
    )

    open_console_on_start: BoolProperty(
        name="Open Console On Start",
        default=override_setting("open_console_on_start", False)
    )

    dev_packs_path: StringProperty(
        name="Dev Resource Packs Folder",
        subtype="DIR_PATH",
        default=override_setting("dev_packs_path", "")
    )

    enable_custom_packs_path: BoolProperty(
        name="Enable Resource Packs Folder",
        default=override_setting("enable_custom_packs_path", False)
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Info:")                                                        # Info
        try:
            for component_name, component in bpy.context.scene["mib_options"]["components_vesion"].items():
                row = box.row()
                row.label(text=f"{component_name}: {component}")
        except:
            pass

        box = layout.box()
        row = box.row()
        row.label(text="UI:")                                                          # UI

        if blender_version(">= 4.1.0"):
            row = box.row()
            row.prop(self, "transparent_ui")
        else:
            self.transparent_ui = False

        row = box.row()
        row.prop(self, "show_warnings")

        box = layout.box()
        row = box.row()
        row.label(text="Algorithms:")                                                  # Algorithms

        row = box.row()
        row.label(text="Emissive Blocks Detection Method:", icon="LIGHT")

        row = box.row()
        row.prop(self, "emissiondetection", text='emissiondetection', expand=True)

        row = box.row()
        row.prop(self, "update_packs")

        box = layout.box()
        row = box.row()
        row.label(text="Other:")                                                       # Other

        row = box.row()
        row.prop(self, "enable_deprecated_features")

        row = box.row()
        row.prop(self, "experimental_features")

        row = box.row()
        row.prop(self, "mc_instances_path")
        
        box = layout.box()
        row = box.row()
        row.prop(self, "dev_tools", text="")
        row.label(text="Dev Tools:")                                                   # Dev Tools

        if self.dev_tools:
            row = box.row()
            row.prop(self, "dprint", toggle=True)

            sbox = box.box()

            row = sbox.row()
            row.label(text="Debug:")

            row = sbox.row()
            row.prop(self, "debug_tools", toggle=True)

            row = sbox.row()
            row.prop(self, "debug_panel", toggle=True)

            row = sbox.row()
            row.prop(self, "deep_debug", toggle=True)

            row = sbox.row()
            row.prop(self, "uas_debug_mode", toggle=True)

            row = sbox.row()
            row.prop(self, "rp_debug_mode", toggle=True)

            row = sbox.row()
            row.prop(self, "fw_debug_mode", toggle=True)

            row = sbox.row()
            row.prop(self, "fm_debug_mode", toggle=True)

            row = sbox.row()
            row.prop(self, "ui_debug_mode", toggle=True)

            row = box.row()
            row.prop(self, "perf_time", toggle=True)

            if not sys.platform.startswith('linux'):
                row = box.row()
                row.prop(self, "open_console_on_start", toggle=True)

            row = box.row()
            row.prop(self, "dev_packs_path")
            row.prop(self, "enable_custom_packs_path", text="")
        else:
            row = box.row()
            row.label(text="Dev Tools Disabled")