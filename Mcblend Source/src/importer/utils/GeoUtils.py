import io
import math
import time
from typing import Dict

import bpy
import bmesh
import imbuf.types
from bpy.types import Image
from mathutils import Vector, Matrix, Euler
from .MinecraftUtils import ResourceLocation, getResource
from .JsonUtils import JsonElement


class FaceData:
	uv: list[float]
	texture: str
	rotation: int

	def __init__(self, uv: list[float], texture: str, rotation: int):
		self.uv = uv
		self.texture = texture.removeprefix("#")
		self.rotation = rotation


class CubeData:
	name: str
	minPos: Vector
	maxPos: Vector
	originPos: Vector
	rotation: Euler
	textures: dict[str, str]
	northFace: FaceData
	southFace: FaceData
	eastFace: FaceData
	westFace: FaceData
	upFace: FaceData
	downFace: FaceData

	def __init__(self, name: str, minPos: Vector, maxPos: Vector, originPos: Vector, rotation: Euler, textures: dict[str, str],
				 northFace: FaceData, southFace: FaceData, eastFace: FaceData, westFace: FaceData, upFace: FaceData, downFace: FaceData):
		self.textures = textures
		self.downFace = downFace
		self.upFace = upFace
		self.westFace = westFace
		self.eastFace = eastFace
		self.southFace = southFace
		self.northFace = northFace
		self.name = name
		self.minPos = Vector((minPos.x, minPos.z, minPos.y))
		self.maxPos = Vector((maxPos.x, maxPos.z, maxPos.y))
		self.originPos = Vector((originPos.x, originPos.z, originPos.y))
		self.rotation = rotation


def create_cube(data: CubeData):
	mesh = bpy.data.meshes.new(data.name)
	obj = bpy.data.objects.new(data.name, mesh)
	originPos = data.originPos
	minPos = data.minPos-originPos
	maxPos = data.maxPos-originPos

	verts = [
		(minPos.x, minPos.y, maxPos.z), (minPos.x, maxPos.y, maxPos.z), (maxPos.x, maxPos.y, maxPos.z), (maxPos.x, minPos.y, maxPos.z),
		(minPos.x, minPos.y, minPos.z), (minPos.x, maxPos.y, minPos.z), (maxPos.x, maxPos.y, minPos.z), (maxPos.x, minPos.y, minPos.z)
	]
	faces = []
	faceData = []
	if data.upFace is not None:
		faces.append((3, 0, 1, 2))
		faceData.append(data.upFace)
	if data.downFace is not None:
		faces.append((6, 5, 4, 7))
		faceData.append(data.downFace)
	if data.eastFace is not None:
		faces.append((1, 0, 4, 5))
		faceData.append(data.eastFace)
	if data.southFace is not None:
		faces.append((2, 1, 5, 6))
		faceData.append(data.southFace)
	if data.westFace is not None:
		faces.append((3, 2, 6, 7))
		faceData.append(data.westFace)
	if data.northFace is not None:
		faces.append((0, 3, 7, 4))
		faceData.append(data.northFace)

	mesh.from_pydata(verts, [], faces)
	uvLayers = mesh.uv_layers.new(name=data.name)

	for polygon in mesh.polygons:
		face = faceData[polygon.index]
		if face.texture in bpy.data.materials:
			material = bpy.data.materials[face.texture]
		else:
			material = bpy.data.materials.new(name=face.texture)
			material.use_nodes = True
			nodes = material.node_tree.nodes

			principled_BSDF = nodes.get('Principled BSDF')

			texture_node = nodes.new(type="ShaderNodeTexImage")
			texture_node.location = (-400, 0)

			textureLocation = ResourceLocation(data.textures.get(face.texture))
			if textureLocation.path.endswith(".png") is False:
				textureLocation.path += ".png"
			textureLocation.path = "textures/" + textureLocation.path
			texture = bpy.data.images.load(textureLocation.toPath(), check_existing=True)
			texture_node.image = texture
			texture_node.interpolation = "Closest"

			material.node_tree.links.new(texture_node.outputs[0], principled_BSDF.inputs[0])

		if mesh.materials.find(face.texture) == -1:
			mesh.materials.append(material)

		mat_idx = mesh.materials.find(face.texture)
		if mat_idx != -1:
			polygon.material_index = mat_idx

		fullUV = face.uv

		index = 0
		for vert_idx, loop_idx in zip(polygon.vertices, polygon.loop_indices):
			if face.rotation == 90: vertOrder = [1, 2, 3, 0]
			elif face.rotation == 180: vertOrder = [2, 3, 0, 1]
			elif face.rotation == 270: vertOrder = [3, 0, 1, 2]
			else: vertOrder = [0, 1, 2, 3]

			if index == vertOrder[0]: uv = (fullUV[0], fullUV[1])
			elif index == vertOrder[1]: uv = (fullUV[2], fullUV[1])
			elif index == vertOrder[2]: uv = (fullUV[2], fullUV[3])
			elif index == vertOrder[3]: uv = (fullUV[0], fullUV[3])
			index += 1

			uv = (uv[0] / 16, -(uv[1] / 16) + 1)
			uvLayers.data[loop_idx].uv = uv


	obj.location = originPos-Vector((8, 8, 0))
	obj.rotation_euler = data.rotation
	obj.rotation_quaternion = data.rotation.to_quaternion()
	return obj