import cv2

# class for storing card information, could make cards persistent between
# frames later
class CardPrediction:
	def __init__(self, id, position, left, right, top, bottom, class_id, suit_rank, confidence):
		self.id = id
		self.position = position
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.class_id = class_id
		self.suit_rank = suit_rank
		self.confidence = confidence
		self.hand = -1


	def draw(self, frame):
		cv2.rectangle(frame, 
				 	  (self.left, self.top),
					  (self.right, self.bottom), 
					  (0, 255, 0), 
					  1)
		cv2.circle(frame,
				   self.position,
				   3,
				   (0, 255, 0),
				   -1)
		cv2.putText(frame, 
					f"[{self.id}]{self.suit_rank}({self.hand}): {100*self.confidence:.2f}%", 
					(self.left, self.top - 30), 
					cv2.FONT_HERSHEY_SIMPLEX, 
					0.5, 
					(0, 255, 0), 
					1, 
					cv2.LINE_AA)