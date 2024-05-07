import os
import zipfile

current_dir = os.path.dirname(__file__)
addon_directory = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

class ResourceLocation:
	namespace: str = "minecraft"
	path: str = ""

	def __init__(self, location: str):
		locationStrings = location.split(":")
		if len(locationStrings) > 1:
			self.namespace = locationStrings[0]
			self.path = locationStrings[1]
		elif len(locationStrings) == 1:
			self.path = locationStrings[0]

	def toString(self):
		return self.namespace + ":" + self.path

	def toPath(self):
		return os.path.join(addon_directory, "Assets/" + self.namespace + "/" + self.path)


def getResource(resourceLocation: ResourceLocation) -> bytes:
	archive = zipfile.ZipFile(addon_directory + "/Assets/1.20.4.jar", "r")
	return archive.open("assets/" + resourceLocation.namespace + "/" + resourceLocation.path).read()