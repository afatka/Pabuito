"""
 This class controls the main window of the pabuito Grading System. It deals with tabbing the main sections as well as holding all the relavent information. 

"""
# Pabuito Version 1.0

import maya.cmds as cmds
import xml.etree.ElementTree as etree
from pabuito import cat_class as category_class
import pabuito.fileManager as fileManagerFile
#cPickle/Pickle deal with serializing the data for saving/loading
try:
	import cPickle as pickle
except:
	import pickle
#These deal with saving the pickle file/ making sure pickle file directory exists	
import os
import errno
import textwrap
import random
reload(category_class)
reload(fileManagerFile)


class PabuitoGradingSystem_HTML(object):

	def __init__(self, xmlFileLocation):

		self.development = False

		self.projectIncomplete = False

		self.fail_message = [
			('A PGS Section is not complete', 'Ok'),
			('You haven\'t completed the tool. Dummy', 'Ok'),
			('Please finish grading before cycling to the next file', 'Ok'),
			('What a dingus...You\'re not finished yet', 'Ok'),
			('What did the error say?', 'I can read...'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			('A PGS Section is not complete', 'Ok'),
			]


		self.xmlFile = xmlFileLocation
		if xmlFileLocation.endswith('.xml'):
			self.log('xml is an xml \n\n')
			self.xml_elementTree = etree.ElementTree(file = self.xmlFile)
			self.loadedByPickle = False
		elif xmlFileLocation.endswith('.pgs'):
			self.log('PGS Pickle Detected! \n\n')
			self.unpackPickle(self.xmlFile)
		else:
			cmds.error('Unknown file type loaded.')

		self.xml_elementRoot = self.xml_elementTree.getroot()

		self.xml_elementDefaults = self.xml_elementRoot.find('defaults')
		self.xml_elementMainCategories = self.xml_elementRoot.findall('category')

		self.validateXML()
		# cmds.error('force stop')

		longestElement = 0
		for cat in self.xml_elementMainCategories:
			if len(cat.findall('subcategory')) > longestElement:
				longestElement = len(cat.findall('subcategory'))

		self.windowWidth = 350
		subcategoryHeight = 780
		windowBufferHeight = 55
		self.windowHeight = 825

		self.uiPadding = 2

		self.outputModel = 'root'
		if self.xml_elementDefaults.find('auto').text == 'True':
			self.log('Auto Defaults: True')
			self.runAuto = True
			autoLabel = 'RunAuto - On'
		else:
			self.log('Auto Defaults: False')
			self.runAuto = False
			autoLabel = 'RunAuto - Off'

		#if PGS window exists delete it
		if (cmds.window('PGS', exists = True)):
			cmds.deleteUI('PGS')
		# if preferences exist, delete them
		if self.development:
			if (cmds.windowPref('PGS', exists = True)):
				cmds.windowPref('PGS', remove = True)

		PGS_window = cmds.window('PGS', title = 'Pabuito Grading System', iconName = 'PGS', width = self.windowWidth, height = self.windowHeight)
		cmds.formLayout('rootLayout', numberOfDivisions = self.windowWidth)
		cmds.rowLayout('topRow', numberOfColumns = 5)
		##This is the top button area

		# self.loadingButtons('start')
		buttonWidth = 152
		cmds.button ('loadDirButton', label = "Load Directory", width = buttonWidth, command = lambda *args:self.fileManager.runFileManager(1, self.enableStart, self.focusStart), enable = not (self.loadedByPickle))
		cmds.button (label = "Load All", width = 2, command = lambda *args:self.fileManager.runFileManager(2), enable = not (self.loadedByPickle), visible = False)
		self.startButton = cmds.button (label = "Start", width = buttonWidth, command = lambda *args: self.startGrading(), enable = False)
		cmds.popupMenu(parent = self.startButton, button = 3)
		self.startRootMenuItem = cmds.menuItem(label = '-> Root Placement', command = lambda *args:self.outputModelFunction('root'))
		self.startSaksonMenuItem = cmds.menuItem(label = 'Sakson Placement', command = lambda *args: self.outputModelFunction('sakson'))
		if self.development:
			self.startDevelopmentMenuItem = cmds.menuItem(label = 'Development', command = lambda *args: self.outputModelFunction('development'))
		self.startRunAutoMenuItem = cmds.menuItem(label = autoLabel, command = lambda *args: self.runAutoToggle())

		##End top button area
		cmds.setParent('topRow')
		cmds.setParent('rootLayout')

		resetWidth = 25
		nextWidth = 40
		self.topRowTwo = cmds.rowLayout('topRow2', numberOfColumns = 3, visible = False)
		cmds.button(label = 'X', width = resetWidth, command = lambda *args: self.resetTool(restart = True), enable = not (self.loadedByPickle))
		self.activeProjectTextField = cmds.textField(text = 'Active Project.ma', editable = False, width = ((buttonWidth*2)-(resetWidth + nextWidth + 2)))
		cmds.popupMenu(parent = self.activeProjectTextField, button = 3)
		cmds.menuItem(label = 'Skip Current', command = lambda *args: self.skipCurrent())
		self.nextFileButton = cmds.button(label = '-->', width = nextWidth, command = lambda *args: self.runNextFile())
		cmds.popupMenu(parent = self.nextFileButton, button = 3)
		self.rootMenuItem = cmds.menuItem(label = '-> Root Placement', command = lambda *args:self.outputModelFunction('root'))
		self.saksonMenuItem = cmds.menuItem(label = 'Sakson Placement', command = lambda *args: self.outputModelFunction('sakson'))
		if self.development:
			self.developmentMenuItem = cmds.menuItem(label = 'Development', command = lambda *args: self.outputModelFunction('development'))
		self.runAutoMenuItem = cmds.menuItem(label = autoLabel, command = lambda *args: self.runAutoToggle())
		self.incompleteMenuItem = cmds.menuItem(label = 'Project Incomplete', command = lambda *args: self.setProjectAsIncomplete())
		cmds.setParent('topRow2')

		cmds.setParent('rootLayout')

		cmds.formLayout('bodyFormLayout', numberOfDivisions = 215)

		self.gradeIntFormLayoutVar = cmds.formLayout('gradeIntFormLayout', numberOfDivisions = 75)

		#set up the category Grade Totals
		self.categoryGrades = GenerateCategoryGrades(self.xml_elementRoot, self.gradeIntFormLayoutVar)
		cmds.setParent('bodyFormLayout')

		gradeSectionsFormLayoutVar = cmds.formLayout(numberOfDivisions = 215)

		cmds.scrollLayout('automatedContentColumn', width = 240)
		#set up the tab layout for the main categories

		self.mainCategories = []
		# tabColumn = [] #Maybe garbage?
		self.pgs_tabLayout = cmds.tabLayout( width = 235, height = subcategoryHeight, scrollable = True)#, backgroundColor = (0.0,0.4,0.0) )#subcategoryHeight

		
		#create main category sections
		for category in self.xml_elementMainCategories:
			
			self.mainCategories.append(category_class.MainCategoryGradeSection(category, self.xml_elementDefaults, self.Update_PGS_intFields))
			cmds.setParent(self.pgs_tabLayout)

		#make all main categories children of the tab layout
		for tab in self.mainCategories:
			cmds.tabLayout(self.pgs_tabLayout, edit = True, tabLabel = (tab.maincat_main_column_layout, tab.title))

		self.log('Running File Manager')
		self.fileManager = fileManagerFile.FileManager()
		self.log('fileManager: {}'.format(self.fileManager))
		self.log('fileManager form \n {}'.format(self.fileManager.fileManagerFormLayout))
		cmds.setParent(self.pgs_tabLayout)
		cmds.tabLayout(self.pgs_tabLayout, edit =True, tabLabel = (self.fileManager.fileManagerFormLayout, 'File Options'))
		self.projectIncompleteGUI(self.pgs_tabLayout)
		cmds.setParent('automatedContentColumn')
		cmds.setParent(gradeSectionsFormLayoutVar)
		cmds.formLayout(gradeSectionsFormLayoutVar, edit = True, attachForm = [
			('automatedContentColumn', 'left', self.uiPadding),
			('automatedContentColumn', 'right', self.uiPadding),
			('automatedContentColumn', 'top', self.uiPadding),
			('automatedContentColumn', 'bottom', self.uiPadding)
			])

		cmds.setParent('bodyFormLayout')

		cmds.formLayout('bodyFormLayout', edit = True, attachForm = [
			(self.gradeIntFormLayoutVar, 'top', self.uiPadding),
			(self.gradeIntFormLayoutVar, 'left', self.uiPadding),
			(gradeSectionsFormLayoutVar, 'top', self.uiPadding),
			(gradeSectionsFormLayoutVar, 'right', self.uiPadding),
			(gradeSectionsFormLayoutVar, 'bottom', self.uiPadding)
			],
			attachControl = [(gradeSectionsFormLayoutVar, 'left', self.uiPadding, self.gradeIntFormLayoutVar)])


		cmds.setParent('..')#main column Layout
		cmds.formLayout('rootLayout',edit = True, 
			attachForm = [
			('topRow', 'left', self.uiPadding),('topRow', 'right', self.uiPadding), ('topRow', 'top', self.uiPadding),
			(self.topRowTwo, 'left', self.uiPadding), (self.topRowTwo, 'right', self.uiPadding), (self.topRowTwo, 'top', self.uiPadding),
			('bodyFormLayout', 'left', self.uiPadding), ('bodyFormLayout', 'right', self.uiPadding),
			('bodyFormLayout', 'bottom', self.uiPadding)
			],
			attachControl = [
			('bodyFormLayout', 'top', self.uiPadding, 'topRow'),
			])

		cmds.showWindow( PGS_window )

		self.log('is this loaded by pickle? {}'.format(self.loadedByPickle))
		if self.loadedByPickle:
			self.fileManager.loadedByPickle()
			self.fileManager.findPicklesFile(self.loadedFileInfo)
			for cat in self.mainCategories:
				for index in self.loadedGradeInfo:
					if index[0] is cat.title:
						cat.this_is_the_grade(index)
			for index in self.loadedGradeInfo:
				self.log('looking for grade boxes')
				if index[0] == 'grade_boxes_internal':
					self.log('grade boxes found!')
					self.categoryGrades.set_pickle_grades(index)

			self.enableStart()
			self.log('starting tool')
			self.startGrading()
			self.log('did it start?')

	def validateXML(self):
		self.log('Validate XML')
		error_list = []
		cat_weights = 0
		eq = self.xml_elementDefaults.find('gradeEquation').text
		self.log('equation: {}'.format(eq))
		cats_to_validate = 0
		for cat in self.xml_elementMainCategories:

			cat_title = cat.get('title')
			if cat_title == None:
				cat_title = cat.find('title').text

			cat_weight = cat.get('weight')
			if cat_weight == None:
				cat_weight = cat.find('weight').text

			if eq.count(cat_title[:3]) != 1:
				self.log('title: {}'.format(cat_title[:3]))
				self.log('count: {}'.format(eq.count(cat_title[:3])))
				error_list.append('{} \nnot present in equation exactly once.'.format(cat_title))

			# self.log('Adding: {}'.format(cat.find('title').text))
			# ignore_validation = False
			ignore_validation = cat.find('ignore_validation')
			# print('ignore validation element: {}'.format(ignore_validation))
			# if ignore_validation != None:
				# print('value: {}').format(ignore_validation.text.lower())
			if ignore_validation != None:
				if ignore_validation.text.lower() == 'true':
					ignore_validation = True
			else:
				ignore_validation = False

			
			if not ignore_validation:
				# print('validation counted: {}'.format(cat_title))
				cat_weights += float(cat_weight)
				cats_to_validate += 1
			else:
				# print('ignore validation!\n\n')
				cmds.warning('Category: {} ignored in validation.'.format(cat_title))

			# self.log('current weighting: {}'.format(cat_weights))
			subcat_weights = 0
			subs_to_validate = 0
			for subcat in cat.findall('subcategory'):

				sub_title = subcat.get('title')
				if sub_title == None:
					sub_title = subcat.find('title').text

				sub_weight = subcat.get('weight')
				if sub_weight == None:
					sub_weight = subcat.find('weight').text

				# print('Subcat: {} - {}'.format(sub_title, sub_weight))

				ignore_validation = subcat.find('ignore_validation')
				if ignore_validation != None:
					if ignore_validation.text.lower() == 'true':
						ignore_validation = True
				else:
					ignore_validation = False

				if not ignore_validation:
					subcat_weights += float(sub_weight)
					subs_to_validate += 1
				else:
					cmds.warning('Subcategory: {} ignored in validation.'.format(sub_title))
					
				# self.log('current weighting: {}'.format(subcat_weights))
			self.log('total subcat weighting: {}'.format(subcat_weights))

			if (subcat_weights != 100) and (subs_to_validate != 0):
				error_list.append('{} \nsubweights incorrect. Total weights: {}'.format(cat_title, subcat_weights))
				cmds.warning('Subcategory weighting incorrect!\n{} total subcategory weighting: {}'.format(
					cat_title, subcat_weights))
				error_list.append('\n')

		for box in self.xml_elementRoot.findall('grade_box'):
			self.log('box: {}'.format(box.get('title')))
			if box.get('title') == 'Late':
				if eq.count(box.get('title')) != 1:
					error_list.append('{} Grade Box\nnot present in equation exactly once'.format(box.get('title')))
			elif eq.count(box.get('title')[:3]) != 1:
				error_list.append('{} Grade Box\nnot present in equation exactly once'.format(box.get('title')))

		self.log('total cat weighting: {}'.format(cat_weights))
		if (cat_weights != 100) and (cats_to_validate != 0): 
			error_list.append('\nCategory weights incorrect. Total weights: {}'.format(cat_weights))
			cmds.warning('Category Weighting Incorrect!\nTotal category weight: {}'.format(cat_weights))

		if len(error_list) >= 1:
			self.log('len(error_list): {}'.format(len(error_list)))
			self.log('error_list: {}'.format(error_list))
			msg = ''
			for i in error_list:
				msg += '{}\n'.format(i)

			prelist = ['Oh Snap!', 'Stop the ship!', 'Well butter my biscuits!',
						'I better fix that!', 'Oopsie daisy!', "Yup, that's about right"]
			button_list = random.sample(prelist, 2)
			button_list.append('Continue Anyway')
			random.shuffle(button_list)
			dialog = cmds.confirmDialog( 
					title="PGS XML Validation Error", 
					message = msg , 
					button =button_list, 
					defaultButton = 'Oh Snap!', 
					cancelButton = 'Stop the ship!',
					dismissString = 'Stop the ship!')
			if dialog != 'Continue Anyway':
				cmds.error('\nPGS XML Validation Error!\n{}'.format(msg))

	def visSwap(self, int, *args):
		if int == 1: 
			cmds.rowLayout(self.topRowTwo, edit = True, visible = True)
			cmds.rowLayout('topRow', edit = True, visible = False)
			cmds.formLayout('rootLayout', edit = True, attachControl = [('bodyFormLayout', 'top', self.uiPadding, self.topRowTwo)])
		else:
			cmds.rowLayout('topRow', edit = True, visible = True)
			cmds.rowLayout(self.topRowTwo, edit = True, visible = False)
			cmds.formLayout('rootLayout', edit = True, attachControl = [('bodyFormLayout', 'top', self.uiPadding, 'topRow')])

	def unpackPickle(self, pickleFile, *args):
		self.log('unpacking pickle')
		self.log('pickle file is: {}'.format(pickleFile))

		#switching to a better file reading style
		with open(pickleFile, 'r') as pickleFileObject:
			unpackedPickleInfo = pickle.loads(pickleFileObject.read())

		self.xml_elementTree = unpackedPickleInfo[0]
		self.loadedGradeInfo = unpackedPickleInfo[1]
		self.loadedFileInfo = unpackedPickleInfo[2]
		self.loadedFileInfo['pickleDirectory'] = pickleFile
		self.loadedByPickle = True

	def startGrading(self, *args):
		self.log('Start Grading!')

		if not self.loadedByPickle:
			# print('attempting to pickle filter')
			auto_pickle_filter_element = self.xml_elementDefaults.find('auto_pickle_filter')
			# print(auto_pickle_filter_element)
			if auto_pickle_filter_element != None:
				# print('element found!')
				# print(auto_pickle_filter_element.text)
				if auto_pickle_filter_element.text.lower() == 'True'.lower():
					# print('lets filter')
					self.fileManager.pickle_filter()
					# print('done')

		firstFile = self.fileManager.what_is_the_next_file()
		if firstFile == None:
			cmds.error('No files loaded. Please load files into PGS.')
		self.log('The first file is: {}'.format(firstFile[1]))
		cmds.textField(self.activeProjectTextField, edit = True, text = firstFile[1])
		self.log('first file path is: \n {}'.format(firstFile[0]))
		self.visSwap(1)
		cmds.file(force = True, newFile = True)
		try:
			cmds.file(firstFile[0], open = True)
		except RuntimeError:
			cmds.warning('File is from Maya {}. Ignoring version.'.format(cmds.fileInfo('version', query = True)))
			cmds.warning('Errors may occur')
			cmds.file(firstFile[0], open = True, ignoreVersion = True)

		self.fileManager.toolStarted = True
		if not self.loadedByPickle:
			self.runAutomation()
		self.enable()

	def enable(self):
		self.categoryGrades.enable()
		for cat in self.mainCategories:
			cat.enable()

	def enableStart(self):
		cmds.button(self.startButton, edit = True, enable = True)

	def focusStart(self):
		#sets focus but cannot keyboard enter activate :-/
		# cmds.setFocus(self.startButton)
		self.log('sad focus start')

	def disableStart(self):
		cmds.button(self.startButton, edit = True, enable = False)

	def disable(self):
		self.categoryGrades.disable()
		for cat in self.mainCategories:
			cat.disable()

	def toolIsComplete(self):
		self.incomplete_cats = []
		for cat in self.mainCategories:
			inc_cats = cat.are_you_complete()
			if inc_cats != []:
				self.incomplete_cats.append((cat.title, inc_cats))
		return self.incomplete_cats

	def setProjectAsNOTIncomplete(self):
		self.log('set up interface as not incomplete')
		self.projectIncomplete = False
		self.enable()
		cmds.formLayout(self.projectIncompleteFormLayout, edit = True, enable = False)
		self.resetIncompleteGUI()
		cmds.menuItem(self.incompleteMenuItem, edit = True, label = 'Project Incomplete', command = lambda *args:self.setProjectAsIncomplete())

	def setProjectAsIncomplete(self):
		self.log('set up interface as project incomplete')
		self.projectIncomplete = True
		self.disable()
		cmds.formLayout(self.projectIncompleteFormLayout, edit = True, enable = True)
		cmds.tabLayout(self.pgs_tabLayout, edit = True, selectTab = self.projectIncompleteFormLayout )
		cmds.menuItem(self.incompleteMenuItem, edit = True, label = 'Not Incomplete', command = lambda *args:self.setProjectAsNOTIncomplete())

	def outputProjectIncomplete(self):
		self.log('Outputting project incomplete!')
		self.projectIncompleteOutputText = cmds.scrollField(self.projectIncompleteScrollField, query = True, text = True)
		if not self.projectIncompleteOutputText:
			if self.development:
				cmds.warning('Incomplete Field not filled out. Please comment')
			else:
				cmds.error('Incomplete Field not filled out. Please add a comment.')
		projectIncompleteGradeBundle = (cmds.intField(self.projectIncompleteIntField, query = True, value = True), 
			cmds.scrollField(self.projectIncompleteScrollField, query = True, text = True))

		if self.outputModel is 'development':
			self.log('outputModel is development. Printing output to stdout')
			self.writeProjectIncompleteTextDoc_Dev(projectIncompleteGradeBundle)
		else:
			self.log('collecting path for output')
			workingPathAndName = self.fileManager.currentPath(self.outputModel)
			self.log('workingPathAndName: \n Name: {} \n Path: {} \n Pickle: {}'.format(workingPathAndName['filename'], workingPathAndName['textDirectory'], workingPathAndName['pickleDirectory']))
			if self.outputModel is 'sakson':
				self.log('outputModel is Sakson. Saving output to maya file locations')
				self.writeProjectIncompleteTextDoc(projectIncompleteGradeBundle, workingPathAndName)
			elif self.outputModel is 'root':
				self.log('outputModel is root. Saving output to root directory')
				self.writeProjectIncompleteTextDoc(projectIncompleteGradeBundle, workingPathAndName)

	def resetIncompleteGUI(self):
		cmds.formLayout(self.projectIncompleteFormLayout, edit = True, enable = False)
		cmds.intField(self.projectIncompleteIntField, edit = True, value = 0)
		cmds.scrollField(self.projectIncompleteScrollField, edit = True, text = '')
		self.updateProjectIncompleteIntField()

	def writeProjectIncompleteTextDoc(self, gradeInfo, directoryDict):
		self.log('write project incomplete text doc')
		self.log('gradeInfo: {}'.format(gradeInfo))
		self.log('Directory: {}'.format(directoryDict))
		fileOutList = []

		try:
			os.makedirs(directoryDict['textDirectory'])
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise
		lineSeparator = ('-' * 50)
		fileOutList.extend(self.wordwrap('Grading for: {}\n'.format(directoryDict['filename'])))
		fileOutList.append(lineSeparator)
		try:
			gradeTotal_textIntro = self.xml_elementDefaults.find('total_intro').text
			if gradeTotal_textIntro != None: 
				fileOutList.extend(self.wordwrap('{}{}%'.format(gradeTotal_textIntro,gradeInfo[0])))
		except AttributeError:
			fileOutList.extend(self.wordwrap('{}%\n'.format(gradeInfo[0])))

		fileOutList.append(lineSeparator)

		try:
			incomplete_text = self.xml_elementDefaults.find('incomplete').text
			self.log('Incomplete info is: {}'.format(incomplete_text))
			if incomplete_text != None:
				fileOutList.extend(self.wordwrap(incomplete_text))
				fileOutList.append(lineSeparator)
				fileOutList.extend(self.wordwrap(gradeInfo[1]))
		except AttributeError:
			fileOutList.extend(self.wordwrap(gradeInfo[1]))

		try:
			gradeTotal_textIntro = self.xml_elementDefaults.find('total_intro').text
			if gradeTotal_textIntro != None: 
				fileOutList.extend(self.wordwrap('{}{}%'.format(gradeTotal_textIntro,gradeInfo[0])))
		except AttributeError:
			fileOutList.extend(self.wordwrap('{}%\n'.format(gradeInfo[0])))

		#Add HTML Comment <!-- Grade total : File Name -->
		# fileOutList.extend(['<!-- {}: {}-->'.format(directoryDict['filename'][:20].encode('utf-8'), gradeInfo[0])])
		fileOutList.extend(['\n\n{}: {}%'.format(directoryDict['filename'][:20].encode('utf-8'), gradeInfo[0])])

		with open(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt', 'w') as f:
			for line in fileOutList:
				# f.write(line + '<br>\n')
				f.write(line + '\n')

	def writeProjectIncompleteTextDoc_Dev(self, gradeInfo):
		self.log('write Project Incomplete - dev')
		self.log('Grade Info: {}'.format(gradeInfo))

	def projectIncompleteGUI(self, parentTabLayout):
		self.log('runProjectIncomplete')
		noLoadWarning = 'Projects processed as incomplete cannot be reloaded into the PGS grading platform. '
		defaultIncompleteText = self.xml_elementDefaults.find('incomplete').text
		try:
			defaultIncompleteHeight = (len(defaultIncompleteText)//30)*15
		except TypeError:
			defaultIncompleteHeight = 1
		# print('defaultIncompleteText len: {}\ndefaultIncompleteHeight: {}'.format(defaultIncompleteText, defaultIncompleteHeight))
		incompleteWindowWidthHeight = (200, 300)
		intFieldWidth = 35
		# pgs_project_incomplete_window = cmds.window('PGS - Incomplete Project', title = 'PGS - Incomplete Project', iconName = 'PGS - Prj Inc', widthHeight = incompleteWindowWidthHeight)
		self.projectIncompleteFormLayout = cmds.formLayout(numberOfDivisions = incompleteWindowWidthHeight[0], enable = False)
		projectIncompleteRowLayout = cmds.rowLayout(numberOfColumns = 2)
		self.projectIncompleteIntField = cmds.intField(minValue=0, maxValue=150, step=1 , width = intFieldWidth, changeCommand = lambda *args: self.updateProjectIncompleteIntField())
		self.projectIncompleteIntSlider = cmds.intSlider( min=-100, max=0, value=0, step=1, width = (incompleteWindowWidthHeight[0] - intFieldWidth), changeCommand = lambda *args: self.updateProjectIncompleteSlider(), dragCommand = lambda *args: self.updateProjectIncompleteSlider())
		cmds.setParent('..')
		cmds.setParent(self.projectIncompleteFormLayout)
		projectIncompleteColumnLayout = cmds.columnLayout(columnAttach = ('both', 5), width = incompleteWindowWidthHeight[0])
		cmds.text(label = defaultIncompleteText,  wordWrap = True, height = defaultIncompleteHeight, width = incompleteWindowWidthHeight[0])
		self.projectIncompleteScrollField = cmds.scrollField(wordWrap = True, width = incompleteWindowWidthHeight[0])
		cmds.text(label = noLoadWarning,  wordWrap = True, height = 60, width = incompleteWindowWidthHeight[0], backgroundColor = (0.9, 0.5, 0.5))
		# cmds.button(label = 'Output Incomplet Project',width = incompleteWindowWidthHeight[0], command = lambda *args: self.outputProjectIncomplete())
		cmds.setParent('..')
		cmds.setParent(self.projectIncompleteFormLayout)
		cmds.tabLayout(parentTabLayout, edit = True, tabLabel = (self.projectIncompleteFormLayout, 'Project Incomplete'))


		cmds.formLayout(self.projectIncompleteFormLayout, edit = True, attachForm = [
			(projectIncompleteRowLayout, 'top', self.uiPadding),
			(projectIncompleteRowLayout, 'right', self.uiPadding),
			(projectIncompleteRowLayout, 'left', self.uiPadding),
			(projectIncompleteColumnLayout, 'right', self.uiPadding),
			(projectIncompleteColumnLayout, 'left', self.uiPadding)],
			attachControl = [
			(projectIncompleteColumnLayout, 'top', self.uiPadding, projectIncompleteRowLayout)])
		# cmds.showWindow(pgs_project_incomplete_window)

	def updateProjectIncompleteSlider(self):
		self.log('update project incomplete slider')
		sliderValue = abs(cmds.intSlider(self.projectIncompleteIntSlider, query = True, value = True))
		cmds.intField(self.projectIncompleteIntField, edit = True, value = sliderValue)

	def updateProjectIncompleteIntField(self):
		self.log('update project incomplete int field')
		fieldValue = cmds.intField(self.projectIncompleteIntField, query = True, value = True)
		cmds.intSlider(self.projectIncompleteIntSlider, edit = True, value = -fieldValue)

	def skipCurrent(self):
		self.log('skipCurrent activated')
		self.fileManager.skip_current()
		nextFile = self.fileManager.what_is_the_next_file()
		if nextFile != None:
			cmds.textField(self.activeProjectTextField, edit = True, text = nextFile[1])
			self.log('clear the gradeTool grades')
			self.resetTool()
			self.disable()
			self.log('New Maya Scene')
			cmds.file(force = True, newFile = True)
			self.log('load the next Maya file')
			try:
				cmds.file(nextFile[0], open = True)
			except RuntimeError:
				cmds.warning('File is from Maya {}. Ignoring version.'.format(cmds.fileInfo('version', query = True)))
				cmds.warning('Errors may occur')
				cmds.file(nextFile[0], open = True, ignoreVersion = True)
			if not self.loadedByPickle:
				self.log('run auto')
				self.runAutomation()
			self.enable()
			cmds.tabLayout(self.pgs_tabLayout, edit = True, selectTabIndex = 1)

	def runNextFile(self):
		self.log('This method will run all methods necessary to move from one file to another')
		if not self.projectIncomplete:
			incomplete_sections = self.toolIsComplete()
			for section in incomplete_sections:
				self.log('incomplete_sections: {}'.format(section))
			if incomplete_sections == []:
				self.log('The tool is complete')
			else: 
				self.log('\n\n')
				if self.development:
					cmds.warning('Tool is not complete!')
				else: 
					print('len is: {}'.format(len(self.fail_message)))
					rand = random.randint(0, len(self.fail_message) - 1)
					incomplete_str = '\n::Incomplete Sections::\n'
					for cat in self.incomplete_cats:
						incomplete_str += '\n' + cat[0] + ':\n' 
						for section in cat[1]:
							incomplete_str += section + '\n'
					message_str = self.fail_message[rand][0] + '\n' + incomplete_str
					button_str = self.fail_message[rand][1]
					print('rand: {}'.format(rand))
					cmds.confirmDialog( title="PGS Error", message = message_str , button =button_str, dismissString = None)
					cmds.error('PGS not complete. Please complete all grade sections.')
				self.log('\n\n')
			self.log('output grade')
			self.handleOutput()
		else: 
			self.log('project incomplete!')
			self.outputProjectIncomplete()
			self.projectIncomplete = False
			self.setProjectAsNOTIncomplete()

		self.log('cycle the active file to the completed list')
		self.fileManager.cycle_file()
		nextFile = self.fileManager.what_is_the_next_file()
		if nextFile != None:
			cmds.textField(self.activeProjectTextField, edit = True, text = nextFile[1])
			self.log('clear the gradeTool grades')
			self.resetTool()
			self.disable()
			self.log('New Maya Scene')
			cmds.file(force = True, newFile = True)
			self.log('load the next Maya file')
			try:
				cmds.file(nextFile[0], open = True)
			except RuntimeError:
				cmds.warning('File is from Maya {}. Ignoring version.'.format(cmds.fileInfo('version', query = True)))
				cmds.warning('Errors may occur')
				cmds.file(nextFile[0], open = True, ignoreVersion = True)
			if not self.loadedByPickle:
				self.log('run auto')
				self.runAutomation()
			self.enable()
			cmds.tabLayout(self.pgs_tabLayout, edit = True, selectTabIndex = 1)

		else:
			self.endOfQueue()

	def runAutomation(self):
		if self.runAuto:
			for cat in self.mainCategories:
				cat.autoProGo()

	def runAutoToggle(self, *args):
		if self.runAuto:
			self.runAuto = False
			cmds.menuItem(self.startRunAutoMenuItem, edit = True, label = 'RunAuto - Off')
			cmds.menuItem(self.runAutoMenuItem, edit = True, label = 'RunAuto - Off')
			self.log('runAuto: {}'.format(self.runAuto))
		else:
			self.runAuto = True
			cmds.menuItem(self.startRunAutoMenuItem, edit = True, label = 'RunAuto - On')
			cmds.menuItem(self.runAutoMenuItem, edit = True, label = 'RunAuto - On')
			self.log('runAuto: {}'.format(self.runAuto))
			
	def endOfQueue(self):
		if self.loadedByPickle:
			dialog = cmds.confirmDialog( title="Grade Correction Output.", message='Good job!', button=['Done!'], defaultButton='Done!', cancelButton='Done!', dismissString='Done!')
		else:
			dialog = cmds.confirmDialog( title="You've reached the end of the queue!", message='Are you finished?', button=['Add Files','Done!'], defaultButton='Done!', cancelButton='Done!', dismissString='Done!')
		if dialog == 'Add Files':
			self.log('Add Files')
			self.fileManager.runFileManager(1)
			self.disable()
			self.resetTool()
			self.startGrading()
		elif dialog == 'Done!':
			self.log('Done!')
			cmds.deleteUI('PGS')
			cmds.file(force = True, newFile = True)
		else:
			cmds.error('I think the dialog is broken?')

	def outputModelFunction(self, modelType, *args):
		self.outputModel = modelType
		self.log('outputModel: {}'.format(self.outputModel))
		self.toggleOutputModelLabels()

	def toggleOutputModelLabels(self):
		if self.outputModel == 'root':
			cmds.menuItem(self.rootMenuItem, edit = True, label = '-> Root Placement')
			cmds.menuItem(self.saksonMenuItem, edit = True, label = 'Sakson Placement')
			cmds.menuItem(self.startRootMenuItem, edit = True, label = '-> Root Placement')
			cmds.menuItem(self.startSaksonMenuItem, edit = True, label = 'Sakson Placement')
			if self.development:
				cmds.menuItem(self.developmentMenuItem, edit = True, label = 'Development')
				cmds.menuItem(self.startDevelopmentMenuItem, edit = True, label = 'Development')
		if self.outputModel == 'sakson':
			cmds.menuItem(self.rootMenuItem, edit = True, label = 'Root Placement')
			cmds.menuItem(self.saksonMenuItem, edit = True, label = '-> Sakson Placement')
			cmds.menuItem(self.startRootMenuItem, edit = True, label = 'Root Placement')
			cmds.menuItem(self.startSaksonMenuItem, edit = True, label = '-> Sakson Placement')
			if self.development:
				cmds.menuItem(self.developmentMenuItem, edit = True, label = 'Development')
				cmds.menuItem(self.startDevelopmentMenuItem, edit = True, label = 'Development')
		if self.outputModel == 'development':
			if self.development:
				cmds.menuItem(self.rootMenuItem, edit = True, label = 'Root Placement')
				cmds.menuItem(self.saksonMenuItem, edit = True, label = 'Sakson Placement')
				cmds.menuItem(self.startRootMenuItem, edit = True, label = 'Root Placement')
				cmds.menuItem(self.startSaksonMenuItem, edit = True, label = 'Sakson Placement')
				cmds.menuItem(self.developmentMenuItem, edit = True, label = '-> Development')
				cmds.menuItem(self.startDevelopmentMenuItem, edit = True, label = '-> Development')			

	def handleOutput(self):
		self.log('output model is: {}'.format(self.outputModel))
		grades = self.gatherGrades()
		self.outputTextFiles(grades)

	def outputTextFiles(self,grades):
		self.log('running outputTextFiles')
		if self.outputModel is 'development':
			self.log('outputModel is development. Printing output to stdout')
			self.developmentOutput(grades)
		else:
			self.log('collecting path for output')
			workingPathAndName = self.fileManager.currentPath(self.outputModel)
			self.log('workingPathAndName: \n Name: {} \n Path: {} \n Pickle: {}'.format(workingPathAndName['filename'], workingPathAndName['textDirectory'], workingPathAndName['pickleDirectory']))


			# print('\n\nworkingPathAndName: \n Name: {} \n Path: {} \n Pickle: {}'.format(workingPathAndName['filename'], workingPathAndName['textDirectory'], workingPathAndName['pickleDirectory']))


			workingPathAndName['filename'] = self.validate_filename_func(workingPathAndName)

			# print('workingPathAndName: \n{}'.format(workingPathAndName['filename']))

			if self.outputModel is 'sakson':
				self.log('outputModel is Sakson. Saving output to maya file locations')
				self.writeOutputFile(grades, workingPathAndName)
			elif self.outputModel is 'root':
				self.log('outputModel is root. Saving output to root directory')
				self.writeOutputFile(grades, workingPathAndName)
			self.log('writing pickle')
			self.writePickleFile(grades, workingPathAndName)
	
	def developmentOutput(self, grades):
		lineSeparator = '--------------------\n'
		fileName = self.fileManager.what_is_the_current_file()	
		self.log('Print text file')
		self.log('\n\n\n<<<START TEXT DOC>>>\n\n\n')
		self.log('Grading for: {}\n'.format(fileName))
		self.log(lineSeparator)
		for section in grades:
			self.log('{}\n'.format(section[0]))
			self.log(lineSeparator)
			if section[2] != '':
				try:
					highnoteIntro = self.xml_elementDefaults.find('highnote_intro').text
					if highnoteIntro != None: self.log('{}\n'.format(highnoteIntro))
				except AttributeError:
					pass
				self.log('{}\n'.format(section[2]))
				self.log(lineSeparator)
			self.log('{}\n'.format(section[4]['section_title']))
			self.log(lineSeparator)

			if section[4]['comment_text'] != '':
				try:
					comment_textIntro = self.xml_elementDefaults.find('comment_intro').text
					if comment_textIntro != None: self.log('{}\n'.format(comment_textIntro))
				except AttributeError:
					pass
				self.log('{}\n'.format(section[4]['comment_text']))

			if section[4]['default_comments_text'] != '':
				try:
					default_comments_textIntro = self.xml_elementDefaults.find('default_comment_intro').text
					if default_comments_textIntro != None: self.log('{}\n'.format(default_comments_textIntro))
				except AttributeError:
					pass
				self.log('{}\n'.format(section[4]['default_comments_text']))

			if section[4]['example_comments_text'] != '':
				try: 
					example_comments_textIntro = self.xml_elementDefaults.find('example_object_intro').text
					if example_comments_textIntro != None: self.log('{}\n'.format(example_comments_textIntro))
				except AttributeError:
					pass
				self.log('{}\n'.format(section[4]['example_comments_text']))
			self.log(lineSeparator)

		self.log('\n\n\n<<<END TEXT DOC>>>\n\n\n')

	def wordwrap(self, inputText, wrapWidth = 50):
		return textwrap.wrap(inputText, wrapWidth)

	def validate_filename_func(self, directoryDict):
		# print('\n\n{}\n\n'.format(directoryDict))
		if os.path.isfile(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt') or \
		   os.path.isfile(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs'):
			# print('\n\nFILE EXISTS!!!\n\n')
			handle_file = cmds.confirmDialog( 
				title='File Exists', 
				message='Overwrite or Iterate file?', 
				button=['Overwrite','Iterate'], 
				defaultButton='Overwrite',  
				dismissString='Iterate' )
			# print('\n\n{}\n\n'.format(handle_file))
			if handle_file == 'Overwrite':
				# print('Overwrite selected')
				if os.path.isfile(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt'):
					os.remove(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt')
					# print('deleted text doc')
				if os.path.isfile(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs'):
					os.remove(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs')
					# print('deleted pgs file')
				return directoryDict['filename']
			if handle_file == 'Iterate':
				# print('Iterate Selected')
				# print('textDict: {}\nfilename: {}'.format(directoryDict['textDirectory'] , directoryDict['filename']))
				if os.path.isfile(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt') or \
				   os.path.isfile(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs'):
					the_file = directoryDict['filename']
					iter = 1
					# print('os.path.isfile: {}'.format((directoryDict['textDirectory'] + the_file + '.txt')))
					while os.path.isfile(directoryDict['textDirectory'] + the_file + '.txt') or \
					   os.path.isfile(directoryDict['pickleDirectory'] + the_file + '.pgs'):
						if iter > 1:
							the_file = the_file.rsplit('_', 1)[0]
						the_file += '_{:02d}'.format(iter)
						# print('the_file: {}'.format(the_file))
						# print('os.path.isfile: {}'.format((directoryDict['textDirectory'] + the_file + '.txt')))
						iter += 1
					return the_file 
		else:
			return directoryDict['filename']

	def writeOutputFile(self, grades, directoryDict):
		self.log('write output file to directory')

		#make directory, if it exists...OK!
		try:
			os.makedirs(directoryDict['textDirectory'])
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

		wrapWidth = 50
		# lineSeparator = '-' * wrapWidth
		lineSeparator = '<hr>'
		# smallLineSeparator = '-' * (wrapWidth / 2)
		smallLineSeparator = '<hr style="width:50%;margin:0">'
		newLine = '<br>'
		mini_break = '<hr style="width:25%;margin:0">'
		# newLine = '\n'
		self.log('filename: {}'.format(directoryDict['filename']))
		self.log('text path: {}'.format(directoryDict['textDirectory']))
		fileOutList = []

		# print('\nfilename: {}\n'.format(directoryDict['filename']))

		# add "Grading for" title
		fileOutList.extend(textwrap.wrap('<b>Grading for:</b> <i>{}</i>\n'.format(directoryDict['filename'].encode('utf-8')), wrapWidth))
		# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
		# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))
		# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		#grade total  text
		try:
			gradeTotal_textIntro = self.xml_elementDefaults.find('total_intro').text
			if gradeTotal_textIntro != None: 
				fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
				fileOutList.extend(textwrap.wrap('<b>{}</b> {}%'.format(gradeTotal_textIntro,self.categoryGrades.gradeTotal()), wrapWidth))
		except AttributeError:
			fileOutList.extend(textwrap.wrap('{}%\n'.format(self.categoryGrades.gradeTotal()), wrapWidth))
		# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
		# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		# grade category... maybe
		for section in grades:
			fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
			if section[0] != 'grade_boxes_internal':
				fileOutList.extend(textwrap.wrap('<b>{}:</b> {}%\n'.format(section[0],int(section[3])), wrapWidth))
				# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
				fileOutList.extend(textwrap.wrap(smallLineSeparator, wrapWidth))
				# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))

				if section[2] != '':
					try:
						highnoteIntro = self.xml_elementDefaults.find('highnote_intro').textField
						if highnoteIntro != None: 
							fileOutList.extend(textwrap.wrap('{}\n'.format(highnoteIntro), wrapWidth))
					except AttributeError:
						pass
						fileOutList.extend(textwrap.wrap('{}\n'.format(section[2]), wrapWidth))
						# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))

				# grading subcategories...?
				for subSection in section[4]:
					fileOutList.extend(textwrap.wrap(mini_break, wrapWidth))
					#section title
					fileOutList.extend(textwrap.wrap('<i>{}</i>'.format(subSection['section_title'].encode('utf-8')), wrapWidth))
					fileOutList.extend(textwrap.wrap(newLine, wrapWidth))
					# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
					#comment text
					if subSection['comment_text'] !='':
						try:
							comment_textIntro = self.xml_elementDefaults.find('comment_intro').text
							if comment_textIntro != None: 
								fileOutList.extend(textwrap.wrap('{}\n'.format(comment_textIntro), wrapWidth))
						except AttributeError:
							pass
						fileOutList.extend(textwrap.wrap('{}\n'.format(subSection['comment_text'].encode('utf-8')), wrapWidth))
						# fileOutList.extend(textwrap.wrap(smallLineSeparator, wrapWidth))
						fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

					#default comments text
					if subSection['default_comments_text'] !='':
						try:
							default_comments_textIntro = self.xml_elementDefaults.find('default_comment_intro').text
							if default_comments_textIntro != None: 
								fileOutList.extend(textwrap.wrap('{}\n'.format(default_comments_textIntro), wrapWidth))
						except AttributeError:
							pass
						fileOutList.extend(textwrap.wrap('{}\n'.format(subSection['default_comments_text'].encode('utf-8')), wrapWidth))
						# fileOutList.extend(textwrap.wrap(smallLineSeparator, wrapWidth))
						fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

					#example comments text
					if subSection['example_comments_text'] !='':
						try:
							example_comments_textIntro = self.xml_elementDefaults.find('example_object_intro').text
							if example_comments_textIntro != None: 
								fileOutList.extend(textwrap.wrap('{}\n'.format(example_comments_textIntro), wrapWidth))
						except AttributeError:
							pass
						fileOutList.extend(textwrap.wrap('{}\n'.format(subSection['example_comments_text'].encode('utf-8')), wrapWidth))
						# fileOutList.extend(textwrap.wrap(smallLineSeparator, wrapWidth))
						fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

					# fileOutList.extend(textwrap.wrap(mini_break, wrapWidth))

				# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
			# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
		# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		# grading summary
		for section in grades:
			if section[0] != 'grade_boxes_internal':
				fileOutList.extend(textwrap.wrap('{}: {}%'.format(section[0],int(section[3])), wrapWidth))
				fileOutList.extend(textwrap.wrap(newLine, wrapWidth))
			else:
				# fileOutList.extend(textwrap.wrap(newLine, wrapWidth))
				for box in section[4]:
					self.log('box: \n{}'.format(box))
					fileOutList.extend(textwrap.wrap('{}: {}%'.format(box['default_comments_text'], box['grade_value'])))
					fileOutList.extend(textwrap.wrap(newLine, wrapWidth))
				fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		fileOutList.extend(textwrap.wrap(smallLineSeparator, wrapWidth))
		#grade total  text
		try:
			gradeTotal_textIntro = self.xml_elementDefaults.find('total_intro').text
			if gradeTotal_textIntro != None: 
				# fileOutList.extend(textwrap.wrap(lineSeparator, wrapWidth))
				fileOutList.extend(textwrap.wrap('{} {}%'.format(gradeTotal_textIntro,self.categoryGrades.gradeTotal()), wrapWidth))
		except AttributeError:
			fileOutList.extend(textwrap.wrap('{}%'.format(self.categoryGrades.gradeTotal()), wrapWidth))
			fileOutList.extend(textwrap.wrap(newLine, wrapWidth))

		fileOutList.extend(['{}'.format(directoryDict['filename'].encode('utf-8'), self.categoryGrades.gradeTotal())])		

		with open(os.path.join(directoryDict['textDirectory'], directoryDict['filename'] + '.txt'), 'w') as f:
		# with open(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt', 'w') as f:
			for line in fileOutList:
				# f.write('{}{}'.format(line.replace('\n', '<br>\n'), '<br>\n'))
				f.write('{}{}'.format(line, '\n'))

	def writePickleFile(self, grades, directoryDict):
		self.log('write cPickle file')
		pickleBuild = (self.xml_elementTree, grades, directoryDict)
		pickleToWrite = pickle.dumps(pickleBuild)

		# print('pickleDirectory: \n{}\nFilename: {}'.format(directoryDict['pickleDirectory'], directoryDict['filename']))

		# print('{}\n\n\n'.format(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs'))

		# print('new pickle dir: \n{}\n\n'.format(os.path.join(directoryDict['pickleDirectory'], directoryDict['filename'] + '.pgs')))

		with open(os.path.join(directoryDict['pickleDirectory'], directoryDict['filename'] + '.pgs'), 'w') as f:
			f.write(pickleToWrite)

		# pickleFile = open(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs', 'w')
		# pickleFile.write(pickleToWrite)
		# pickleFile.close()

	def gatherGrades(self):
		gradesForPickle = []
		for cat in self.mainCategories:
			gradesForPickle.append(cat.what_is_the_grade())
		gradesForPickle.append(self.categoryGrades.collect_grades())
		for index in gradesForPickle:
			self.log('Grades from cat {} : {}'.format(index[0], index))
			self.log('\n\n{}\n\n'.format(index))
		return gradesForPickle

	def restartTool(self):
		self.log('reset PGS grade tool')

		cmds.button(self.startButton, edit = False, enable = False)
		self.disableStart()
		self.visSwap(2)
		self.fileManager.reset()
		self.categoryGrades.disable()
		self.setProjectAsNOTIncomplete()
		for cat in self.mainCategories:
			self.log('disable categories')
			cat.disable()
			self.log('disabled?')
		cmds.file(force = True, newFile = True)

	def resetTool(self, restart = False):
		self.log('reset PGS grade tool')
		# self.categoryGrades.reset()
		for cat in self.mainCategories:
			cat.reset()
		self.categoryGrades.reset()
		self.categoryGrades.enable()
		if restart:
			self.restartTool()

	def update(self):
		for cat in self.mainCategories:
			cat.update()

	def Update_PGS_intFields(self):
		"""
		Update the grade tool
		"""
		self.log('Updating PGS')

		currentStatus = []
		for mainCat in self.mainCategories:
			currentStatus.append(mainCat.check_grade_status())

		self.categoryGrades.setGradeValues(currentStatus)
		self.log('grades should be set now')

	def log(self, message, prefix = '.:Pabuito Grading System::'):
		"""
		print stuff yo!
		"""
		if self.development:
			print "%s: %s" % (prefix, message)

class GenerateCategoryGrades(object):

	def __init__(self, rootXMLElement, uiParentFormLayout):
		parent = uiParentFormLayout
		rowPadding = 1
		mainCategories = rootXMLElement.findall('category')
		self.gradeEquation = rootXMLElement.find('defaults').find('gradeEquation').text
		self.log('gradeEquation raw: {}'.format(self.gradeEquation))
		self.catGrades = []
		cycleCount = 0
		lastRowControl = []
		# self.isLate = False
		for cat in mainCategories:
			tempList = []

			cat_title = cat.get('title')
			if cat_title == None:
				cat_title = cat.find('title').text

			cat_weight = cat.get('weight')
			if cat_weight == None:
				cat_weight = cat.find('weight').text

			tempList.append(cat_title[:3])
			self.log('cat title: %s' % tempList[0])
			tempRow = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
			cmds.text(label = tempList[0], width = 30)
			tempList.append(cmds.intField(value = 0, width = 30, editable = False, backgroundColor = (0.5,0.5,0.5)))
			self.log('intField lives at: %s' % tempList[1])
			tempList.append(cat_weight)
			self.log('cat weight: {}'.format(tempList[2]))
			cmds.setParent(tempRow)
			cmds.setParent(parent)


			self.catGrades.append(tempList)
			self.log('Collected Tuples are: %s' % self.catGrades)

			cmds.formLayout(parent, edit = True, attachForm = [
				(tempRow, 'left', rowPadding), (tempRow, 'right', rowPadding)
				])
			if cycleCount == 0:
				cmds.formLayout(parent, edit = True, attachForm = [(tempRow, 'top', rowPadding)])
				cycleCount += 1
				lastRowControl = tempRow
			else:
				cmds.formLayout(parent, edit = True, attachControl = [(tempRow, 'top', rowPadding, lastRowControl)])
				lastRowControl = tempRow

		################
		################
		#Implement variable int fields
		################
		################
		self.grade_boxes = rootXMLElement.findall('grade_box')
		self.log('self.grade_boxes found: {}'.format(len(self.grade_boxes)))
		for box in self.grade_boxes:
			self.log('{}: found'.format(box.get('title')))

		self.log('Create grade boxes')
		if len(self.grade_boxes) > 0:
			for box in self.grade_boxes:
				tempList = []
				if box.get('title') == 'Late':
					tempList.append(box.get('title')[:4])
				else:
					tempList.append(box.get('title')[:3])
				self.log('Box title: %s' % tempList[0])
				tempRow = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
				cmds.text(label = tempList[0], width = 30)
				tempList.append(cmds.intField(value = 0, width = 30, editable = True, backgroundColor = (0.4,0.4,0.4), changeCommand = self.calculateTotal, enable = False))
				self.log('intField lives at: %s' % tempList[1])
				tempList.append('100')
				self.log('box weight: {}'.format(tempList[2]))
				cmds.setParent(tempRow)
				cmds.setParent(parent)


				self.catGrades.append(tempList)

				cmds.formLayout(parent, edit = True, attachForm = [
					(tempRow, 'left', rowPadding), (tempRow, 'right', rowPadding)
					])
				if cycleCount == 0:
					cmds.formLayout(parent, edit = True, attachForm = [(tempRow, 'top', rowPadding)])
					cycleCount += 1
					lastRowControl = tempRow
				else:
					cmds.formLayout(parent, edit = True, attachControl = [(tempRow, 'top', rowPadding, lastRowControl)])
					lastRowControl = tempRow


		# row1 = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
		# cmds.text(label = 'Late', width = 30)
		# lateIntField = cmds.intField(value = 0, width = 30, editable = True, backgroundColor = (0.4,0.4,0.4), changeCommand = self.calculateTotal, enable = False)
		# self.catGrades.append(('Late', lateIntField, '100'))
		# cmds.setParent(row1)
		# cmds.setParent(parent)


		totalSeparator = cmds.separator()
		row2 = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
		cmds.text(label = 'Total', width = 30)
		gradeTotalIntField = cmds.intField(value = 0, width = 30, editable = False, backgroundColor = (0.5,0.5,0.5))
		self.catGrades.append(('Total', gradeTotalIntField, '100'))
		cmds.setParent(row2)
		cmds.setParent(parent)

		# BEFORE THE EDIT!!
		# cmds.formLayout(parent, edit = True, attachForm = [
		# 	(row1, 'left', rowPadding), (row1, 'right', rowPadding),
		# 	(totalSeparator, 'left', rowPadding), (totalSeparator, 'right', rowPadding), 
		# 	(row2, 'left', rowPadding), (row2, 'right', rowPadding)
		# 	],
		# 	attachControl = [
		# 	(row1, 'top', rowPadding, lastRowControl),
		# 	(totalSeparator, 'top', rowPadding, row1),
		# 	(row2, 'top', rowPadding, totalSeparator)])

		cmds.formLayout(parent, edit = True, attachForm = [
			(totalSeparator, 'left', rowPadding), (totalSeparator, 'right', rowPadding), 
			(row2, 'left', rowPadding), (row2, 'right', rowPadding)
			],
			attachControl = [
			(totalSeparator, 'top', rowPadding, lastRowControl),
			(row2, 'top', rowPadding, totalSeparator)])

	def setGradeValues(self, categoryTitleGradeLists):
		self.log('setting grade intField values')
		sectionGradeList = categoryTitleGradeLists
		for section in sectionGradeList:
			self.log('verify section:')
			self.log(section)
			for sectionIntField in self.catGrades:
				self.log('for sectionIntField: %s' % sectionIntField[0])
				self.log('section letters are: %s' % section[0][:3])
				if section[0][:3] == sectionIntField[0]:
					self.log('Its a match!')
					cmds.intField(sectionIntField[1], edit = True, value = section[2])
				else: 
					self.log('No match.')
		self.calculateTotal()

	def enable(self):
		for field in self.catGrades:
			for box in self.grade_boxes:
				self.log('field:{}\nbox:{}'.format(field[0], box.get('title')))
				if field[0] == 'Late' == box.get('title')[:4]:
					cmds.intField(field[1], edit = True, enable = True)
				elif field[0] == box.get('title')[:3]:
					cmds.intField(field[1], edit = True, enable = True)

	def disable(self):
		for field in self.catGrades:
			for box in self.grade_boxes:
				self.log('field:{}\nbox:{}'.format(field[0], box.get('title')))
				if field[0] == 'Late' == box.get('title')[:4]:
					cmds.intField(field[1], edit = True, enable = False)
				elif field[0] == box.get('title')[:3]:
					cmds.intField(field[1], edit = True, enable = False)

	def collect_grades(self):
		self.log('Collect category grades')
		#return a list of lists for grade_boxes
		return_list = []
		return_list.append('grade_boxes_internal') #title
		return_list.append(100) #100% weighting
		return_list.append('') #fake 'highnotes'
		grade_box_list = [] #fake 'subcategory' list, holds grading box info
		for field in self.catGrades:
			for box in self.grade_boxes:
				self.log('field:{}\nbox:{}'.format(field[0], box.get('title')))
				if field[0] == 'Late' == box.get('title')[:4]:
					grade_box_list.append({
						'section_title': field[0], 
						'section_weight': 100,
						'grade_value' : cmds.intField(field[1], query = True, value = True),
						'comment_text' : '',
						'default_comments_text' : box.text,
						'example_comments_text' : '',
						'is_complete': True
									})
				elif field[0] == box.get('title')[:3]:
					grade_box_list.append({
						'section_title': field[0], 
						'section_weight': 100,
						'grade_value' : cmds.intField(field[1], query = True, value = True),
						'comment_text' : '',
						'default_comments_text' : box.text,
						'example_comments_text' : '',
						'is_complete': True
									})
		return_list.append(0)
		return_list.append(grade_box_list)
		return return_list

	def set_pickle_grades(self, gradeInfo):
		self.log('set grades')
		self.log('grade info: {}'.format(gradeInfo))
		for box in gradeInfo[4]:
			self.log('Box: {}'.format(box))
		for field in self.catGrades:
			for box in gradeInfo[4]:
				self.log('field:{}\nbox:{}'.format(field[0], box['section_title']))
				if field[0] == 'Late' == box['section_title'][:4]:
					cmds.intField(field[1], edit = True, value = box['grade_value'])
				elif field[0] == box['section_title'][:3]:
					cmds.intField(field[1], edit = True, value = box['grade_value'])


	# def lateDeduction(self):
	# 	return cmds.intField(self.catGrades[-2][1], query = True, value = True)

	def gradeTotal(self):
		return cmds.intField(self.catGrades[-1][1], query = True, value = True)

	def reset(self):
		self.log('resetting late grade field?')

		for field in self.catGrades:
			for box in self.grade_boxes:
				self.log('field:{}\nbox:{}'.format(field[0], box.get('title')))
				if field[0] == 'Late' == box.get('title')[:4]:
					cmds.intField(field[1], edit = True, value = 0)
				elif field[0] == box.get('title')[:3]:
					cmds.intField(field[1], edit = True, value = 0)
		# cmds.intField(self.catGrades[-2][1], edit = True, value = 0)
		self.log('late grade field set')
		self.calculateTotal()


	def calculateTotal(self, *args):
		equation = self.gradeEquation
		for section in self.catGrades:
			self.log('Section: {}'.format(section[0]))
		for section in self.catGrades:
			self.log('section title: {}'.format(section[0]))
			self.log('section int field value: {}'.format(cmds.intField(section[1], query = True, value = True)))
			grade = cmds.intField(section[1], query = True, value = True)
			equation = equation.replace(section[0], str(round(grade * (float(section[2])/100.0), 2)))
			self.log('equation: {}'.format(equation))
		self.log('Grade Total Eval: {}'.format(eval(equation)))
		#
		#
		#
		### HERE!!! FLoat to int! (perhaps round?)###
		#
		#
		#
		gradeTotalValue = eval(equation)
		if gradeTotalValue <= 0: gradeTotalValue = 0
		self.log('Grade Total Value: {}'.format(gradeTotalValue))
		cmds.intField(self.catGrades[-1][1], edit = True, value = gradeTotalValue)
		# if cmds.intField(self.catGrades[-2][1], query = True, value = True) != 0:
		# 	self.isLate = True
		# 	self.log('isLate: {}'.format(self.isLate))
		# else:
		# 	self.isLate = False
		# 	self.log('isLate: {}'.format(self.isLate))

	def log(self, message, prefix = '.:Generate Category Grades::', hush = True):
		"""
		print stuff yo!
		"""
		if not hush:
			print "%s: %s" % (prefix, message)


