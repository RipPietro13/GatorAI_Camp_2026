import pygame 

class Timer:
	"""A simple countdown timer; optionally calls `func` when it finishes."""
	def __init__(self,duration,func = None):
		"""Store the duration (ms) and optional callback; start inactive."""
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.active = False

	def activate(self):
		"""Start the timer from now."""
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		"""Stop and reset the timer."""
		self.active = False
		self.start_time = 0

	def update(self):
		"""Check if the duration has elapsed; if so, fire the callback and deactivate."""
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time >= self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.deactivate()