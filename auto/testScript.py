"""
Pabuito Auto Script

Test Script

This script contains a test auto script for the Pabuito Grade Tool.

!!!
All scripts need to create a progress bar and print status to stdout
!!!
All auto scripts need to return the grade information in the form of a dictionary

return {
		'grade_value': int, 
		'comment_text':string,
		'default_comments_text':string,
		'example_comments_text':string,
		}

the comments can remain '' without effecting the tools functionality. 

Written by: Adam Fatka
adam.fatka@gmail.com
www.fatkaforce.com

"""

import maya.cmds as cmds
def testScript():
	print "Test Script"
	
	import maya.mel
	gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

	cmds.progressBar( gMainProgressBar,
					edit=True,
					beginProgress=True,
					isInterruptable=True,
					status='Test Script',
					maxValue=100 )


	cmds.progressBar(gMainProgressBar, edit=True, step=50)



	print "Test Auto Script Successful!"
	tempDict = {
				'grade_value':92,
				'comment_text':'Auto Success!',
				'default_comments_text':'stuff',
				'example_comments_text':'things!'}
	cmds.progressBar(gMainProgressBar, edit=True, step=50)
	
	
	cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
	return tempDict







	# #if the window exists delete it
	# if (cmds.window('Test Script Auto',exists = True)):
	# 	cmds.deleteUI('Test Script Auto')
	# #if the preferences exist, delete them
	# if (cmds.windowPref('Test Script Auto',exists=True)):
	# 	cmds.windowPref('Test Script Auto', remove=True)


	# progressWindow = cmds.window('Test Script Auto')
	# cmds.columnLayout()

	# progressControl = cmds.progressBar(maxValue=10, width=300)
	# cmds.showWindow( 'Test Script Auto' )

	# cmds.progressBar(progressControl, edit=True, step=5)
	# print "Window Creating; exporting grade"
	# cmds.progressBar(progressControl, edit=True, step=5)
	# gradeValueInput = raw_input('whats the number?')
	
	# print "Test Auto Script Successful!"
	# tempDict = {
	# 			'grade_value':int(gradeValueInput),
	# 			'comment_text':'Auto Success!',
	# 			'default_comments_text':'blahblah',
	# 			'example_comments_text':'Yippe!'}
	# print "Did it work?"
	
	
	# if (cmds.window('Test Script Auto',exists = True)):
	# 	cmds.deleteUI('Test Script Auto')
	# return tempDict

