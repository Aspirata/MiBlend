from bpy.types import Panel
from ...mib_utils import get_preferences


class MIBLEND_PT_procedural_pbr(Panel):
    bl_label = "Procedural PBR"
    bl_idname = "miblend.procedural_pbr_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MiBlend'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = get_preferences()

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()

        box = layout.box()
        row = box.row()
        row.label(text="Procedural PBR", icon="NODE_MATERIAL")

        row = box.row()
        row.prop(scene.miblend_properties.procedural_pbr_properties, "use_normals")
        row.prop(scene.miblend_properties.procedural_pbr_properties, "toggle_normals_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.toggle_normals_settings else "TRIA_LEFT"), icon_only=True)
        if scene.miblend_properties.procedural_pbr_properties.toggle_normals_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Normals Type:", icon="NORMALS_FACE")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "normals_selector", expand=True)

            if scene.miblend_properties.procedural_pbr_properties.normals_selector == "Bump":
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Bump Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "bump_strength", slider=True)
            else:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Procedural Normals Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_size", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_blur", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_strength", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_exclude", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_min", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_max", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_size_x_multiplier", slider=True)

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "pnormals_size_y_multiplier", slider=True)
            
            row = tbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "revert_normals")
            row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_normals
        
        row = box.row()
        row.prop(scene.miblend_properties.procedural_pbr_properties, "use_procedural_emission_and_animation")
        row.prop(scene.miblend_properties.procedural_pbr_properties, "toggle_procedural_emission_and_animation_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_emission_and_animation_settings else "TRIA_LEFT"), icon_only=True)
        if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_emission_and_animation_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Procedural Emission & Animation Settings:", icon="MODIFIER")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "camera_strength")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "non_camera_strength")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "use_procedural_animation")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "randomize_animation_speed")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "custom_peaa_config")

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "revert_procedural_emission_and_animation")
            row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_procedural_emission_and_animation
        
        if preferences.experimental_features:
            row = box.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "use_procedural_specular")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "toggle_procedural_specular_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_specular_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_specular_settings:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Procedural Specular Settings:", icon="MODIFIER")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "procedural_specular_interpolation")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "procedural_specular_difference")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "revert_procedural_specular")
                row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_procedural_specular
        
            row = box.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "use_procedural_roughness")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "toggle_procedural_roughness_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_roughness_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.toggle_procedural_roughness_settings:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Procedural Roughness Settings:", icon="MODIFIER")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "procedural_roughness_interpolation")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "procedural_roughness_difference")

                row = sbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "revert_procedural_roughness")
                row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_procedural_roughness

        row = box.row()
        row.prop(scene.miblend_properties.procedural_pbr_properties, "advanced_settings", toggle=True, text="Advanced Settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.advanced_settings else "TRIA_RIGHT"))
        if scene.miblend_properties.procedural_pbr_properties.advanced_settings:
            sbox = box.box()

            row = sbox.row()
            row.prop(context.scene.miblend_properties.procedural_pbr_properties, "change_bsdf")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "change_bsdf_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.change_bsdf_settings else "TRIA_LEFT"), icon_only=True)
            if  scene.miblend_properties.procedural_pbr_properties.change_bsdf_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Global PBSDF Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "specular", slider=True)
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "roughness", slider=True)

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "use_sss")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "sss_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.sss_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.sss_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="SSS Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "sss_type", text="")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "sss_skip")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "connect_texture")

                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "sss_weight", slider=True)
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "sss_scale", slider=True)
                
                row = tbox.row()
                row.prop(context.scene.miblend_properties.procedural_pbr_properties, "revert_sss")
                row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_sss
            
            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "use_translucency")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "translucency_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.translucency_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.translucency_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Translucent Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "translucency", slider=True)

                row = tbox.row()
                row.prop(context.scene.miblend_properties.procedural_pbr_properties, "revert_translucency")
                row.enabled = not context.scene.miblend_properties.procedural_pbr_properties.use_translucency

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "make_metal")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "metal_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.metal_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.metal_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Metallic Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "metal_metallic", slider=True)
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "metal_roughness", slider=True)

            row = sbox.row()
            row.prop(scene.miblend_properties.procedural_pbr_properties, "make_reflections")
            row.prop(scene.miblend_properties.procedural_pbr_properties, "reflections_settings", icon=("TRIA_DOWN" if scene.miblend_properties.procedural_pbr_properties.reflections_settings else "TRIA_LEFT"), icon_only=True)
            if scene.miblend_properties.procedural_pbr_properties.reflections_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Reflective Materials Settings:", icon="MODIFIER")
                row = tbox.row()
                row.prop(scene.miblend_properties.procedural_pbr_properties, "reflections_roughness", text="Roughness", slider=True)
                
        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.apply_procedural_pbr", text="Apply Procedural PBR", icon="CHECKMARK")
