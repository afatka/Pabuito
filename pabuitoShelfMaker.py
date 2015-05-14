"""Pabuito Grading System
Maya Shelf Button Creator

Created by Adam  Fatka : 2015 : adam.fatka@gmail.com
"""

import maya.cmds as cmds
import maya.mel as mel

class PabuitoShelfMaker(object):

	def __init__(self):
		self.development = True

	def __enter__(self):
		shelfTabLayout = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
		shelves = cmds.tabLayout(shelfTabLayout, query = True, childArray = True)
		for shelf in shelves:
			if cmds.shelfLayout(shelf, query = True, visible = True):
				parentShelf = shelf

		xmlFile = cmds.fileDialog2(caption = 'Please select project xml', fileMode = 1, fileFilter = "XML (*.xml)")[0]
		annotation = 'PGS Tool - ' + str(xmlFile.rsplit('/', 1)[-1].rsplit('.',1)[0])
		commandBlock = "from pabuito import pabuitoGradingSystem as pgs\nimport maya.cmds as cmds\npgsGUI = pgs.PabuitoGradingSystem('{}')".format(xmlFile)

		# cmds.shelfButton( parent = parentShelf, annotation = annotation, image1 ='../../../scripts/pabuito/icons/pgs_blank.png', command = commandBlock, label = '1', style = 'iconAndTextVertical', font = 'smallObliqueLabelFont', sourceType = 'python' )
		cmds.shelfButton( parent = parentShelf, annotation = annotation, image1 ='../../../scripts/pabuito/icons/pgs.png', command = commandBlock, sourceType = 'python' )

		return self

		# commandBlock = "from pabuito import pabuitoGradingSystem as pgs\nimport maya.cmds as cmds\npgsGUI = pgs.PabuitoGradingSystem({})".format(xmlFile)

	def __exit__(self, *args):
		self.log('exit')
		for arg in args:
			self.log(arg)

	def log(self, message, prefix = 'Pabuito Shelf Maker - '):
		if self.development:
			print ('{}{}'.format(prefix, message))

