import cv2


class Camera():
	def __init__(self):
		# get camera feed
		self.cam = cv2.VideoCapture(0)

		# TODO: should I use enum here?
		self.prop_map = {
			"AUTOFOCUS": cv2.CAP_PROP_AUTOFOCUS,
			"FOCUS": cv2.CAP_PROP_FOCUS,
			"BRIGHTNESS": cv2.CAP_PROP_BRIGHTNESS
		}

	# TODO: throw error if unsupported prop passed in, for get function as well
	def set_cam_prop(self, prop, val):
		self.cam.set(self.prop_map[prop], val)

	def get_cam_prop(self, prop):
		self.cam.get(self.prop_map[prop])

	def read(self):
		ret, frame = self.cam.read()
		# TODO: should throw error if ret is false
		return frame
	
	def release(self):
		self.cam.release()