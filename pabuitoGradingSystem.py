"""
 This class controls the main window of the pabuito Grading System. It deals with tabbing the main sections as well as holding all the relavent information. 

"""


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
reload(category_class)
reload(fileManagerFile)


class PabuitoGradingSystem(object):

	def __init__(self, xmlFileLocation):

		self.development = True

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
		longestElement = 0
		for cat in self.xml_elementMainCategories:
			if len(cat.findall('subcategory')) > longestElement:
				longestElement = len(cat.findall('subcategory'))

		self.windowWidth = 300
		subcategoryHeight = (longestElement * 100)
		windowBufferHeight = 55
		if (subcategoryHeight + windowBufferHeight) > 825:
			self.windowHeight = 825
		elif (subcategoryHeight + windowBufferHeight) < 465:
			self.windowHeight = 465
		else:
			self.windowHeight = (subcategoryHeight + windowBufferHeight)
		if subcategoryHeight < 410:
			subcategoryHeight = 410

		self.uiPadding = 2

		self.outputModel = 'root'
		self.runAuto = True

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
		cmds.button (label = "Load Directory", width = buttonWidth, command = lambda *args:self.fileManager.runFileManager(1, self.enableStart), enable = not (self.loadedByPickle))
		cmds.button (label = "Load All", width = 2, command = lambda *args:self.fileManager.runFileManager(2), enable = not (self.loadedByPickle), visible = False)
		self.startButton = cmds.button (label = "Start", width = buttonWidth, command = lambda *args: self.startGrading(), enable = False)
		cmds.popupMenu(parent = self.startButton, button = 3)
		self.startRootMenuItem = cmds.menuItem(label = '-> Root Placement', command = lambda *args:self.outputModelFunction('root'))
		self.startSaksonMenuItem = cmds.menuItem(label = 'Sakson Placement', command = lambda *args: self.outputModelFunction('sakson'))
		if self.development:
			self.startDevelopmentMenuItem = cmds.menuItem(label = 'Development', command = lambda *args: self.outputModelFunction('development'))
		self.startRunAutoMenuItem = cmds.menuItem(label = 'RunAuto - On', command = lambda *args: self.runAutoToggle())

		##End top button area
		cmds.setParent('topRow')
		cmds.setParent('rootLayout')

		resetWidth = 25
		nextWidth = 40
		self.topRowTwo = cmds.rowLayout('topRow2', numberOfColumns = 3, visible = False)
		cmds.button(label = 'X', width = resetWidth, command = lambda *args: self.resetTool(restart = True), enable = not (self.loadedByPickle))
		self.activeProjectTextField = cmds.textField(text = 'Active Project.ma', editable = False, width = ((buttonWidth*2)-(resetWidth + nextWidth + 2)))
		self.nextFileButton = cmds.button(label = '-->', width = nextWidth, command = lambda *args: self.runNextFile())
		cmds.popupMenu(parent = self.nextFileButton, button = 3)
		self.rootMenuItem = cmds.menuItem(label = '-> Root Placement', command = lambda *args:self.outputModelFunction('root'))
		self.saksonMenuItem = cmds.menuItem(label = 'Sakson Placement', command = lambda *args: self.outputModelFunction('sakson'))
		if self.development:
			self.developmentMenuItem = cmds.menuItem(label = 'Development', command = lambda *args: self.outputModelFunction('development'))
		self.runAutoMenuItem = cmds.menuItem(label = 'RunAuto - On', command = lambda *args: self.runAutoToggle())
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
		self.pgs_tabLayout = cmds.tabLayout( width = 215, height = subcategoryHeight )

		
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

		##old file reading style
		# pickleFileObject = open(pickleFile, 'r')
		# unpackedPickleInfo = pickle.loads(pickleFileObject.read())
		# pickleFileObject.close()
		self.xml_elementTree = unpackedPickleInfo[0]
		self.loadedGradeInfo = unpackedPickleInfo[1]
		self.loadedFileInfo = unpackedPickleInfo[2]
		self.loadedFileInfo['pickleDirectory'] = pickleFile
		self.loadedByPickle = True

	def startGrading(self, *args):
		self.log('Start Grading!')
		firstFile = self.fileManager.what_is_the_next_file()
		if firstFile == None:
			cmds.error('No files loaded. Please load files into PGS.')
		self.log('The first file is: {}'.format(firstFile[1]))
		cmds.textField(self.activeProjectTextField, edit = True, text = firstFile[1])
		self.log('first file path is: \n {}'.format(firstFile[0]))
		self.visSwap(1)
		cmds.file(force = True, newFile = True)
		cmds.file(firstFile[0], open = True)
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

	def disableStart(self):
		cmds.button(self.startButton, edit = True, enable = False)

	def disable(self):
		self.categoryGrades.disable()
		for cat in self.mainCategories:
			cat.disable()

	def toolIsComplete(self):
		for cat in self.mainCategories:
			if not cat.are_you_complete():
				return False
		return True

	def runNextFile(self):
		self.log('This method will run all methods necessary to move from one file to another')
		if self.toolIsComplete():
			self.log('The tool is complete')
		else: 
			self.log('\n\n')
			if self.development:
				cmds.warning('Tool is not complete!')
			else: 
				cmds.error('PGS not complete. Please complete all grade sections.')
			self.log('\n\n')
		self.log('output grade')
		self.handleOutput()
		self.log('cycle the active file to the completed list')
		# if doCycle:
		self.fileManager.cycle_file()
		nextFile = self.fileManager.what_is_the_next_file()
		if nextFile != None:
			# doCycle = True
			cmds.textField(self.activeProjectTextField, edit = True, text = nextFile[1])
			self.log('clear the gradeTool grades')
			self.resetTool()
			self.disable()
			self.log('New Maya Scene')
			cmds.file(force = True, newFile = True)
			self.log('load the next Maya file')
			cmds.file(nextFile[0], open = True)
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

	def writeOutputFile(self, grades, directoryDict):
		self.log('write output file to directory')

		#make pickle directory, if it exists...OK!
		try:
			os.makedirs(directoryDict['textDirectory'])
		except OSError as exception:
			if exception.errno != errno.EEXIST:
				raise

		lineSeparator = '-----------------------------\n'
		smallLineSeparator = '----------\n'
		self.log('filename: {}'.format(directoryDict['filename']))
		self.log('text path: {}'.format(directoryDict['textDirectory']))
		with open(directoryDict['textDirectory'] + directoryDict['filename'] + '.txt', 'w') as f:
			f.write('Grading for: {}\n'.format(directoryDict['filename']))
			f.write(lineSeparator)
			for section in grades:
				f.write('{}: {}%\n'.format(section[0],section[3]))
				f.write(lineSeparator)
				f.write(lineSeparator)

				#highnotes
				if section[2] != '':
					try:
						highnoteIntro = self.xml_elementDefaults.find('highnote_intro').textField
						if highnoteIntro != None: 
							f.write('{}\n'.format(highnoteIntro))
					except AttributeError:
						pass
					f.write('{}\n'.format(section[2]))
					f.write(lineSeparator)
				for subSection in section[4]:
					#section title
					f.write('{}\n'.format(subSection['section_title']))
					f.write(lineSeparator)
					#comment text
					if subSection['comment_text'] !='':
						try:
							comment_textIntro = self.xml_elementDefaults.find('comment_intro').text
							if comment_textIntro != None: 
								f.write('{}\n'.format(comment_textIntro))
						except AttributeError:
							pass
						f.write('{}\n'.format(subSection['comment_text']))
						f.write(smallLineSeparator)

					#default comments text
					if subSection['default_comments_text'] !='':
						try:
							default_comments_textIntro = self.xml_elementDefaults.find('default_comment_intro').text
							if default_comments_textIntro != None: 
								f.write('{}\n'.format(default_comments_textIntro))
						except AttributeError:
							pass
						f.write('{}\n'.format(subSection['default_comments_text']))
						f.write(smallLineSeparator)

					#example comments text
					if subSection['example_comments_text'] !='':
						try:
							example_comments_textIntro = self.xml_elementDefaults.find('example_object_intro').text
							if example_comments_textIntro != None: 
								f.write('{}\n'.format(example_comments_textIntro))
						except AttributeError:
							pass
						f.write('{}\n'.format(subSection['example_comments_text']))
						f.write(smallLineSeparator)

				f.write(lineSeparator)

			f.write(lineSeparator)
			for section in grades:
				f.write('{}: {}%\n'.format(section[0],section[3]))
				f.write(smallLineSeparator) 

			#Late  text
			if self.categoryGrades.isLate:
				try:
					late_textIntro = self.xml_elementDefaults.find('late_intro').text
					if late_textIntro != None: 
						f.write(lineSeparator)
						f.write('{}'.format(late_textIntro))
				except AttributeError:
					pass
				f.write('{}\n'.format(self.categoryGrades.lateDeduction()))
				f.write(lineSeparator)

			#grade total  text
			try:
				gradeTotal_textIntro = self.xml_elementDefaults.find('total_intro').text
				if gradeTotal_textIntro != None: 
					f.write(lineSeparator)
					f.write('{}'.format(gradeTotal_textIntro))
			except AttributeError:
				pass
			f.write('{}\n'.format(self.categoryGrades.gradeTotal()))

	def writePickleFile(self, grades, directoryDict):
		#make pickle directory, if it exists...OK!
		# try:
		# 	os.makedirs(directoryDict['pickleDirectory'])
		# except OSError as exception:
		# 	if exception.errno != errno.EEXIST:
		# 		raise
				
		self.log('write cPickle file')
		pickleBuild = (self.xml_elementTree, grades, directoryDict)
		pickleToWrite = pickle.dumps(pickleBuild)
		pickleFile = open(directoryDict['pickleDirectory'] + directoryDict['filename'] + '.pgs', 'w')
		pickleFile.write(pickleToWrite)
		pickleFile.close()

	def gatherGrades(self):
		gradesForPickle = []
		for cat in self.mainCategories:
			gradesForPickle.append(cat.what_is_the_grade())
		for index in gradesForPickle:
			self.log('Grades from cat {} : {}'.format(index[0], index))
		return gradesForPickle

	def restartTool(self):
		self.log('reset PGS grade tool')
		for cat in self.mainCategories:
			cat.disable()
		cmds.button(self.startButton, edit = False, enable = False)
		self.disableStart()
		self.visSwap(2)
		self.fileManager.reset()
		self.categoryGrades.disable()

	def resetTool(self, restart = False):
		self.log('reset PGS grade tool')
		for cat in self.mainCategories:
			cat.reset()
		self.categoryGrades.reset()
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
		self.isLate = False
		for cat in mainCategories:
			tempList = []
			tempList.append(cat.find('title').text[:3])
			self.log('cat title: %s' % tempList[0])
			tempRow = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
			cmds.text(label = tempList[0], width = 30)
			tempList.append(cmds.intField(value = 0, width = 30, editable = False, backgroundColor = (0.5,0.5,0.5)))
			self.log('intField lives at: %s' % tempList[1])
			tempList.append(cat.find('weight').text)
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

		row1 = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
		cmds.text(label = 'Late', width = 30)
		lateIntField = cmds.intField(value = 0, width = 30, editable = True, backgroundColor = (0.4,0.4,0.4), changeCommand = self.calculateTotal, enable = False)
		self.catGrades.append(('Late', lateIntField, '100'))
		cmds.setParent(row1)
		cmds.setParent(parent)
		totalSeparator = cmds.separator()
		row2 = cmds.rowLayout(numberOfColumns = 2, columnAlign2 = ['left', 'right'])
		cmds.text(label = 'Total', width = 30)
		gradeTotalIntField = cmds.intField(value = 0, width = 30, editable = False, backgroundColor = (0.5,0.5,0.5))
		self.catGrades.append(('Total', gradeTotalIntField, '100'))
		cmds.setParent(row2)
		cmds.setParent(parent)

		cmds.formLayout(parent, edit = True, attachForm = [
			(row1, 'left', rowPadding), (row1, 'right', rowPadding),
			(totalSeparator, 'left', rowPadding), (totalSeparator, 'right', rowPadding), 
			(row2, 'left', rowPadding), (row2, 'right', rowPadding)
			],
			attachControl = [
			(row1, 'top', rowPadding, lastRowControl),
			(totalSeparator, 'top', rowPadding, row1),
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
					# if section[0][:3] in equation:
					# 	self.log('the bit is in there... ')
					# equation = equation.replace(str(section[0][:3]),(str(((section[2]/100) * float(section[1])))))
					# self.log('new equation: {}'.format(equation))
				else: 
					self.log('No match.')
		self.calculateTotal()

	def enable(self):
		cmds.intField(self.catGrades[-2][1], edit = True, enable = True)

	def disable(self):
		cmds.intField(self.catGrades[-2][1], edit = True, enable = False)

	def lateDeduction(self):
		return cmds.intField(self.catGrades[-2][1], query = True, value = True)

	def gradeTotal(self):
		return cmds.intField(self.catGrades[-1][1], query = True, value = True)

	def reset(self):
		self.log('resetting late grade field?')
		cmds.intField(self.catGrades[-2][1], edit = True, value = 0)
		self.log('late grade field set')
		self.calculateTotal()

	def calculateTotal(self, *args):
		equation = self.gradeEquation
		for section in self.catGrades:
			self.log('section title: {}'.format(section[0]))
			self.log('section int field value: {}'.format(cmds.intField(section[1], query = True, value = True)))
			grade = cmds.intField(section[1], query = True, value = True)
			equation = equation.replace(section[0], str(grade * (float(section[2])/100.0)))
			self.log('equation: {}'.format(equation))
		gradeTotal = eval(equation)
		if gradeTotal <= 0: gradeTotal = 0
		cmds.intField(self.catGrades[-1][1], edit = True, value = gradeTotal)
		if cmds.intField(self.catGrades[-2][1], query = True, value = True) != 0:
			self.isLate = True
			self.log('isLate: {}'.format(self.isLate))
		else:
			self.isLate = False
			self.log('isLate: {}'.format(self.isLate))

	def log(self, message, prefix = '.:Generate Category Grades::', hush = True):
		"""
		print stuff yo!
		"""
		if not hush:
			print "%s: %s" % (prefix, message)


