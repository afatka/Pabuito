'''
Timer class: 
Designed to work in the python 'with as' keywords. when bundled around code will tell you how long it takes to run them
'''
import time
class codeTimer(object):

	def __init__(self, message, development = False, prefix = '-Timer-', *args):
		self.development = development
		self.prefix = prefix
		self.message = message

	def __enter__(self, *args):
		self.start_time = time.time()
		return self

	def __exit__(self, *args):
		self.end_time = time.time()
		self.duration_sec = self.end_time - self.start_time
		self.duration_ms = self.duration_sec * 1000 #Milliseconds
		if self.development:
			print ('{} {} : elapsed time: {}ms'.format(self.prefix, self.message, self.duration_ms))
