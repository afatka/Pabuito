"""
This class handles the file management portion of the grade tool. It will be a tab placed into the existing PGS grade tool 

This tab should contain a single parent that can be loaded as a child into a tabLayout or window element

Created by Adam Fatka :: adam.fatka@gmail.com
"""

import maya.cmds as cmds
import os 
# import codeTimer
# reload(codeTimer)



class FileManager(object):

	def __init__(self, fileTypesToFind = ('.mb', '.ma')):
		#control log silencing
		self.development = False

		self.toolStarted = False
		self.uiPadding = 2
		#input args
		# self.pathType = pathSelection #1 is singleSection, 2 is allSections
		self.fileTypes = fileTypesToFind

		#possibly make it work on windows as well? no testing done
		if os.name == 'posix':
			self.fileSeparator = '/'
		else: self.fileSeparator = "\\"

		#declaration of variables
		
		self.completedFiles = []
		

		#build GUI
		self.fileManagerGUI()

	def runFileManager(self, pathSelection, *args):

		self.directoryContentPaths = []
		self.foundFiles = []
		self.pathType = pathSelection#1 is singleSection, 2 is allSections

		#ID working directory, make that directory functional
		workingDirectory = cmds.fileDialog2(fileMode = 3, caption = 'Select Directory')[0] + self.fileSeparator
		self.log('working directory: {}'.format(workingDirectory))
		self.workingDirectoryOSWalk = workingDirectory

		if os.path.isdir(workingDirectory):
			self.log('workingDirectory is a directory')

		#capture contents of the workingDirectory, strip out 'extra'/ignore files
		directoryContents = self.stripFiles(os.listdir(workingDirectory))
		self.log('new directoryContents: {}'.format(directoryContents))

		
		for item in directoryContents:
			self.directoryContentPaths.append(workingDirectory + item)
		self.log('new item with path: {}'.format(self.directoryContentPaths))

		try:
			self.log('prefoundFiles declare: {}'.format(self.foundFiles))
		except:
			pass
		self.log('found Files: {}'.format(self.foundFiles))


		######
		######
		# with codeTimer.codeTimer('FileFinder', development = self.development ) as timer:
		# 	#find files
		# 	# self.fileFinder()
		self.fileFinderOSWalk()
		######
		######


		self.log('{} maya files found'.format(len(self.foundFiles)))
		self.log('Maya files: {}'.format(self.foundFiles))

		
		for fileItem in self.foundFiles:

			self.log('All Items in Completed: \n{}'.format(cmds.textScrollList(self.completeFilesScrollList, query = True, allItems = True)))
			self.log('item is: {}'.format(fileItem))
			completedFilesTempList = cmds.textScrollList(self.completeFilesScrollList, query = True, allItems = True)
			if completedFilesTempList is not None:
				if fileItem.rsplit(self.fileSeparator)[-1] in completedFilesTempList:
					self.log('added file is in completed list')
					cmds.textScrollList(self.completeFilesScrollList, edit = True, removeItem = fileItem.rsplit(self.fileSeparator)[-1])

			self.log('file name: {}'.format(fileItem.rsplit(self.fileSeparator)[-1]))
			incompleteFilesTempList = cmds.textScrollList(self.incompleteFilesScrollList, query = True, allItems = True)
			try: 
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, append = [fileItem.rsplit(self.fileSeparator)[-1]], uniqueTag = [fileItem])
			except RuntimeError:
				cmds.warning('File already in Queue, Ignoring File.')
		if args:
			self.log('args detected: \n {}'.format(args))
			try: 
				for x in args:
					x()
			except:
				raise

	def grade_next(self, *args):
		self.log('send selection to next')
		currentSelection = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		currentSelectionUniqueTags = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
		if currentSelection == None:
			cmds.error('No item selected')
		i = 1
		if self.toolStarted:
			i = 2
		i2 = 0
		for item in currentSelection:
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeItem = item)	
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True,  appendPosition = [i, item], uniqueTag = currentSelectionUniqueTags[i2])
			i += 1
			i2 += 1

	def send_to_last(self, *args):
		self.log('send selection to last')
		currentSelection = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		currentSelectionUniqueTags = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
		if currentSelection == None:
			cmds.error('No item selected')
		i = 0
		for item in currentSelection:
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeItem = item)	
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True,  append = item, uniqueTag = currentSelectionUniqueTags[i])
			i += 1

	def what_is_the_next_file(self):
		original_selected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		if original_selected == None:
			try:
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, selectIndexedItem = [1])
			except RuntimeError:
				self.log('No Files to Select')
				next_file = None
				return next_file 
			next_file = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, deselectIndexedItem = [1])
		else: 
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, deselectAll = True)
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, selectIndexedItem = [1])
			next_file = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, deselectAll = True)
			for item in original_selected:
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, selectItem = item)
		return next_file[0], next_file[0].rsplit(self.fileSeparator)[-1]

	def what_is_the_current_file(self):
		currentFile = cmds.textScrollList(self.incompleteFilesScrollList, query = True, allItems = True)
		return currentFile[0]

	def currentPath(self, directoryType):
		self.log('directoryType: {}'.format(directoryType))
		currentFileWPath = cmds.file(query = True, sceneName = True)
		currentFilename = cmds.file(query = True, sceneName = True, shortName = True)
		maxSplit = 2
		if directoryType is 'sakson':
			maxSplit = 1
		self.log('maxSplit is: {}'.format(maxSplit))
		workingDirectory = currentFileWPath.rsplit(self.fileSeparator,maxSplit)[0]
		if directoryType is 'sakson':
			workingDirectory += self.fileSeparator
			pickleDirectory = workingDirectory
		else:
			pickleDirectory = currentFileWPath.rsplit(self.fileSeparator,1)[0] + self.fileSeparator
			workingDirectory += '_gradeFiles' + self.fileSeparator
		return {'filename' : currentFilename, 'textDirectory' : workingDirectory, 'pickleDirectory' : pickleDirectory}

	def is_last_file(self):
		self.log('Is this the last file?')
		itemCount = cmds.textScrollList(self.incompleteFilesScrollList, query = True, numberOfItems = True)
		if itemCount == 1:
			return True
		return False

	def cycle_file(self, *args):
		original_selected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		cmds.textScrollList(self.incompleteFilesScrollList, edit = True, deselectAll = True)
		cmds.textScrollList(self.incompleteFilesScrollList, edit = True, selectIndexedItem = [1])
		self.markAsComplete()
		cmds.textScrollList(self.incompleteFilesScrollList, edit = True, deselectAll = True)
		if original_selected != None:
			for item in original_selected:
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, selectItem = item)

	def markAsComplete(self, *args):
		selected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		selectedUniqueTags = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
		i = 0
		if selected != None:
			for item in selected:
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeItem = item)
				cmds.textScrollList(self.completeFilesScrollList, edit = True, append = item, uniqueTag = selectedUniqueTags[i])
				i+=1
		else: cmds.warning('No item selected from incompleted list.')

	def markAsIncomplete(self, *args):
		selected = cmds.textScrollList(self.completeFilesScrollList, query = True, selectItem = True)
		selectedUniqueTags = cmds.textScrollList(self.completeFilesScrollList, query = True, selectUniqueTagItem = True)
		i = 0
		if selected != None:
			for item in selected:
				cmds.textScrollList(self.completeFilesScrollList, edit = True, removeItem = item)
				cmds.textScrollList(self.incompleteFilesScrollList, edit = True, append = item, uniqueTag = selectedUniqueTags[i])
				i+=1
		else: cmds.warning('No item selected from completed list.')

	def scrollListSelectCommand(self):
		if self.development:
			selected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
			self.log('selected is: {}'.format(selected))
			uniqueSelected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
			self.log('path: {}'.format(uniqueSelected))

	def stripFiles(self, directoryList):
		ignoreFiles = [".DS_Store", "workspace.mel"] 
		for item in ignoreFiles:
			if item in directoryList:
				directoryList.remove(item)
		return directoryList

	def fileFinderOSWalk(self, *args):
		for directoryName, subDirectoryName, fileList in os.walk(self.workingDirectoryOSWalk):
			for item in fileList:
				if item.endswith(self.fileTypes):
					self.log('directory name is: {}'.format(directoryName))
					self.log('file name: {}'.format(item))
					if directoryName.endswith(self.fileSeparator):
						fileToAdd = directoryName + item
					else:
						fileToAdd = directoryName + self.fileSeparator + item
					self.foundFiles.append(fileToAdd)

	# def fileFinder(self):
	# 	if self.pathType == 2:
	# 		# self.log('pathType is allSections')
	# 		for item in self.directoryContentPaths:
	# 			# self.log('looking in directoryContentPaths at {}'.format(item))
	# 			# self.log('os.path.isdir = {}'.format(os.path.isdir(item)))
	# 			if os.path.isdir(item):
	# 				# self.log('{} is a directory'.format(item))
	# 				tempContents = self.stripFiles(os.listdir(item))
	# 				# self.log('capturing dir contents: {}'.format(tempContents))
	# 				tempContentsPaths = []
	# 				for content in tempContents:
	# 					tempContentsPaths.append(item + self.fileSeparator + content)
	# 				# self.log('tempContentsPaths: {}'.format(tempContentsPaths))
	# 				for newItem in tempContentsPaths:
	# 					# self.log('looking at path: {}'.format(newItem))
	# 					# self.log('os.path.isdir: {}'.format(os.path.isdir(newItem)))
	# 					if os.path.isdir(newItem):
	# 						# self.log('os.isdir: True - {}'.format(newItem))
	# 						tempContents2 = self.stripFiles(os.listdir(newItem))
	# 						for fileItem in tempContents2:
	# 							if fileItem.endswith(self.fileTypes):
	# 								self.foundFiles.append(newItem + self.fileSeparator + fileItem)
	# 								# self.log('Maya File Added to List: {}'.format(fileItem))

	# 	if self.pathType == 1:
	# 		# self.log('pathType is singleSection')
	# 		for item in self.directoryContentPaths:
	# 			# self.log('looking at: {}'.format(item))
	# 			if os.path.isdir(item):
	# 				tempContents = self.stripFiles(os.listdir(item))
	# 				for fileItem in tempContents:
	# 					if fileItem.endswith(self.fileTypes):
	# 						self.foundFiles.append(item + self.fileSeparator + fileItem)


	def findPicklesFile(self, picklesFileDict):
		self.log('pickles file name is: {}'.format(picklesFileDict['filename']))
		self.log('We will look for the maya file here: {}'.format(picklesFileDict['pickleDirectory']))
		picklesFileName = picklesFileDict['filename']
		pickleDirectory = picklesFileDict['pickleDirectory'].rsplit(self.fileSeparator,1)[0]
		picklesMayaFile = pickleDirectory + self.fileSeparator + picklesFileName
		if os.path.isfile(picklesMayaFile):
			self.log('the file exists!')
			self.addFile(path = picklesMayaFile)
		else:
			self.addFile(cmds.fileDialog2(fileMode = 1, caption = 'Select associated Maya file')[0])

	def addFile(self, path = None, *args):
		self.log('Add a File to Queue')
		self.log('path is: {}'.format(path))
		if not path:
			newFile = cmds.fileDialog2(fileMode = 4, caption = 'Select files to add')
		else: 
			self.log('newFile = path: {}'.format(path))
			newFile = [path]
		self.log('New files \n {}'.format(newFile))
		if newFile:
			for item in newFile:
				self.log('All Items in Completed: \n{}'.format(cmds.textScrollList(self.completeFilesScrollList, query = True, allItems = True)))
				self.log('item is: {}'.format(item))
				tempList = cmds.textScrollList(self.completeFilesScrollList, query = True, allItems = True)
				if tempList is not None:
					if item.rsplit(self.fileSeparator)[-1] in tempList:
						self.log('added file is in completed list')
						cmds.textScrollList(self.completeFilesScrollList, edit = True, removeItem = item.rsplit(self.fileSeparator)[-1])
				try:
					cmds.textScrollList(self.incompleteFilesScrollList, edit = True, append = item.rsplit(self.fileSeparator)[-1], uniqueTag = item)
					self.log('File: {}, appended. \n Path: {}'.format(item.rsplit(self.fileSeparator)[-1], item))
				except RuntimeError:
					cmds.warning('File Already in Queue')

	def removeFile(self, *args):
		self.log('Remove a File from Queue')
		incompleteFilesSelected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		incompleteFilesSelectedUniqueTags = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectUniqueTagItem = True)
		completeFilesSelected = cmds.textScrollList(self.completeFilesScrollList, query = True, selectItem = True)
		completeFilesSelectedUniqueTags = cmds.textScrollList(self.completeFilesScrollList, query = True, selectUniqueTagItem = True)
		selected = []
		removalString = ''
		if  incompleteFilesSelected is not None:
			removalString += 'Remove {} queued files?'.format(len(incompleteFilesSelected))
			for selectedFile in incompleteFilesSelected:
				selected.append(selectedFile)
		if completeFilesSelected is not None:
			removalString += '\nRemove {} graded files'.format(len(completeFilesSelected))
			for selectedFile in completeFilesSelected:
				selected.append(selectedFile)
		self.log('selected: {}'.format(selected))
		if selected:
			if cmds.confirmDialog( title='Confirm Removal,\n Are you sure?', message=removalString, button=['Remove File','Cancel'], defaultButton='Remove File', cancelButton='Cancel', dismissString='No' ) == 'Remove File':
				for item in selected:
					self.log('removing file: {}'.format(item))
					if item in incompleteFilesSelected:
						cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeItem = item)
					else:
						cmds.textScrollList(self.completeFilesScrollList, edit = True, removeItem = item)
					self.log('Removed file: {}'.format(item))
		else: cmds.warning('No item selected from lists for removal.')

	def removeCompletedFile(self, *args):
		self.log('remove complted file')
		completeFilesSelected = cmds.textScrollList(self.completeFilesScrollList, query = True, selectItem = True)
		for item in completeFilesSelected:
			cmds.textScrollList(self.completeFilesScrollList, edit = True, removeItem = item)

	def removeIncompleteFile(self, *args):
		self.log('remove complted file')
		incompleteFilesSelected = cmds.textScrollList(self.incompleteFilesScrollList, query = True, selectItem = True)
		for item in incompleteFilesSelected:
			cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeItem = item)

	def loadedByPickle(self, *args):
		self.log('Adjusting file manger for pickle loading')
		cmds.textScrollList(self.incompleteFilesScrollList, edit = True, enable = False)
		cmds.textScrollList(self.completeFilesScrollList, edit = True, enable = False)
		cmds.button(self.addFileButton, edit = True, enable = False)
		cmds.button(self.removeFileButton, edit = True, enable = False)
		cmds.button(self.markAsIncompleteButton , edit = True, enable = False)
		cmds.button(self.markAsCompleteButton , edit = True, enable = False)

	def fileManagerGUI(self):
		"""
		Stand alone GUI element. Single UI Parent required to return
		"""

		doWindow = False
		scrollListWidth = 75
		scrollListHeight = 155
		buttonWidth = 102
		if doWindow:
			cmds.window(width = scrollListWidth)
		self.fileManagerFormLayout = cmds.formLayout('fileManager Form Layout', numberOfDivisions = 200)
		self.addFileButton = cmds.button(label = 'Add File +', command = lambda *args: self.runFileManager(1), width = buttonWidth)
		# addFilePopupMenu = cmds.popupMenu(parent = self.addFileButton, button = 3)
		# cmds.menuItem(label = 'Add Section +', command = lambda *args: self.runFileManager(1))
		# cmds.menuItem(label = 'Add Project +', command = lambda *args: self.runFileManager(2))
		self.removeFileButton = cmds.button(label = '- Remove File', command = self.removeFile, width = buttonWidth)
		fieldSeparator1 = cmds.separator()
		self.incompleteFilesScrollList = cmds.textScrollList(numberOfRows=10, allowMultiSelection=True, selectCommand = self.scrollListSelectCommand, width = scrollListWidth, height = scrollListHeight, font = "smallObliqueLabelFont", deleteKeyCommand = self.removeIncompleteFile)
		cmds.popupMenu(parent = self.incompleteFilesScrollList, button = 3)
		cmds.menuItem(label = 'Grade Next', command = self.grade_next)
		cmds.menuItem(label = 'Send to Bottom', command = self.send_to_last)
		fieldSeparator2 = cmds.separator()
		self.markAsCompleteButton = cmds.button(label = u'Mark as Done v', command = self.markAsComplete, width = buttonWidth)
		self.markAsIncompleteButton = cmds.button(label = '^ Add to Queue', command = self.markAsIncomplete, width = buttonWidth)
		fieldSeparator3 = cmds.separator()
		self.completeFilesScrollList = cmds.textScrollList(numberOfRows=10, allowMultiSelection=True, width = scrollListWidth, height = scrollListHeight, font = "smallObliqueLabelFont", deleteKeyCommand = self.removeCompletedFile)
		

		cmds.setParent(self.fileManagerFormLayout)
		cmds.formLayout(self.fileManagerFormLayout, edit = True, 
			attachForm = [
			(self.addFileButton, 'top', self.uiPadding),
			(self.addFileButton, 'left', self.uiPadding),
			(self.removeFileButton, 'top', self.uiPadding),
			(self.removeFileButton, 'right', self.uiPadding),
			(fieldSeparator1, 'right', self.uiPadding),
			(fieldSeparator1, 'left', self.uiPadding),
			(self.incompleteFilesScrollList, 'left', self.uiPadding),
			(self.incompleteFilesScrollList, 'right', self.uiPadding),
			(fieldSeparator2, 'right', self.uiPadding), 
			(fieldSeparator2, 'left', self.uiPadding),
			(self.markAsCompleteButton, 'right', self.uiPadding),
			(self.markAsIncompleteButton, 'left', self.uiPadding),
			(fieldSeparator3, 'right', self.uiPadding), 
			(fieldSeparator3, 'left', self.uiPadding),
			(self.completeFilesScrollList, 'left', self.uiPadding),
			(self.completeFilesScrollList, 'right', self.uiPadding),
			],
			attachControl = [
			(self.addFileButton, 'right', self.uiPadding, self.removeFileButton),
			(fieldSeparator1, 'top', self.uiPadding, self.addFileButton),
			(self.incompleteFilesScrollList, 'top', self.uiPadding, fieldSeparator1), 
			(fieldSeparator2, 'top', self.uiPadding, self.incompleteFilesScrollList),
			(self.markAsCompleteButton, 'top', self.uiPadding, fieldSeparator2), 
			(self.markAsCompleteButton, 'right', self.uiPadding, self.markAsIncompleteButton),
			(self.markAsIncompleteButton, 'top', self.uiPadding, fieldSeparator2),
			(fieldSeparator3, 'top', self.uiPadding, self.markAsIncompleteButton),
			(self.completeFilesScrollList, 'top', self.uiPadding, fieldSeparator3)
			])
		if doWindow:
			cmds.showWindow()

	def reset(self):
		self.toolStarted = False
		cmds.textScrollList(self.incompleteFilesScrollList, edit = True, removeAll = True)
		cmds.textScrollList(self.completeFilesScrollList, edit = True, removeAll = True)

	def log(self, message, prefix = '.:File Manager:.'):
		if self.development:
			print ('{0} -- {1}'.format(prefix, message))
