import bpy, json
from typing import Union
from pathlib import Path
from bpy.types import AddonPreferences
from .MIB_API import main_directory
from bpy.props import BoolProperty, StringProperty


class MiBlendPreferences(AddonPreferences):
    bl_idname = __package__

    @staticmethod
    def override_preference(setting_name: str, default_value: Union[str, bool, int, float]) -> Union[str, bool, int, float]:
        settings_override_path = Path(main_directory).parent / "miblend_preferences_override.json"
        if settings_override_path.exists():
            return json.loads(settings_override_path.read_text()).get(setting_name, default_value)
        return default_value

    transparent_ui: BoolProperty(
        name="Transparent UI",
        description="Toggles Transparent GUI",
        default=override_preference("transparent_ui", False),
    )

    show_warnings: BoolProperty(
        name="Show Warnings",
        description="Display Warning Messages with Absolute Solver",
        default=override_preference("show_warnings", True)
    )

    #enable_deprecated_features: BoolProperty(
    #    name="Enable Deprecated Features",
    #    default=override_preference("enable_deprecated_features", False)
    #)

    experimental_features: BoolProperty(
        name="Experimental Features",
        description="Enable Unfinished or Highly Experimental Tools. May be Unstable !",
        default=override_preference("experimental_features", False)
    )

    mc_instances_path: StringProperty(
        name="Minecraft Instances Folder",
        description="Path to the Folder Containing Your Minecraft Instances (MultiMC, Prism Launcher, CurseForge, etc.)",
        subtype="DIR_PATH"
    )

    update_packs: BoolProperty(
        name="Update Packs",
        description="Download and Update Built-in Resource Packs on Resource Packs List Reload (requires internet)",
        default=override_preference("update_packs", True)
    )

    dev_tools: BoolProperty(
        name="Dev Tools",
        description="Show Advanced Developer and Debugging Options",
        default=override_preference("dev_tools", False)
    )

    dprint: BoolProperty(
        name="dprint",
        description="Print Debug Information About the Add-on's Work to the System Console",
        default=override_preference("dprint", True)
    )

    debug_panel: BoolProperty(
        name="Enable Debug Panel",
        description="Enable a Special 'MiBlend Debug' panel",
        default=override_preference("debug_panel", False)
    )

    deep_debug: BoolProperty(
        name="Deep Debug",
        description="Enable Deep Debug Information",
        default=override_preference("deep_debug", False)
    )

    rp_debug_mode: BoolProperty(
        name="Resource Packs Debug Mode",
        description="Enable Debug Information Printing in Resource Packs Functions",
        default=override_preference("rp_debug_mode", False)
    )

    fw_debug_mode: BoolProperty(
        name="Fix World Debug Mode",
        description="Enable Debug Information Printing in the Fix Word Function",
        default=override_preference("fw_debug_mode", False)
    )

    fm_debug_mode: BoolProperty(
        name="Fix Materials Debug Mode",
        description="Enable Debug Information Printing in the Fix Materials Function",
        default=override_preference("fm_debug_mode", False)
    )

    ui_debug_mode: BoolProperty(
        name="UI Debug Mode",
        description="Enable Debug Information Printing in UI Functions",
        default=override_preference("ui_debug_mode", False)
    )

    perf_time: BoolProperty(
        name="Perf_Time",
        description="Print Execution Time of Major Operations",
        default=override_preference("perf_time", False)
    )

    debug_tools: BoolProperty(
        name="Debug Tools",
        description="Enable Extra Debugging Operators and Tools",
        default=override_preference("debug_tools", False)
    )

    uas_debug_mode: BoolProperty(
        name="UAS v2 Debug Mode",
        description="Enable Debug Information Printing in UAS v2 Functions",
        default=override_preference("uas_debug_mode", False)
    )

    dev_packs_path: StringProperty(
        name="Dev Resource Packs Folder",
        description="Path to Your Local Resource Packs (Overrides Built-in Ones, Usefull When Using Custom Build of MiBlend)",
        subtype="DIR_PATH",
        default=override_preference("dev_packs_path", "")
    )

    enable_custom_packs_path: BoolProperty(
        name="Enable Resource Packs Folder",
        description="Enables Using of Dev Resource Packs Folder",
        default=override_preference("enable_custom_packs_path", False)
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
        except Exception:
            pass

        box = layout.box()
        row = box.row()
        row.label(text="UI:")                                                          # UI

        row = box.row()
        row.prop(self, "transparent_ui")

        row = box.row()
        row.prop(self, "show_warnings")

        box = layout.box()
        row = box.row()
        row.label(text="Algorithms:")                                                  # Algorithms

        row = box.row()
        row.prop(self, "update_packs")

        box = layout.box()
        row = box.row()
        row.label(text="Other:")                                                       # Other

        #row = box.row()
        #row.prop(self, "enable_deprecated_features")

        row = box.row()
        row.prop(self, "experimental_features")

        row = box.row()
        row.prop(self, "mc_instances_path")

        row = box.row()
        row.operator("preferences.save_preferences")

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

            row = box.row()
            row.prop(self, "dev_packs_path")
            row.prop(self, "enable_custom_packs_path", text="")
        else:
            row = box.row()
            row.label(text="Dev Tools Disabled")