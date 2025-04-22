from PIL import Image, ImageTk


def load_sprites(atlas_path):
	"""
	Load the sprites into a dictionary when given the path to .txt file written in specific format.

	Args:
		atlas_path (str): Path to the sprite atlas .txt file.

	Returns:
		dict[str, ImageTk.PhotoImage]: A dictionary of (sprite name, image).
	"""

	# get directory that atlas is in
	dir_path = atlas_path[:atlas_path.rfind("/") + 1]

	sprites = {}
	with open("./res/sprites/atlas.txt", "r") as file:
		for line in file:
			line = line.strip()

			if line == "":
				continue

			# ignore comments
			elif line[0] == "#":
				continue
			
			# look for spritemaps
			elif line[0] == "S":
				sheet_name = line[2:]
				sheet_image = Image.open(dir_path + sheet_name)

			# look for sprites
			elif line[0] == "s":
				name, x1, y1, w, h = line[2:].split(",")
				x1, y1, w, h = int(x1), int(y1), int(w), int(h)
				img = ImageTk.PhotoImage(sheet_image.crop((x1, y1, x1+w, y1+h)))
				sprites[name] = img

	return sprites