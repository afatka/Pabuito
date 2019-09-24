"""Pabuito Grading System
Maya Shelf Button Creator

Created by Adam  Fatka : 2015 : adam.fatka@gmail.com
"""

import maya.cmds as cmds
import maya.mel as mel
import os.path

class PabuitoShelfMaker(object):

	def __init__(self):
		self.development = True

	def __enter__(self):
		# print('file: {}'.format(__file__))
		# print('dirname: {}'.format(os.path.dirname(__file__)))
		# print('icon path: {}'.format(os.path.join(os.path.dirname(__file__), 'icons', 'pgs.png')))
		shelfTabLayout = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
		shelves = cmds.tabLayout(shelfTabLayout, query = True, childArray = True)
		for shelf in shelves:
			if cmds.shelfLayout(shelf, query = True, visible = True):
				parentShelf = shelf

		icon_count = 1
		shelfBtns = cmds.shelfLayout(parentShelf, query = True, childArray = True)
		for btn in shelfBtns:
		    cmd = cmds.shelfButton(btn, query = True, command = True)
		    if 'pgs.PabuitoGradingSystem(\'' in cmd:
		        icon_count += 1


		xmlFile = cmds.fileDialog2(caption = 'Please select project xml', fileMode = 1, fileFilter = "XML (*.xml)")[0]
		annotation = 'PGS Tool - ' + str(xmlFile.rsplit('/', 1)[-1].rsplit('.',1)[0])
		commandBlock = "from pabuito import pabuitoGradingSystem as pgs\nimport maya.cmds as cmds\npgsGUI = pgs.PabuitoGradingSystem('{}')".format(xmlFile)
		
		icon = os.path.join(os.path.dirname(__file__), 'icons', 'pgs_{:02d}.png'.format(icon_count))
		if not os.path.isfile(icon):
			icon = os.path.join(os.path.dirname(__file__), 'icons', 'pgs.png')

		cmds.shelfButton( parent = parentShelf, annotation = annotation, image1 =icon, command = commandBlock, sourceType = 'python' )

		shelfDirectory = cmds.internalVar(userShelfDir = True) + 'shelf_PGS'
		cmds.saveShelf(parentShelf, shelfDirectory)

		return self


	def __exit__(self, *args):
		self.log('exit')
		# for arg in args:
		# 	self.log(arg)

	def log(self, message, prefix = 'Pabuito Shelf Maker - '):
		if self.development:
			print ('{}{}'.format(prefix, message))




