import pygame
from settings import *

class Transition:
	"""The fade-to-black-and-back effect played when the player sleeps."""
	def __init__(self, reset, player):
		"""Store the reset callback and player, and set up the fade overlay."""
		# setup
		self.display_surface = pygame.display.get_surface()
		self.reset = reset
		self.player = player

		# overlay image
		self.image = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.color = 255
		self.speed = -2

	def update(self):
		"""Darken to black (running reset at the bottom), then brighten back to day."""
		self.color += self.speed
		if self.color <= 0:
			self.speed *= -1
			self.color = 0
			self.reset()
		if self.color > 255:
			self.color = 255
			self.player.sleep = False
			self.speed = -2

	def display(self):
		"""Blend the current fade color over the screen."""
		self.image.fill((self.color,self.color,self.color))
		self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)