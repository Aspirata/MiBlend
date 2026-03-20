import bpy

mode = properties.get("Only Selected Objects", False)
overblur = clamp(0.0, properties.get("Overblur", 20.0), 100.0)
world_jitter = properties.get("World Jitter", False)

if mode:
    for obj in bpy.context.selected_objects:
        try:
            obj.data.use_shadow_jitter = True
            obj.data.shadow_jitter_overblur = overblur
        except:
            pass
else:
    for obj in bpy.context.scene.objects:
        try:
            obj.data.use_shadow_jitter = True
            obj.data.shadow_jitter_overblur = overblur
        except:
            pass
    

if bpy.context.scene.world != None and world_jitter:
    bpy.context.scene.world.use_sun_shadow_jitter = True
    bpy.context.scene.world.sun_shadow_jitter_overblur = overblur