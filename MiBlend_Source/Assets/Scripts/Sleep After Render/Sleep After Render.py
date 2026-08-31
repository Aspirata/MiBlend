import bpy, os, platform, subprocess


def sleep_after_render(dummy):
    system = platform.system()

    try:
        if system == "Windows":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        elif system == "Linux":
            subprocess.run(["systemctl", "suspend"])
        elif system == "Darwin":
            subprocess.run(["pmset", "sleepnow"])
    except Exception as e:
        print(f"Cannot sleep system: {e}")

handler_key = "miblend_sleep_after_render"
previous_handler = bpy.app.driver_namespace.get(handler_key)
if previous_handler in bpy.app.handlers.render_complete:
    bpy.app.handlers.render_complete.remove(previous_handler)

bpy.app.driver_namespace[handler_key] = sleep_after_render
bpy.app.handlers.render_complete.append(sleep_after_render)
