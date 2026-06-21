import pygame
from settings import *
from random import randint, choice
from timer import Timer
import os

class Generic(pygame.sprite.Sprite):
	"""Base sprite: an image at a position on a draw layer, with a default hitbox."""
	def __init__(self, pos, surf, groups, z = LAYERS['main']):
		"""Place `surf` at `pos`, add to `groups`, and build a default hitbox."""
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = z
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Interaction(Generic):
	"""An invisible, named trigger zone (e.g. the Bed or Trader spot)."""
	def __init__(self, pos, size, groups, name):
		"""Create a `size`-sized invisible zone named `name`."""
		surf = pygame.Surface(size)
		super().__init__(pos, surf, groups)
		self.name = name

class Water(Generic):
	"""An animated water tile that cycles through its frames."""
	def __init__(self, pos, frames, groups):
		"""Set up the water animation frames and show the first one."""
		#animation setup
		self.frames = frames
		self.frame_index = 0

		# sprite setup
		super().__init__(
				pos = pos, 
				surf = self.frames[self.frame_index], 
				groups = groups, 
				z = LAYERS['water']) 

	def animate(self,dt):
		"""Advance to the next water frame, looping at the end."""
		self.frame_index += 5 * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self,dt):
		"""Per-frame update: animate the water."""
		self.animate(dt)

class WildFlower(Generic):
	"""A decorative flower/bush that also blocks movement."""
	def __init__(self, pos, surf, groups):
		"""Place the flower and shrink its hitbox so the player can stand close."""
		super().__init__(pos, surf, groups)
		self.hitbox = self.rect.copy().inflate(-20,-self.rect.height * 0.9)

class Particle(Generic):
	"""A short-lived white flash sprite (used for harvest/chop effects)."""
	def __init__(self, pos, surf, groups, z, duration = 200):
		"""Create a white silhouette of `surf` that disappears after `duration` ms."""
		super().__init__(pos, surf, groups, z)
		self.start_time = pygame.time.get_ticks()
		self.duration = duration

		# white surface 
		mask_surf = pygame.mask.from_surface(self.image)
		new_surf = mask_surf.to_surface()
		new_surf.set_colorkey((0,0,0))
		self.image = new_surf

	def update(self,dt):
		"""Remove the particle once its lifetime has passed."""
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time > self.duration:
			self.kill()

class Tree(Generic):
	"""A choppable tree that drops apples, then wood, and leaves a stump."""
	def __init__(self, pos, surf, groups, name, player_add):
		"""Set up the tree's health, stump image, apples, and chop sound."""
		super().__init__(pos, surf, groups)

		# tree attributes
		self.health = 5
		self.alive = True
		base_path = os.path.dirname(os.path.abspath(__file__))
		stump_path = os.path.join(base_path, 'graphics/stumps', 'small.png' if name == 'Small' else 'large.png')
		self.stump_surf = pygame.image.load(stump_path).convert_alpha()

		# apples
		self.apple_surf = pygame.image.load(os.path.join(base_path, 'graphics/fruit/apple.png'))
		self.apple_pos = APPLE_POS[name]
		self.apple_sprites = pygame.sprite.Group()
		self.create_fruit()

		self.player_add = player_add

		# sounds
		self.axe_sound = pygame.mixer.Sound(os.path.join(base_path, 'audio/axe.mp3'))

	def damage(self):
		"""Take one hit: play a sound and drop one apple if any remain."""
		# damaging the tree
		self.health -= 1

		# play sound
		self.axe_sound.play()

		# remove an apple
		if len(self.apple_sprites.sprites()) > 0:
			random_apple = choice(self.apple_sprites.sprites())
			Particle(
				pos = random_apple.rect.topleft,
				surf = random_apple.image, 
				groups = self.groups()[0], 
				z = LAYERS['fruit'])
			self.player_add('apple')
			random_apple.kill()

	def check_death(self):
		"""If health is gone, replace the tree with a stump and give the player wood."""
		if self.health <= 0:
			Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 300)
			self.image = self.stump_surf
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
			self.hitbox = self.rect.copy().inflate(-10,-self.rect.height * 0.6)
			self.alive = False
			self.player_add('wood')

	def update(self,dt):
		"""While alive, check whether the tree has been chopped down."""
		if self.alive:
			self.check_death()

	def create_fruit(self):
		"""Randomly place apples at this tree's apple positions."""
		for pos in self.apple_pos:
			if randint(0,10) < 2:
				x = pos[0] + self.rect.left
				y = pos[1] + self.rect.top
				Generic(
					pos = (x,y), 
					surf = self.apple_surf, 
					groups = [self.apple_sprites,self.groups()[0]],
					z = LAYERS['fruit'])

class NPC(Generic):
	"""A talkable character with a name and a list of dialogue lines (from NPC_DATA)."""
	def __init__(self, pos, surf, name, dialogue, groups):
		"""Store the NPC's name and dialogue, and set an interaction hitbox."""
		super().__init__(pos, surf, groups)
		self.name = name
		self.dialogue = dialogue
		# Setup a hitbox for collisions and interaction range
		self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.2)