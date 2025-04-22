import cv2


class Camera():
	"""
	Camera class used to abstract access to webcam through opencv.
	"""
	def __init__(self):
		"""
		Initialise Camera instance.
		"""

		# get camera feed
		self.cam = cv2.VideoCapture(0)

		# TODO: should I use enum here?
		self.prop_map = {
			"AUTOFOCUS": cv2.CAP_PROP_AUTOFOCUS,
			"FOCUS": cv2.CAP_PROP_FOCUS,
			"BRIGHTNESS": cv2.CAP_PROP_BRIGHTNESS
		}

	def set_cam_prop(self, prop, val):
		"""
		Set the camera setting (prop) to the given value (val).

		Args:
			prop (str): The setting to be changed, e.g. "BRIGHTNESS".
			val (int): The value to change the setting to.
		"""
		
		# TODO: throw error if unsupported prop passed in, for get function as well
		self.cam.set(self.prop_map[prop], val)

	def get_cam_prop(self, prop):
		"""
		Get the current value of the camera setting (prop).

		Args:
			prop (str): The setting to be accessed, e.g. "BRIGHTNESS".
		"""

		self.cam.get(self.prop_map[prop])

	def read(self):
		"""
		Get a frame from the camera.

		Returns:
			MatLike: An image/frame pulled from the webcam.
		"""

		ret, frame = self.cam.read()
		# TODO: should throw error if ret is false
		return frame
	
	def release(self):
		"""
		Release the camera resource.
		"""

		self.cam.release()