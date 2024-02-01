import bpy
import os
def CShadows():
    for obj in bpy.context.selected_objects:
        if hasattr(obj.data, 'use_contact_shadow'):
            obj.data.use_contact_shadow = True

def sleep_after_render():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    bpy.app.handlers.render_complete.append(sleep_after_render)