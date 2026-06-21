from os import walk, path
import pygame

def import_folder(folder_path):
	"""Load every image in a folder and return them as a list of surfaces."""
	surface_list = []
	base_path = path.dirname(path.abspath(__file__))

	for _, __, img_files in walk(path.join(base_path, folder_path)):
		for image in img_files:
			full_path = path.join(base_path, folder_path, image)
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list

def import_folder_dict(folder_path):
	"""Load every image in a folder into a dict keyed by filename (without extension)."""
	surface_dict = {}
	base_path = path.dirname(path.abspath(__file__))

	for _, __, img_files in walk(path.join(base_path, folder_path)):
		for image in img_files:
			full_path = path.join(base_path, folder_path, image)
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image.split('.')[0]] = image_surf

	return surface_dict