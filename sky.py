import pygame 
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky:
	"""Tints the screen over time to simulate a day/night cycle."""
	def __init__(self):
		"""Set up the full-screen tint surface and the day/night color cycle."""
		self.display_surface = pygame.display.get_surface()
		self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.start_color = [255, 255, 255]
		self.end_color = (38, 101, 189)
		self.cycle_duration = 300  # Duration of the day/night cycle in seconds (e.g., 5 minutes)
		self.elapsed_time = 0
		self.phase = 'day_to_night'  # Initial phase

	def update(self, dt):
		"""Advance the day/night cycle, easing the tint toward day or night color."""
		self.elapsed_time += dt
		progress = min(self.elapsed_time / self.cycle_duration, 1)

		if self.phase == 'day_to_night':
			for index, value in enumerate(self.end_color):
				self.start_color[index] = max(value, 255 - (255 - value) * progress)
			if progress >= 1:
				self.phase = 'night_to_day'
				self.elapsed_time = 0
		elif self.phase == 'night_to_day':
			for index, value in enumerate(self.end_color):
				self.start_color[index] = min(255, value + (255 - value) * progress)
			if progress >= 1:
				self.phase = 'day_to_night'
				self.elapsed_time = 0

	def display(self):
		"""Multiply the current sky color over the screen."""
		self.full_surf.fill(self.start_color)
		self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class Drop(Generic):
	"""A single rain drop (or floor splash) that disappears after a short lifetime."""
	def __init__(self, surf, pos, moving, groups, z):
		"""Create a drop; if `moving`, give it a downward velocity."""
		# general setup
		super().__init__(pos, surf, groups, z)
		self.lifetime = randint(400,500)
		self.start_time = pygame.time.get_ticks()

		# moving 
		self.moving = moving
		if self.moving:
			self.pos = pygame.math.Vector2(self.rect.topleft)
			self.direction = pygame.math.Vector2(-2,4)
			self.speed = randint(200,250)

	def update(self,dt):
		"""Move the drop (if moving) and remove it once its lifetime expires."""
		# movement
		if self.moving:
			self.pos += self.direction * self.speed * dt
			self.rect.topleft = (round(self.pos.x), round(self.pos.y))

		# timer
		if pygame.time.get_ticks() - self.start_time >= self.lifetime:
			self.kill()

class Rain:
	"""Spawns falling rain drops and floor splashes each frame while it's raining."""
	def __init__(self, all_sprites):
		"""Load the drop/floor images and the map size for random placement."""
		self.all_sprites = all_sprites
		self.rain_drops = import_folder('./graphics/rain/drops/')
		self.rain_floor = import_folder('./graphics/rain/floor/')
		self.floor_w, self.floor_h =  pygame.image.load('./graphics/world/ground.png').get_size()

	def create_floor(self):
		"""Spawn one stationary floor splash at a random spot."""
		Drop(
			surf = choice(self.rain_floor),
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = False, 
			groups = self.all_sprites, 
			z = LAYERS['rain floor'])

	def create_drops(self):
		"""Spawn one moving rain drop at a random spot."""
		Drop(
			surf = choice(self.rain_drops),
			pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
			moving = True, 
			groups = self.all_sprites, 
			z = LAYERS['rain drops'])

	def update(self):
		"""Spawn a floor splash and a rain drop for this frame."""
		self.create_floor()
		self.create_drops()