import json

def load(filepath: str):
	jsonData = json.load(open(filepath, "r", encoding='utf-8'))
	return JsonElement(jsonData)

class JsonElement:
	def __init__(self, json_data):
		self.data = json_data

	def isObject(self):
		return isinstance(self.data, dict)

	def asObject(self):
		if self.isObject():
			return JsonObject(self.data)
		return JsonObject({})

	def isArray(self):
		return isinstance(self.data, list)

	def asArray(self):
		if self.isArray():
			return JsonArray(self.data)
		return JsonArray([])

	def isString(self):
		return isinstance(self.data, str)

	def asString(self, default: str = ""):
		if self.isString():
			return str(self.data)
		return default

	def isInteger(self):
		return isinstance(self.data, int)

	def asInteger(self, default: int = 0):
		if self.isInteger():
			return int(self.data)
		if self.isFloat():
			return int(self.data)
		return default

	def isFloat(self):
		return isinstance(self.data, float)

	def asFloat(self, default: float = 0):
		if self.isInteger():
			return float(self.data)
		if self.isFloat():
			return float(self.data)
		return default

	def isBool(self):
		return self.data is bool

	def asBool(self, default: bool = False):
		if self.isFloat():
			return bool(self.data)
		return default


class JsonObject(JsonElement):
	data: dict[str, JsonElement]

	def has(self, name: str):
		return name in self.data

	def get(self, name: str):
		if self.has(name):
			return JsonElement(self.data[name])
		return JsonElement({})

class JsonArray(JsonElement):
	data: list[JsonElement]

	def __init__(self, json_data: list):
		children: list[JsonElement] = []
		for element in json_data:
			children.append(JsonElement(element))
		super().__init__(children)

	def length(self):
		return len(self.data)

	def get(self, index: int):
		return self.data[index]

	def asList(self):
		return self.data
