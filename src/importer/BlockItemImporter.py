import math
from mathutils import Vector, Euler

from .utils import JsonUtils
from .utils import GeoUtils
import bpy

from .utils.GeoUtils import CubeData, FaceData
from .utils.JsonUtils import JsonObject

import os


def importModel(filepath):
	modelJsonObject = JsonUtils.load(filepath).asObject()
	elements = []

	for element in modelJsonObject.get("elements").asArray().asList():
		
		elementJsonObject = element.asObject()
		fromPos = []
		toPos = []
		originPos = [8, 0, 8]
		rotation = Euler((0, 0, 0))

		for fromE in elementJsonObject.get("from").asArray().asList():
			fromPos.append(fromE.asFloat())
		for toE in elementJsonObject.get("to").asArray().asList():
			toPos.append(toE.asFloat())

		if elementJsonObject.has("rotation"):
			rotationJsonObject = elementJsonObject.get("rotation").asObject()
			originPos.clear()
			for originE in rotationJsonObject.get("origin").asArray().asList():
				originPos.append(originE.asFloat())

			angle = rotationJsonObject.get("angle").asFloat()
			axis = rotationJsonObject.get("axis").asString()
			if axis == "x":
				rotation.x = -math.radians(angle)
			elif axis == "y":
				rotation.y = math.radians(angle)
			elif axis == "z":
				rotation.z = math.radians(angle)

		upFace: FaceData = FaceData([0, 0, 0, 0], "", 0)
		downFace: FaceData = FaceData([0, 0, 0, 0], "", 0)
		northFace: FaceData = FaceData([0, 0, 0, 0], "", 0)
		southFace: FaceData = FaceData([0, 0, 0, 0], "", 0)
		eastFace: FaceData = FaceData([0, 0, 0, 0], "", 0)
		westFace: FaceData = FaceData([0, 0, 0, 0], "", 0)

		if elementJsonObject.has("faces"):
			facesJsonObject = elementJsonObject.get("faces").asObject()
			upFace = getFace(facesJsonObject, "up")
			downFace = getFace(facesJsonObject, "down")
			northFace = getFace(facesJsonObject, "north")
			southFace = getFace(facesJsonObject, "south")
			eastFace = getFace(facesJsonObject, "east")
			westFace = getFace(facesJsonObject, "west")

		obj = GeoUtils.create_cube(CubeData(
			"cube", Vector(fromPos), Vector(toPos), Vector(originPos), rotation,
			northFace, southFace, eastFace, westFace, upFace, downFace
		))
		col = bpy.context.scene.collection
		col.objects.link(obj)
		bpy.context.view_layer.objects.active = obj
		obj.name = os.path.splitext(os.path.basename(filepath))[0]
		elements.append(obj)
	
	# It doesn't work
	if bpy.context.scene.assetsproperties.separate_model_parts == False:
		if len(elements) >= 2:
			main_object = elements[0]

			# Цикл по остальным объектам в списке
			for obj in elements[1:]:
				# Выбираем объект в текущей итерации
				bpy.context.view_layer.objects.active = obj
					
				# Выбираем все вершины в объекте
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				obj.select_set(True)
				bpy.context.view_layer.objects.active = obj
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')

				# Объединяем объект с основным объектом
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.join()


def getFace(facesJsonObject: JsonObject, name: str) -> FaceData:
	if facesJsonObject.has(name):
		faceJsonObject = facesJsonObject.get(name).asObject()
		rotation = 0
		if faceJsonObject.has("rotation"):
			rotation = faceJsonObject.get("rotation").asFloat()
		return FaceData(faceJsonObject.get("uv").data, faceJsonObject.get("texture").asString(), rotation)
	return FaceData([0, 0, 0, 0], "", 0)