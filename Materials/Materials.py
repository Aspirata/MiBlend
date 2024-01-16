import bpy
import os
from ..Data import *
from bpy.props import (IntProperty, BoolProperty, FloatProperty)
#Replace Materials

script_directory = os.path.dirname(os.path.realpath(__file__))
blend_file_path = os.path.join(script_directory, "Materials.blend")

def MaterialIn(Array, material):
    for keyword in Array:
        if keyword in material.name.lower():
            return True
        else:
            return False
    
def append_materials(upgraded_material_name, selected_object, i):
    if upgraded_material_name not in bpy.data.materials:
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.materials = [upgraded_material_name]
        appended_material = bpy.data.materials.get(upgraded_material_name)
        selected_object.data.materials[i] = appended_material
    else:
        selected_object.data.materials[i] = bpy.data.materials[upgraded_material_name]

def upgrade_materials():
    for selected_object in bpy.context.selected_objects:
        for i, material in enumerate(selected_object.data.materials):
            for original_material, upgraded_material in Materials.items():
                if original_material in material.name.lower():
                    append_materials(upgraded_material, selected_object, i)

# Fix World
                        
def fix_world():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            PBSDF = None
            if MaterialIn(Alpha_Blend_Materials, material):
                material.blend_method = 'BLEND'
            else:
                material.blend_method = 'HASHED'

            if material.node_tree.nodes.get("Principled BSDF") != None:
                PBSDF = material.node_tree.nodes.get("Principled BSDF")

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = material.node_tree.nodes[node.name]
                    image_texture_node.interpolation = "Closest"

            if (image_texture_node and PBSDF) != None:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])
                if MaterialIn(Emissive_Materials, material):
                    material.node_tree.links.new(image_texture_node.outputs["Color"], PBSDF.inputs[26])

                if MaterialIn(Backface_Culling_Materials, material):
                    material.use_backface_culling = True
                    geometry_node = material.node_tree.nodes.new(type='ShaderNodeNewGeometry')
                    geometry_node.location = (image_texture_node.location.x + 100, image_texture_node.location.y + 230)
                    invert_node = material.node_tree.nodes.new(type='ShaderNodeInvert')
                    invert_node.location = (image_texture_node.location.x + 260, image_texture_node.location.y - 200)
                    mix_node = material.node_tree.nodes.new(type='ShaderNodeMix')
                    mix_node.location = (invert_node.location.x + 170, image_texture_node.location.y - 110)
                    mix_node.blend_type = 'MULTIPLY'
                    mix_node.data_type =  'RGBA'
                    mix_node.inputs[0].default_value = 1
                    material.node_tree.links.new(geometry_node.outputs["Backfacing"], invert_node.inputs[1])
                    material.node_tree.links.new(invert_node.outputs["Color"], mix_node.inputs["A"])
                    material.node_tree.links.new(image_texture_node.outputs["Alpha"], mix_node.inputs["B"])
                    material.node_tree.links.new(mix_node.outputs["Result"], PBSDF.inputs["Alpha"])

        selected_object.data.update()

class RecreateSky(bpy.types.Operator):
    bl_label = "Recreate Sky"
    bl_idname = "wm.recreate_sky"
    
    def execute(self, context):

        world = bpy.context.scene.world
        world_material_name = "Mcblend World"
        
        if hasattr(bpy.context.scene.world, 'Rotation'):
            del world["Rotation"]
        else:
            world["Rotation"] = 0.0
            bpy.types.World.Rotation = FloatProperty(name="Rotation", description="Rotation For World", default=0.0, min=0.0, max=960.0, subtype='ANGLE')
            
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.worlds = [world_material_name]
        appended_world_material = bpy.data.worlds.get(world_material_name)

        bpy.context.scene.world = appended_world_material
            
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=560)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.label(text="WARNING !", icon='ERROR')
        row = box.row()
        row.label(text="This option should be used only if something is broken, as this option will reset material and settings")

classes = [RecreateSky]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()


def create_sky():

    world_material_name = "Mcblend World"
    world = bpy.context.scene.world
    bpy.types.World.Rotation = None
    
    if hasattr(bpy.context.scene.world, 'Rotation') and bpy.context.scene.world == bpy.data.worlds[world_material_name]:
        bpy.ops.wm.recreate_sky('INVOKE_DEFAULT')
    else:
        world["Rotation"] = 0.0
        bpy.types.World.Rotation = FloatProperty(name="Rotation", description="Rotation For World", default=0.0, min=0.0, max=960.0, subtype='ANGLE')

        if world_material_name not in bpy.data.worlds:
            with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                data_to.worlds = [world_material_name]
            appended_world_material = bpy.data.worlds.get(world_material_name)
        else:
            appended_world_material = bpy.data.worlds[world_material_name]

        bpy.context.scene.world = appended_world_material

#def create_clouds():


# Fix materials
    
def fix_materials():
    for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            image_texture_node = None
            PBSDF = None

            material.blend_method = 'HASHED'

            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    image_texture_node = material.node_tree.nodes[node.name]
                    material.node_tree.nodes[node.name].interpolation = "Closest" 
            
            if material.node_tree.nodes.get("Principled BSDF") != None:
                PBSDF = material.node_tree.nodes.get("Principled BSDF")

            if (image_texture_node and PBSDF) != None:
                material.node_tree.links.new(image_texture_node.outputs["Alpha"], PBSDF.inputs[4])

        selected_object.data.update()

#
        
# Set Procedural PBR
        
def setproceduralpbr():
     for selected_object in bpy.context.selected_objects:
        for material in selected_object.data.materials:
            scene = bpy.context.scene
            image_texture_node = None
            PBSDF = None
            bump_node = None
            

            if material.node_tree.nodes.get("Principled BSDF") is not None:
                PBSDF = material.node_tree.nodes.get("Principled BSDF")

                PBSDF.inputs["Roughness"].default_value = 0.6
                PBSDF.inputs[12].default_value = 0.4 # Specular

                if MaterialIn(Metal, material):
                    PBSDF.inputs["Roughness"].default_value = 0.2
                    PBSDF.inputs["Metallic"].default_value = 0.7

                if MaterialIn(Reflective, material):
                    PBSDF.inputs["Roughness"].default_value = 0.1

                for node in material.node_tree.nodes:
                    if node.type == "TEX_IMAGE":
                        image_texture_node = material.node_tree.nodes[node.name]
                    if node.type == "BUMP":
                        bump_node = material.node_tree.nodes[node.name]

                if scene.bump.use_bump == True and image_texture_node and bump_node == None:
                    bump_node = material.node_tree.nodes.new(type='ShaderNodeBump')
                    bump_node.location = (PBSDF.location.x - 200, PBSDF.location.y - 100)
                    material.node_tree.links.new(image_texture_node.outputs["Color"], bump_node.inputs['Height'])
                    material.node_tree.links.new(bump_node.outputs['Normal'], PBSDF.inputs['Normal'])
                    bump_node.inputs[0].default_value = 0.2
                
        selected_object.data.update()
#