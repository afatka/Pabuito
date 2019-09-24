#! /usr/bin/env python
#install Pabuito

import maya.cmds as cmds
import maya.mel as mel
import os
def install():

	#ask the user to install pabuito on the active shelf or a new shelf
	install_type = cmds.confirmDialog( 
		title='Install Pabuito', 
		message='Install to active shelf or new shelf?', 
		button=['Active','New'], 
		defaultButton='New', 
		cancelButton='New', 
		dismissString='New' )

	icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
	parent_shelfTabLayout = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
	shelves = cmds.tabLayout(parent_shelfTabLayout, query = True, childArray = True)
	if install_type == 'Active':
		for shelf in shelves:
		    if cmds.shelfLayout(shelf, query = True, visible = True):
		        install_shelf = shelf
	if install_type == 'New':
		install_shelf = 'PGS'
		i = 1 
		while True:
			if install_shelf not in shelves:
				break
			else: 
				install_shelf = 'PGS' + str(i)
				i += 1
		cmds.shelfLayout(install_shelf, parent = parent_shelfTabLayout)

	#Pabuito shelf maker button
	cmds.shelfButton(parent = install_shelf,
		annotation = 'Pabtuito Shelf Maker', 
		image1 = os.path.join(icon_dir, 'psm.png'),
		command = """
#pabuito shelf maker
from pabuito import pabuitoShelfMaker as psm
reload(psm)

with psm.PabuitoShelfMaker() as psm:
	print 'PSM Running'
		""",
		sourceType = 'python', 
		label = 'PSM'
		)

	#Pabuito Pickle Loader Button
	cmds.shelfButton(parent = install_shelf,
		annotation = 'Pabuito Pickle Loader', 
		image1 = os.path.join(icon_dir, 'ppl.png'),
		command = """
#Pabuito Pickle Loader
import maya.cmds as cmds
PGSFile = cmds.fileDialog2(caption = 'Please select project file', fileMode = 1, fileFilter = "PGS (*.pgs)")[0]

from pabuito import pabuitoGradingSystem as pgs
pgsGUI = pgs.PabuitoGradingSystem(PGSFile)
		""",
		sourceType = 'python',
		label = 'PPL'
		)


	shelfDirectory = cmds.internalVar(userShelfDir = True) + 'shelf_' + install_shelf
	cmds.saveShelf(install_shelf, shelfDirectory)

	cmds.confirmDialog( 
		title='Install Complete', 
		message='Pabuito Install Complete!', 
		button=['Awesome'] )

	#this is a fix for a Maya issue 'provided' from Gary Fixler > in the comments MAR 2012
	# http://www.nkoubi.com/blog/tutorial/how-to-create-a-dynamic-shelf-plugin-for-maya/
	
	topLevelShelf = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
	shelves = cmds.shelfTabLayout(topLevelShelf, query=True, tabLabelIndex=True)
	for index, shelf in enumerate(shelves):
		cmds.optionVar(stringValue=('shelfName%d' % (index+1), str(shelf)))


install()
		