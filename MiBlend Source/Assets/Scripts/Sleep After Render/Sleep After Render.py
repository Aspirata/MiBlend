import bpy
import os

def sleep_after_render(dummy):
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    
bpy.app.handlers.render_complete.append(sleep_after_render)