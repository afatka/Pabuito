'''
AutoProFinder

This script identifies certain aspects of the professionalism expectations at 
Full Sail University. It utilizes the same automation scripts as the 
Pabuito Grading System. 

author: Adam Fatka 
E-mail: adam.fatka@gmail.com

'''

#import maya commands
import maya.cmds as cmds

#import utiliies
#TO DO - IMPORT UTILITIES

#TO DO - define main class
class MainAutoProFinder(object):

	def __init__(self):
		'''Initialize MainAutoProFinder class'''
		self.development = True

		self.window_width_height = (325, 800)
		self.attach_lst = []

		#TO DO - validate window exist
		#if window exists delete it
		if( cmds.window('AutoProFinder_Utilities', exist = True)):
			cmds.deleteUI('AutoProFinder_Utilities')

		#if preferences exist, delete them
		if self.development:
			if(cmds.widowPref('AutoProFinder_Utilities', exists = True)):
				cmds.windowPref('AutoProFinder_Utilities', remove = True)

		#TO DO - create window
		self.main_window = cmds.window('AutoProFinder_Utilities', 
				title = 'Auto Pro Finder', 
				widthHeight = self.window_width_height)
		cmds.formLayout('rootForm', 
				numberOfDivisions = self.window_width_height[0])

		self.init_btn = cmds.button(label = 'Initialize', 
				command = self.initialize)
		self.attach_lst.append(self.init_btn)


	def initialize(self):
		'''Initialize Tool'''












#TO DO - define row GUI class
class AutoProFinderRow(object):

	def __init__(self):
		'''Initialize AutoProFinderRow'''

		self.root_layout = cmds.formLayout()

class AutoProFinderUtilities(object):

	def __init__(self):
		'''Initialize Auto Pro Finder Utilities'''

#TO DO - define automation class (functions and options)

