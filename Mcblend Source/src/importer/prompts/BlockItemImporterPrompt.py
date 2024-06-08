import bpy
import json
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from ..BlockItemImporter import importModel


class ImporterPrompt(Operator, ImportHelper):
	"""Import Block/Item json models used for Minecraft Java edition"""
	bl_idname = "mcblend.import_blockitem"
	bl_label = "Import Block/Item"

	# ExportHelper mixin class uses this
	filename_ext = ".json"

	filter_glob: StringProperty(
		default="*.json",
		options={'HIDDEN'},
		maxlen=255,  # Max internal buffer length, longer would be clamped.
	)

	def execute(self, context):
		importModel(self.filepath)
		return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
	self.layout.operator(ImporterPrompt.bl_idname, text="MC Block/Item (.json)")
