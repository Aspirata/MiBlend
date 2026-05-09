from bpy.types import Panel
from ...mib_utils import get_preferences, draw_toggle_button


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
        procedural_pbr_props = scene.miblend_properties.procedural_pbr_properties

        if preferences.transparent_ui:
            self.bl_options = {'HIDE_HEADER'}
        else:
            self.bl_options = set()

        box = layout.box()
        row = box.row()
        row.label(text="Procedural PBR", icon="NODE_MATERIAL")

        row = box.row()
        row.prop(procedural_pbr_props, "use_normals")
        draw_toggle_button(row, procedural_pbr_props, "toggle_normals_settings")
        if procedural_pbr_props.toggle_normals_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Normals Type:", icon="NORMALS_FACE")

            row = sbox.row()
            row.prop(procedural_pbr_props, "normals_selector", expand=True)

            if procedural_pbr_props.normals_selector == "BUMP":
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Bump Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "bump_strength", slider=True)
            elif procedural_pbr_props.normals_selector == "PROCEDURAL_NORMALS":
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Procedural Normals Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_size", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_blur", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_strength", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_exclude", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_min", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_max", slider=True)
            
            elif procedural_pbr_props.normals_selector == "PROCEDURAL_NORMALS_V2":
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Procedural Normals V2 Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "procedural_normals_v2_size", slider=True)

                row = tbox.row()
                row.prop(procedural_pbr_props, "pnormals_strength", slider=True)
            
            row = sbox.row()
            row.prop(procedural_pbr_props, "revert_normals")
            row.enabled = not procedural_pbr_props.use_normals
        
        row = box.row()
        row.prop(procedural_pbr_props, "use_procedural_emission")
        draw_toggle_button(row, procedural_pbr_props, "toggle_procedural_emission_settings")
        if procedural_pbr_props.toggle_procedural_emission_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Procedural Emission Settings:", icon="MODIFIER")

            row = sbox.row()
            row.prop(procedural_pbr_props, "camera_emission_strength")

            row = sbox.row()
            row.prop(procedural_pbr_props, "non_camera_emission_strength")

            row = sbox.row()
            row.prop(procedural_pbr_props, "randomize_emission_strength")

            row = sbox.row()
            row.prop(procedural_pbr_props, "use_procedural_emission_custom_config")

            row = sbox.row()
            row.prop(procedural_pbr_props, "revert_procedural_emission")
            row.enabled = not procedural_pbr_props.use_procedural_emission
        
        if preferences.experimental_features:
            row = box.row()
            row.prop(procedural_pbr_props, "use_procedural_specular_and_roughness")
            draw_toggle_button(row, procedural_pbr_props, "toggle_procedural_specular_and_roughness_settings")
            if procedural_pbr_props.toggle_procedural_specular_and_roughness_settings:
                sbox = box.box()
                row = sbox.row()
                row.label(text="Procedural Specular & Roughness Settings:", icon="MODIFIER")

                row = sbox.row()
                row.prop(procedural_pbr_props, "procedural_specular_interpolation")

                row = sbox.row()
                row.prop(procedural_pbr_props, "procedural_specular_difference")

                row = sbox.row()
                row.prop(procedural_pbr_props, "procedural_roughness_interpolation")

                row = sbox.row()
                row.prop(procedural_pbr_props, "procedural_roughness_difference")

                row = sbox.row()
                row.prop(procedural_pbr_props, "revert_procedural_specular_and_roughness")
                row.enabled = not procedural_pbr_props.use_procedural_specular_and_roughness

        row = box.row()
        row.prop(procedural_pbr_props, "use_pbsdf_tweaks")
        draw_toggle_button(row, procedural_pbr_props, "toggle_pbsdf_tweaks_settings")
        if procedural_pbr_props.toggle_pbsdf_tweaks_settings:
            sbox = box.box()
            row = sbox.row()
            row.label(text="Global PBSDF Settings:", icon="MODIFIER")

            row = sbox.row()
            row.prop(procedural_pbr_props, "specular", slider=True)
            row.enabled = procedural_pbr_props.use_pbsdf_tweaks

            row = sbox.row()
            row.prop(procedural_pbr_props, "roughness", slider=True)
            row.enabled = procedural_pbr_props.use_pbsdf_tweaks

            sbox = box.box()
            row = sbox.row()
            row.label(text="Smart PBSDF Settings:", icon="MODIFIER")

            row = sbox.row()
            row.prop(procedural_pbr_props, "use_sss")
            draw_toggle_button(row, procedural_pbr_props, "toggle_sss_settings")
            if procedural_pbr_props.toggle_sss_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Subsurface Scattering Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "sss_type", text="")
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_sss

                row = tbox.row()
                row.prop(procedural_pbr_props, "use_sss_connect_texture_to_radius")
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_sss

                row = tbox.row()
                row.prop(procedural_pbr_props, "sss_weight", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_sss

                row = tbox.row()
                row.prop(procedural_pbr_props, "sss_scale", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_sss

                row = tbox.row()
                row.prop(procedural_pbr_props, "revert_sss")
                row.enabled = not procedural_pbr_props.use_pbsdf_tweaks or not procedural_pbr_props.use_sss

            row = sbox.row()
            row.prop(procedural_pbr_props, "use_metallic")
            draw_toggle_button(row, procedural_pbr_props, "toggle_metallic_settings")
            if procedural_pbr_props.toggle_metallic_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Metallic Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "metallic", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_metallic

                row = tbox.row()
                row.prop(procedural_pbr_props, "metallic_roughness", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_metallic

            row = sbox.row()
            row.prop(procedural_pbr_props, "use_reflectiveness")
            draw_toggle_button(row, procedural_pbr_props, "toggle_reflectiveness_settings")
            if procedural_pbr_props.toggle_reflectiveness_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Reflectiveness Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "reflections_roughness", text="Roughness", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_reflectiveness

            row = sbox.row()
            row.prop(procedural_pbr_props, "use_translucency")
            draw_toggle_button(row, procedural_pbr_props, "toggle_translucency_settings")
            if procedural_pbr_props.toggle_translucency_settings:
                tbox = sbox.box()
                row = tbox.row()
                row.label(text="Translucency Settings:", icon="MODIFIER")

                row = tbox.row()
                row.prop(procedural_pbr_props, "translucency", slider=True)
                row.enabled = procedural_pbr_props.use_pbsdf_tweaks and procedural_pbr_props.use_translucency

                row = tbox.row()
                row.prop(procedural_pbr_props, "revert_translucency", slider=True)
                row.enabled = not procedural_pbr_props.use_pbsdf_tweaks or not procedural_pbr_props.use_translucency
                
        row = box.row()
        row.scale_y = 1.4
        row.operator("miblend.apply_procedural_pbr", text="Apply Procedural PBR", icon="CHECKMARK")
