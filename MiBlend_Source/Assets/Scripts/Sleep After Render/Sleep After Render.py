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
    
bpy.app.handlers.render_complete.append(sleep_after_render)