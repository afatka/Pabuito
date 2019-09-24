#! usr/bin/env python3

#install Pabuito Shelf Icons - do make pretty
import os.path
import maya.cmds as cmds
import maya.mel as mel
def install_pabuito():
	icon_dir = os.path.dirname(__file__)
	shelfTabLayout = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
	shelves = cmds.tabLayout(shelfTabLayout, query = True, childArray = True)
	for shelf in shelves:
	    if cmds.shelfLayout(shelf, query = True, visible = True):
	        parentShelf = shelf
	shelfBtns = cmds.shelfLayout(parentShelf, query = True, childArray = True)

	for btn in shelfBtns:
	    cmd = cmds.shelfButton(btn, query = True, command = True)
	    print cmd
	    if '#pabuito shelf maker' in cmd:
	    	cmds.shelfButton(btn, edit = True, image1 = os.path.join(icon_dir, 'icons', 'psm.png'))
	    if '#Pabuito Pickle Loader' in cmd:
	    	cmds.shelfButton(btn, edit = True, image1 = os.path.join(icon_dir, 'icons', 'ppl.png'))
	    if 'install_pabuito' in cmd:
	        cmds.shelfButton(btn, edit = True, visible = False)

def delete_install_pabuito():
	shelfTabLayout = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;") 
	shelves = cmds.tabLayout(shelfTabLayout, query = True, childArray = True)
	for shelf in shelves:
	    if cmds.shelfLayout(shelf, query = True, visible = True):
	        parentShelf = shelf
	shelfBtns = cmds.shelfLayout(parentShelf, query = True, childArray = True)
	for btn in shelfBtns:
	    cmd = cmds.shelfButton(btn, query = True, command = True)
	    if 'install_pabuito' in cmd:
	        cmds.deleteUI(btn)
