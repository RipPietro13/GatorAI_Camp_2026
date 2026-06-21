import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice
import os

class SoilTile(pygame.sprite.Sprite):
	"""A single tilled-soil tile drawn on the soil layer."""
	def __init__(self, pos, surf, groups):
		"""Place the soil tile image at `pos`."""
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
	"""A watered-soil overlay tile drawn above plain soil."""
	def __init__(self, pos, surf, groups):
		"""Place the water-overlay image at `pos`."""
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
	"""A growing crop that ages while watered and becomes harvestable when mature."""
	def __init__(self, plant_type, groups, soil, check_watered):
		"""Set up the plant's frames, growth speed, and starting (seed) image."""
		super().__init__(groups)

		# setup
		self.plant_type = plant_type
		base_path = os.path.dirname(os.path.abspath(__file__))
		self.frames = import_folder(os.path.join(base_path, 'graphics/fruit', plant_type))
		self.soil = soil
		self.check_watered = check_watered

		# plant growing 
		self.age = 0
		self.max_age = len(self.frames) - 1
		self.grow_speed = GROW_SPEED[plant_type]  # Set grow speed based on plant type
		self.harvestable = False

		# sprite setup
		self.image = self.frames[self.age]
		self.y_offset = -16 if plant_type == 'corn' else -8
		self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))
		self.z = LAYERS['ground plant']

	def grow(self, dt):
		"""Age the plant while its soil is watered; mark harvestable when fully grown."""
		if self.check_watered(self.rect.center):
			self.age += self.grow_speed * dt  # Increment age by grow speed multiplied by delta time

			if int(self.age) > 0:
				self.z = LAYERS['main']
				self.hitbox = self.rect.copy().inflate(-26,-self.rect.height * 0.4)

			if self.age >= self.max_age:
				self.age = self.max_age
				self.harvestable = True

			self.image = self.frames[int(self.age)]
			self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pygame.math.Vector2(0,self.y_offset))

class SoilLayer:
	"""Manages the farmable grid: tilling, watering, planting, and plant growth."""
	def __init__(self, all_sprites, collision_sprites):
		"""Set up the soil/water/plant groups, load graphics, and build the grid."""
		# sprite groups
		self.all_sprites = all_sprites
		self.collision_sprites = collision_sprites
		self.soil_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.plant_sprites = pygame.sprite.Group()

		# graphics
		self.soil_surfs = import_folder_dict('graphics/soil/')
		self.water_surfs = import_folder('graphics/soil_water')

		self.create_soil_grid()
		self.create_hit_rects()

		# sounds
		base_path = os.path.dirname(os.path.abspath(__file__))
		self.hoe_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio/hoe.wav'))
		self.hoe_sound.set_volume(0.1)

		self.plant_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio/plant.wav')) 
		self.plant_sound.set_volume(0.2)

	def create_soil_grid(self):
		"""Build a 2D grid and mark farmable cells ('F') from the map's Farmable layer."""
		ground = pygame.image.load('graphics/world/ground.png')
		h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
		
		self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
		for x, y, _ in load_pygame('data/map.tmx').get_layer_by_name('Farmable').tiles():
			self.grid[y][x].append('F')

	def create_hit_rects(self):
		"""Make a clickable rect for every farmable cell (used by the hoe)."""
		self.hit_rects = []
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'F' in cell:
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					rect = pygame.Rect(x,y,TILE_SIZE, TILE_SIZE)
					self.hit_rects.append(rect)

	def get_hit(self, point):
		"""Till the farmable tile at `point` (mark 'X' and create soil tiles)."""
		for rect in self.hit_rects:
			if rect.collidepoint(point):
				self.hoe_sound.play()

				x = rect.x // TILE_SIZE
				y = rect.y // TILE_SIZE

				if 'F' in self.grid[y][x]:
					self.grid[y][x].append('X')
					self.create_soil_tiles()
					if self.raining:
						self.water_all()

	def water(self, target_pos):
		"""Water the tilled soil tile at `target_pos` (mark 'W' and add a water tile)."""
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):

				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE
				self.grid[y][x].append('W')

				pos = soil_sprite.rect.topleft
				surf = choice(self.water_surfs)
				WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

	def water_all(self):
		"""Water every tilled tile at once (used when it rains)."""
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell and 'W' not in cell:
					cell.append('W')
					x = index_col * TILE_SIZE
					y = index_row * TILE_SIZE
					WaterTile((x,y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])

	def remove_water(self):
		"""Dry out all soil: remove water tiles and clear 'W' from the grid (new day)."""
		# destroy all water sprites
		for sprite in self.water_sprites.sprites():
			sprite.kill()

		# clean up the grid
		for row in self.grid:
			for cell in row:
				if 'W' in cell:
					cell.remove('W')

	def check_watered(self, pos):
		"""Return True if the soil cell at `pos` is watered."""
		x = pos[0] // TILE_SIZE
		y = pos[1] // TILE_SIZE
		cell = self.grid[y][x]
		is_watered = 'W' in cell
		return is_watered

	def plant_seed(self, target_pos, seed):
		"""Plant a `seed` on the tilled tile at `target_pos` if it isn't already planted."""
		for soil_sprite in self.soil_sprites.sprites():
			if soil_sprite.rect.collidepoint(target_pos):
				self.plant_sound.play()

				x = soil_sprite.rect.x // TILE_SIZE
				y = soil_sprite.rect.y // TILE_SIZE

				if 'P' not in self.grid[y][x]:
					self.grid[y][x].append('P')
					Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

	def update_plants(self, dt=None):
		"""Grow all plants. With no `dt` (sleeping), advance a full day; else by `dt`."""
		# When the player sleeps, reset() calls this with no dt to advance
		# every plant by a full day's worth of growth. During normal gameplay
		# the Level passes the per-frame delta time so plants grow gradually.
		grow_amount = dt if dt is not None else DAY_GROWTH
		for plant in self.plant_sprites.sprites():
			plant.grow(grow_amount)

	def create_soil_tiles(self):
		"""Rebuild all soil tile sprites, choosing each tile's edge variant from neighbors."""
		self.soil_sprites.empty()
		for index_row, row in enumerate(self.grid):
			for index_col, cell in enumerate(row):
				if 'X' in cell:
					
					# tile options 
					t = 'X' in self.grid[index_row - 1][index_col]
					b = 'X' in self.grid[index_row + 1][index_col]
					r = 'X' in row[index_col + 1]
					l = 'X' in row[index_col - 1]

					tile_type = 'o'

					# all sides
					if all((t,r,b,l)): tile_type = 'x'

					# horizontal tiles only
					if l and not any((t,r,b)): tile_type = 'r'
					if r and not any((t,l,b)): tile_type = 'l'
					if r and l and not any((t,b)): tile_type = 'lr'

					# vertical only 
					if t and not any((r,l,b)): tile_type = 'b'
					if b and not any((r,l,t)): tile_type = 't'
					if b and t and not any((r,l)): tile_type = 'tb'

					# corners 
					if l and b and not any((t,r)): tile_type = 'tr'
					if r and b and not any((t,l)): tile_type = 'tl'
					if l and t and not any((b,r)): tile_type = 'br'
					if r and t and not any((b,l)): tile_type = 'bl'

					# T shapes
					if all((t,b,r)) and not l: tile_type = 'tbr'
					if all((t,b,l)) and not r: tile_type = 'tbl'
					if all((l,r,t)) and not b: tile_type = 'lrb'
					if all((l,r,b)) and not t: tile_type = 'lrt'

					SoilTile(
						pos = (index_col * TILE_SIZE,index_row * TILE_SIZE), 
						surf = self.soil_surfs[tile_type], 
						groups = [self.all_sprites, self.soil_sprites])