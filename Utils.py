import bpy
import os
def CShadows():
    if bpy.context.scene.utils_properties.cshadowsselection == True:
        for obj in bpy.context.selected_objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_thickness = 0.01
    else:
        for obj in bpy.context.scene.objects:
            if hasattr(obj.data, 'use_contact_shadow'):
                obj.data.use_contact_shadow = True
                obj.data.contact_shadow_thickness = 0.01

def sleep_after_render(dummy):
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    
def sleep_detector():
    bpy.app.handlers.render_complete.append(sleep_after_render)