import math

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler


class FaceData:
	uv: list[float]
	texture: str
	rotation: int

	def __init__(self, uv: list[float], texture: str, rotation: int):
		self.uv = uv
		self.texture = texture
		self.rotation = rotation


class CubeData:
	name: str
	minPos: Vector
	maxPos: Vector
	originPos: Vector
	rotation: Euler
	northFace: FaceData
	southFace: FaceData
	eastFace: FaceData
	westFace: FaceData
	upFace: FaceData
	downFace: FaceData

	def __init__(self, name: str, minPos: Vector, maxPos: Vector, originPos: Vector, rotation: Euler,
				 northFace: FaceData, southFace: FaceData, eastFace: FaceData, westFace: FaceData, upFace: FaceData, downFace: FaceData):
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
	faces = [
		# up
		(2, 3, 0, 1),
		# down
		(4, 7, 6, 5),
		# right
		(5, 1, 0, 4),
		# back
		(6, 2, 1, 5),
		# left
		(7, 3, 2, 6),
		# front
		(4, 0, 3, 7)
	]
	mesh.from_pydata(verts, [], faces)
	uvLayers = mesh.uv_layers.new(name=data.name)

	for polygon in mesh.polygons:
		face: FaceData
		if polygon.index == 0: face = data.upFace
		elif polygon.index == 1: face = data.downFace
		elif polygon.index == 2: face = data.eastFace
		elif polygon.index == 3: face = data.southFace
		elif polygon.index == 4: face = data.westFace
		else: face = data.northFace

		if face.texture in bpy.data.materials:
			material = bpy.data.materials[face.texture]
		else:
			material = bpy.data.materials.new(name=face.texture)

		if mesh.materials.find(face.texture) == -1:
			mesh.materials.append(material)

		mat_idx = mesh.materials.find(face.texture)
		if mat_idx != -1:
			polygon.material_index = mat_idx

		fullUV = face.uv

		index = 0
		for vert_idx, loop_idx in zip(polygon.vertices, polygon.loop_indices):
			if face.rotation == 90: vertOrder = [0, 1, 2, 3]
			elif face.rotation == 180: vertOrder = [1, 2, 3, 0]
			elif face.rotation == 270: vertOrder = [2, 3, 0, 1]
			else: vertOrder = [3, 0, 1, 2]

			if polygon.index == 1: vertOrder = [vertOrder[3], vertOrder[0], vertOrder[1], vertOrder[2]]
			else: vertOrder = [vertOrder[2], vertOrder[3], vertOrder[0], vertOrder[1]]

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