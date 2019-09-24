"""
This class is the most granular section of the Pabuito Grade Tool. 

It takes a subcategory from the xml and generates all GUI components for grading. 

It includes all class attributes required to retrieve and load grading attributes [comments, values, etc]
"""

import maya.cmds as cmds
# import maya.utils
import xml.etree.ElementTree as et
import re, sys
class  SubcategoryGradeSection(object):

	def __init__(self, subcategoryFromXML, defaultsFromXML, updateFunction, runAuto):
		"""
		take the element tree element 'subcategory' from the xml to generate the subcategory section'
		"""
		self.updateFunction  = updateFunction
		self.runAuto = runAuto

		subcategory_width = 200
		scrollField_height = 100
		row_spacing = 0

		self.current_grade_value = 0
		self.current_comment_text = ''
		self.current_default_comment_text = ''
		self.current_example_comment_text = ''
		self.auto_flagged_list = []
		self.is_complete = False

		self.subcatXML = subcategoryFromXML
		self.log('trying to unpack gradeValue from defaults')
		self.log('defaultsFromXML are: %s' % defaultsFromXML)
		self.grade_values = defaultsFromXML.find('gradeValue')
		self.log('grade_values: %s' % self.grade_values)

		self.title = self.subcatXML.get('title')
		if self.title == None:
			self.title = self.subcatXML.find('title').text

		self.weight = self.subcatXML.get('weight')
		if self.weight == None:
			self.weight = self.subcatXML.find('weight').text

		# self.title = self.subcatXML.find('title').text
		# self.log('section title: %s' % self.title)

		# self.weight = self.subcatXML.find('weight').text
		# self.log('section weight: %s' % self.weight)

		try: 
			self.auto = self.subcatXML.find('auto').text
		except AttributeError: 
			self.auto = ''

		self.rmb = []
		if self.subcatXML.findall('RMB'):
			for item in self.subcatXML.findall('RMB'):
				self.rmb.append([item.get('title'), item.text])

		self.log('\nRiGHT HERE!')
		if self.rmb != []:
			for item in self.rmb:
				self.log('\nTitle: {}\n{}'.format(item[0], item[1]))
		self.log('RMB: {}'.format(self.rmb))
		
		self.log('starting subcategory GUI')
		self.subcat_main_column_layout = cmds.columnLayout(columnWidth = subcategory_width, rowSpacing = row_spacing)#sub cat main column columnLayout
		self.titleText = cmds.text(label = self.title, align = 'left')
		if self.auto != '':
			cmds.popupMenu(parent = self.titleText, button = 3)
			cmds.menuItem(label = 'Run Auto', command = lambda *args: self.runAuto(self.subcatXML, self, auto = True))
			cmds.menuItem(label = 'Select Flagged', command = lambda *args: self.select_flagged())
		self.int_field_slider_row_layout = cmds.rowLayout(numberOfColumns = 2)#int_field_slider_row_layout
		self.grade_intField = cmds.intField( minValue=0, maxValue=150, step=1 , width = subcategory_width/6, changeCommand = lambda *args: self.update_subcategory('intField', *args))
		self.grade_slider = cmds.intSlider( min=-100, max=0, value=0, step=1, width = subcategory_width*5/6, changeCommand = lambda *args: self.update_subcategory('slider', *args), dragCommand = lambda *args: self.update_subcategory('slider', *args))
		cmds.setParent('..')
		self.radio_creator(self.subcatXML.find('gradeComment'))
		self.log('radios created, starting comment frames')
		self.subcat_comments_frame_layout = cmds.frameLayout( label='Comments', collapsable = True, collapse = True, width = subcategory_width)
		self.comments_text_field = cmds.scrollField(width = subcategory_width, height = scrollField_height, wordWrap = True,  changeCommand = lambda *args: self.update_subcategory('comments_text', *args))

		self.rmb_menu = cmds.popupMenu(parent = self.comments_text_field, button = 3)
			# i = 0
		if self.rmb != []:
			for item in self.rmb:
				self.log('{}:{}'.format(item[0], item[1]))
				cmds.menuItem(label = item[0], command = lambda args, i = item[1]:self.add_comment_to_comments(i))
				# i += 1
		cmds.menuItem(label = 'Append session comment', command = lambda *args: self.append_session_commment())

		cmds.button(label = 'Add Selected to Examples', width = subcategory_width, command = lambda *args: self.add_selected_to_examples(*args))
		self.example_frameLayout = cmds.frameLayout( label='Example Objects', collapsable = True, collapse = True, width = subcategory_width)
		self.example_comments = cmds.scrollField(width = subcategory_width, height = scrollField_height, wordWrap = True, changeCommand = lambda *args: self.update_subcategory('example_comments_text', *args))
		cmds.setParent('..')
		self.default_comments_frameLayout = cmds.frameLayout( label='Default Comments', collapsable = True, collapse = True, width = subcategory_width)
		self.default_comments = cmds.scrollField(width = subcategory_width, height = scrollField_height, wordWrap = True, changeCommand = lambda *args: self.update_subcategory('default_comments_text', *args))
		cmds.setParent('..')
		cmds.setParent('..')

		cmds.setParent('..')

	def select_flagged(self):
		self.log('select flagged!')
		if len(self.auto_flagged_list) == 0:
			cmds.warning('No objects in flagged list')
		else:
			self.log('selecting objects')
			cmds.select(self.auto_flagged_list)
			self.log('objects selected')
		
	def radio_creator(self, gradeComments):
		"""
		take the gradeComments element from the xml and create radio buttons labeled correctly
		"""
		labels = []
		# self.log('gradeComments are: %s' % gradeComments)
		for label in gradeComments:
			labels.append(label)
			# self.log('appending label: %s' % label)
		# self.log('labels: %s' % labels)
		cmds.rowLayout(numberOfColumns = len(labels)+1)
		self.grade_radio_collection = cmds.radioCollection()
		for label in labels:
			self.log('processing label: {}'.format(label.tag))
			tag = re.sub('plus', '+', label.tag)
			self.log('processed label: {}\n'.format(tag))
			cmds.radioButton(label = tag, changeCommand = lambda *args: self.update_subcategory('radioButton', *args), width = 30)

		##
		##
		self.resetRadioButton = cmds.radioButton(label = '.', visible = False)
		##
		##
		cmds.setParent('..')
		cmds.setParent('..')

	def gutCheck_update(self, intValue, *args):
		cmds.intField(self.grade_intField, edit = True, value = intValue)
		self.update_subcategory('intField')

	def update_subcategory(self, control_type, *args):
		"""
		trigger on element change command to update all the other fields in subcategory
		"""

		if control_type is 'intField':
			self.log('query intField and update others')
			intField_value = cmds.intField(self.grade_intField, query = True, value = True)
			self.log('intField is %s' % intField_value)

			self.current_grade_value = intField_value
			self.log('current grade is: %s' % self.current_grade_value)
			cmds.intSlider(self.grade_slider, edit=True, value = -intField_value)
			self.update_radios_default_comments(intField_value)
			self.update_default_comments()
			self.update_is_complete()
			self.updateFunction()

		elif control_type is 'slider':

			self.log('query slider and update others')
			slider_value = abs(cmds.intSlider(self.grade_slider, query = True, value = True))
			self.log('intSlider is %s' % slider_value)

			self.current_grade_value = slider_value
			self.log('current grade is: %s' % self.current_grade_value)
			cmds.intField(self.grade_intField, edit = True, value = slider_value)
			self.update_radios_default_comments(slider_value)
			self.update_default_comments()
			self.update_is_complete()
			self.updateFunction()

		elif control_type is 'radioButton':
			self.log('query radio collection and update others')
			selected = cmds.radioCollection(self.grade_radio_collection, query = True, select = True)
			selected_letter = cmds.radioButton(selected, query = True, label = True)
			selected_letter = re.sub('\\+', 'plus', selected_letter)
			self.log('selected radioButton: %s' % selected_letter)

			self.current_grade_value = int(self.grade_values.find(selected_letter).text)
			self.log('current grade is: %s' % self.current_grade_value)
			cmds.intField(self.grade_intField, edit = True, value = self.current_grade_value)
			cmds.intSlider(self.grade_slider, edit = True, value = -self.current_grade_value)
			self.log('selected_letter: %s' % selected_letter)
			
			cmds.scrollField(self.default_comments, edit = True, text = self.subcatXML.find('gradeComment').find(selected_letter).text)
			self.current_default_comment_text = cmds.scrollField(self.default_comments, query = True, text = True)
			self.log('Default Comments Updated')
			self.log(self.current_default_comment_text)
			self.update_is_complete()
			self.updateFunction()

		elif control_type is 'default_comments_text':
			self.current_default_comment_text = cmds.scrollField(self.default_comments, query = True, text = True)
			self.log('Default Comments Updated')
			self.log(self.current_default_comment_text)
			self.update_is_complete()

		elif control_type is 'example_comments_text':
			self.current_example_comment_text = cmds.scrollField(self.example_comments, query = True, text = True)
			self.log('examples updated')
			self.log(self.current_example_comment_text)

		else:
			self.current_comment_text = cmds.scrollField(self.comments_text_field, query = True, text = True)
			self.log('comments updated')
			self.log(self.current_comment_text)
	
	def update_radios_default_comments(self, value):
		"""
		take value and set radio buttons associated with that buttons
		"""
		self.log('set dim radios')

		grade_value_letter = ""
		do_break = False
		for g_value in self.grade_values:
			for g_comment in self.subcatXML.find('gradeComment'):
				if g_value.tag == g_comment.tag:
					grade_value_letter = g_value.tag
					if int(g_value.text) <= value:
						do_break = True
						break
			if do_break:
				break

		grade_value_letter = re.sub('plus', '+', grade_value_letter)
		radioButtons = cmds.radioCollection(self.grade_radio_collection, query = True, collectionItemArray = True)
		# print('grade_value_letter: {}'.format(grade_value_letter))
		for butn in radioButtons:
			# print('radio button to test: {}'.format(cmds.radioButton(butn, query=True, label = True)))
			if cmds.radioButton(butn, query=True, label = True) == grade_value_letter:
				# print('they match... should have selected it...?')
				cmds.radioButton(butn, edit = True, select = True)

	def update_default_comments(self):
		"""
		query grade values and update default comments accordingly

		SETS BASED ON RADIO BUTTONS. RADIO BUTTONS MUST BE UPDATED FIRST 
		"""
		self.log('update dim default comments')
		selected_letter = ''
		radioButtons = cmds.radioCollection(self.grade_radio_collection, query = True, collectionItemArray = True)
		for butn in radioButtons:
			if cmds.radioButton(butn, query=True, select = True):
				selected_letter = cmds.radioButton(butn, query = True, label = True)
				break
		if selected_letter == '':
			cmds.error('selected_letter not set.\n{}\nGrade Value: {}\n\n'.format(self.title, self.current_grade_value))

		# print('selected letter: {}'.format(selected_letter))
		if '+' in selected_letter:
			# print('plus detected!')
			# selected_letter = re.sub('+', 'plus', selected_letter)
			selected_letter = selected_letter.replace('+', 'plus')
			# print('new selected_letter: {}'.format(selected_letter))
		cmds.scrollField(self.default_comments, edit = True, text = self.subcatXML.find('gradeComment').find(selected_letter).text)

		self.current_default_comment_text = cmds.scrollField(self.default_comments, query = True, text = True)
		self.log('Default Comments Updated')
		self.log(self.current_default_comment_text)

	def append_session_commment(self):
		self.log('append session comment stuff')

		def close_command(*args):
			self.log('close command')
			# maya.utils.executeDeferred("cmds.deleteUI('ASCW')")

		def get_comment(*args):
			self.log('get comment')
			title = cmds.textField(comment_title, query = True, text = True)
			comment = cmds.scrollField(comment_text, query = True, text = True)
			self.log('\nTitle: {}\nComment: {}'.format(title, comment))
			if title != 'Comment Title' and comment != 'Type your comment text here...':
				cmds.menuItem(parent = self.rmb_menu, label = title, command = lambda args, i = comment:self.add_comment_to_comments(i))
				cmds.deleteUI('ASCW')
				reorder_comments()
			else:
				cmds.error('Type in a comment title and comment text to continue.\nClose the window to cancel.')
			self.add_comment_to_comments(comment)

		def reorder_comments(*args):
			self.log('reorder comments')
			comment_items = cmds.popupMenu(self.rmb_menu, query = True, itemArray = True)
			comment_items[-1], comment_items[-2] = comment_items[-2], comment_items[-1]
			comment_labels_commands = []
			for i in comment_items:
				l = cmds.menuItem(i, query = True, label = True)
				c = cmds.menuItem(i, query = True, command = True)
				comment_labels_commands.append((l,c))
			cmds.popupMenu(self.rmb_menu, edit = True, deleteAllItems = True)
			for i in comment_labels_commands:
				cmds.menuItem(label = i[0], command = i[1], parent = self.rmb_menu)



		self.log('make comment window')
		window_widthHeight = (250, 200)
		padding = 2

		#if ASCW window exists delete it
		if (cmds.window('ASCW', exists = True)):
			cmds.deleteUI('ASCW')

		comment_window = cmds.window('ASCW', title = 'Append Session Comment', 
									width = window_widthHeight[0], 
									height = window_widthHeight[1],
									closeCommand = close_command)
		comment_form = cmds.formLayout(numberOfDivisions = 250)
		comment_title = cmds.textField(text = 'Comment Title')
		comment_text = cmds.scrollField(editable = True, wordWrap = True, text = 'Type your comment text here...')
		comment_btn = cmds.button(label = 'Append Comment', command = get_comment)
		cmds.setParent('..')

		cmds.formLayout(comment_form, edit = True, attachForm = [
			(comment_title, 'left', padding),
			(comment_title, 'right', padding),
			(comment_title, 'top', padding),
			(comment_text, 'left', padding),
			(comment_text, 'right', padding),
			(comment_btn, 'left', padding), 
			(comment_btn, 'right', padding), 
			(comment_btn, 'bottom', padding)], 
			attachControl = [
			(comment_text, 'top', padding, comment_title),
			(comment_text, 'bottom', padding, comment_btn)])
		cmds.showWindow(comment_window)
	 
	def add_comment_to_comments(self, comment, *args):
		self.log('add comment to comments')
		text_bucket = cmds.scrollField(self.comments_text_field, query = True, text = True)
		# self.log('index: {}'.format(index))
		self.log('RMB: {}'.format(self.rmb))
		text_bucket += ' {}'.format(comment)
		cmds.scrollField(self.comments_text_field, edit = True, text = text_bucket)

		self.update_subcategory('comments_text')

	def add_selected_to_examples(self, *args):
		"""
		add selected objects to the example text fields
		"""
		self.log('Boom. Adding Selected to examples')
		text_bucket = ''
		selection = cmds.ls(selection = True, long = True)
		self.log('selection is: %s' % selection)
		text_bucket = cmds.scrollField(self.example_comments, query = True, text = True)
		if text_bucket:
			self.log('text_bucket is TRUE:: %s' % text_bucket)
			for selected in selection:
				text_bucket += ( ", " + selected)
		else:
			for selected in selection:
				text_bucket += (selected + ', ')
			text_bucket = text_bucket.rstrip(', ')

		cmds.scrollField(self.example_comments, edit = True, text = text_bucket)



		self.update_subcategory('example_comments_text')

	def update_is_complete(self, reset = False):
		self.log('updating "is_complete"')
		if reset:
			self.is_complete = False
			self.log('is_complete: reset')
		elif self.current_grade_value is 0 and self.current_default_comment_text is '':
			self.is_complete = False
			self.log('not complete')
		else:
			self.is_complete = True
			self.log('is_complete now TRUE')

	def what_is_the_grade(self):
		"""
		collect grade from subcategory and return
		"""
		return_dict = {
			'section_title': self.title, 
			'section_weight': self.weight,
			'grade_value' : self.current_grade_value,
			'comment_text' : self.current_comment_text,
			'default_comments_text' : self.current_default_comment_text,
			'example_comments_text' : self.current_example_comment_text,
			'is_complete': self.is_complete
		}

		return return_dict

	def this_is_the_grade(self, grade_to_set):
		"""
		take an input dictionary and populate all the grade fields accordingly
		"""

		cmds.intField(self.grade_intField, edit = True, value = grade_to_set['grade_value'])
		self.update_subcategory('intField')
		if grade_to_set['grade_value'] is not '':
			cmds.scrollField(self.comments_text_field, edit = True, text = grade_to_set['comment_text'])
			self.update_subcategory('comments_text')
		if grade_to_set['default_comments_text'] is not '':	
			cmds.scrollField(self.default_comments, edit = True, text = grade_to_set['default_comments_text'])
			self.update_subcategory('default_comments_text')
		if grade_to_set['example_comments_text'] is not '':
			cmds.scrollField(self.example_comments, edit = True, text = grade_to_set['example_comments_text'])
			self.update_subcategory('example_comments_text')

		self.auto_flagged_list = grade_to_set.get('examples', [])
		self.log('auto_flagged_list updated: \n{}'.format(self.auto_flagged_list))

	def reset(self):
		cmds.intField(self.grade_intField, edit = True, value = 0)
		self.update_subcategory('intField')
		cmds.scrollField(self.comments_text_field, edit = True, text = '')
		self.update_subcategory('comments_text')
		cmds.scrollField(self.default_comments, edit = True, text = '')
		self.update_subcategory('default_comments_text')
		cmds.scrollField(self.example_comments, edit = True, text = '')
		self.update_subcategory('example_comments_text')
		self.log('reset subsection: {}'.format(self.title))
		self.log('Selection hidden radio')
		cmds.radioButton(self.resetRadioButton, edit = True, select = True)
		self.log('hidden radio selected')
		self.is_complete = False
		#collapse frames
		cmds.frameLayout(self.subcat_comments_frame_layout, edit = True, collapse = True)
		cmds.frameLayout(self.example_frameLayout, edit = True, collapse = True)
		cmds.frameLayout(self.default_comments_frameLayout, edit = True, collapse = True)

	def update(self):
		self.current_grade_value = cmds.intField(self.grade_intField, query = True, value = True)
		self.current_default_comment_text = cmds.scrollField(self.default_comments, query = True, text = True)
		self.current_example_comment_text = cmds.scrollField(self.example_comments, query = True, text = True)
		self.current_comment_text = cmds.scrollField(self.comments_text_field, query = True, text = True)

	def disable(self):
		cmds.columnLayout(self.subcat_main_column_layout, edit = True, enable = False)

	def enable(self):
		cmds.columnLayout(self.subcat_main_column_layout, edit = True, enable = True)

	def log(self, message, prefix = '.:subcategory_class::', hush = True):
		"""
		print stuff yo!
		"""
		if not hush:
			print "%s: %s" % (prefix, message)

class MainCategoryGradeSection(object):

	def __init__(self, mainCategoryFromXML, defaultsFromXML, updateFunction):

		maincategory_width = 200
		scrollField_height = 100
		row_spacing = 0

		self.current_highnote_comment_text = ''
		self.current_grade_value = 0 

		self.updatePGS = updateFunction


		self.log("Main Category Initializing")
		self.maincategory = mainCategoryFromXML
		self.defaults = defaultsFromXML

		self.log('\n\nGutCheck:')
		self.gutCheck = None
		
		if self.maincategory.find('gutCheck') is not None:
			self.gutCheck = self.maincategory.find('gutCheck').text
		self.log('{}\n\n'.format(self.gutCheck))

		self.rmb = []
		if self.maincategory.findall('RMB'):
			for item in self.maincategory.findall('RMB'):
				self.rmb.append([item.get('title'), item.text])

		self.log('\nRiGHT HERE!')
		if self.rmb != []:
			for item in self.rmb:
				self.log('\nTitle: {}\n{}'.format(item[0], item[1]))
		self.log('RMB: {}'.format(self.rmb))
		
		self.title = self.maincategory.get('title')
		if self.title == None:
			self.title = self.maincategory.find('title').text

		self.weight = self.maincategory.get('weight')
		if self.weight == None:
			self.weight = self.maincategory.find('weight').text
			
		# self.title = self.maincategory.find('title').text
		# self.weight = self.maincategory.find('weight').text
		self.log('{} Category Weight: {}'.format(self.title, self.weight))
		self.maincat_main_column_layout = cmds.columnLayout(columnWidth = maincategory_width, rowSpacing = row_spacing, enable = False)#main cat main column columnLayout
		self.mainFrameLayout = cmds.frameLayout(label = 'High Notes',collapsable = True, collapse = True, width = maincategory_width)
		if self.gutCheck == 'True':
			self.log('running gut check GUI stuff')
			self.gutCheckFrameLayout = cmds.frameLayout(label = 'Gut Check', collapsable = True, collapse = True, width = maincategory_width)
			self.gutCheckWindowGo()
			cmds.setParent(self.mainFrameLayout)

		self.highnote_comments = cmds.scrollField(width = maincategory_width, height = scrollField_height, wordWrap = True, changeCommand = lambda *args: self.update_maincategory('highnotes', *args))

		self.rmb_menu = cmds.popupMenu(parent = self.highnote_comments, button = 3)
			# i = 0
		if self.rmb != []:
			for item in self.rmb:
				self.log('{}:{}'.format(item[0], item[1]))
				cmds.menuItem(label = item[0], command = lambda args, i = item[1]:self.add_comment_to_comments(i))
				# i += 1
		cmds.menuItem(label = 'Append session comment', command = lambda *args: self.append_session_commment())

		cmds.setParent(self.mainFrameLayout)
		cmds.setParent(self.maincat_main_column_layout)

		subcatColumnLayout = cmds.columnLayout()
		self.subcategories = []#this will be the subcategory object
		# self.log('maincategory: %s' % self.maincategory.find('title').text)
		self.log('main category title: %s' % self.title)
		self.subcats = self.maincategory.findall('subcategory') #this is the xml subcategory
		self.log('subcategories found: %s' % self.subcats)
		# for subc in self.subcats:
		# 	self.log('subcat: %s' % subc)
		# 	self.log('title: %s' % subc.find('title').text)

		
		for sub in self.subcats:
			self.subcategories.append(SubcategoryGradeSection(sub, self.defaults, self.updatePGS, self.runAuto))
			cmds.setParent(subcatColumnLayout)

		
		cmds.setParent(self.maincat_main_column_layout)

	def append_session_commment(self):
		self.log('append session comment stuff')

		def close_command(*args):
			self.log('close command')
			# maya.utils.executeDeferred("cmds.deleteUI('ASCW')")

		def get_comment(*args):
			self.log('get comment')
			title = cmds.textField(comment_title, query = True, text = True)
			comment = cmds.scrollField(comment_text, query = True, text = True)
			self.log('Title: {}\nComment: {}'.format(title, comment))
			if title != 'Comment Title' and comment != 'Type your comment text here...':
				cmds.menuItem(parent = self.rmb_menu, label = title, command = lambda args, i = comment:self.add_comment_to_comments(i))
				cmds.deleteUI('ASCW')
			else:
				cmds.error('Type in a comment title and comment text to continue.\nClose the window to cancel.')

		self.log('make comment window')
		window_widthHeight = (250, 200)
		padding = 2

		#if ASCW window exists delete it
		if (cmds.window('ASCW', exists = True)):
			cmds.deleteUI('ASCW')

		comment_window = cmds.window('ASCW', title = 'Append Session Comment', 
									width = window_widthHeight[0], 
									height = window_widthHeight[1],
									closeCommand = close_command)
		comment_form = cmds.formLayout(numberOfDivisions = 250)
		comment_title = cmds.textField(text = 'Comment Title')
		comment_text = cmds.scrollField(editable = True, wordWrap = True, text = 'Type your comment text here...')
		comment_btn = cmds.button(label = 'Append Comment', command = get_comment)
		cmds.setParent('..')

		cmds.formLayout(comment_form, edit = True, attachForm = [
			(comment_title, 'left', padding),
			(comment_title, 'right', padding),
			(comment_title, 'top', padding),
			(comment_text, 'left', padding),
			(comment_text, 'right', padding),
			(comment_btn, 'left', padding), 
			(comment_btn, 'right', padding), 
			(comment_btn, 'bottom', padding)], 
			attachControl = [
			(comment_text, 'top', padding, comment_title),
			(comment_text, 'bottom', padding, comment_btn)])
		cmds.showWindow(comment_window)
	 
	def add_comment_to_comments(self, comment, *args):
		self.log('add comment to comments')
		text_bucket = cmds.scrollField(self.highnote_comments, query = True, text = True)
		# self.log('index: {}'.format(index))
		self.log('RMB: {}'.format(self.rmb))
		text_bucket += ' {}'.format(comment)
		cmds.scrollField(self.highnote_comments, edit = True, text = text_bucket)

		self.update_maincategory('highnotes')

	def enable(self):
		self.log('enable the section')
		cmds.columnLayout(self.maincat_main_column_layout, edit = True, enable = True)
		for sub in self.subcategories:
			sub.enable()

	def disable(self):
		self.log('disable the section')
		cmds.columnLayout(self.maincat_main_column_layout, edit = True, enable = False)
		for sub in self.subcategories:
			sub.disable()
		self.log('did it work?')

	def gutCheckGo(self, *args):
		self.log('gut check')
		self.disable()
		self.gutCheckWindowGo()

	def gutCheckWindowGo(self, *args):
		self.log('gut check window')

		elem_width = 200
		row_spacing = 0
		# self.gutCheckWindowElement = cmds.window(title = '{} Gut Check'.format(self.title), width = 215, height = 100, closeCommand = self.gutCheckCancel)

		self.gutCheckWindow = cmds.columnLayout(columnWidth = elem_width, rowSpacing = row_spacing)
		cmds.text(label = 'Gut Check Input', align = 'left')
		
		gutCheck_int_field_slider_row_layout = cmds.rowLayout(numberOfColumns = 2)#int_field_slider_row_layout
		self.gutCheck_grade_intField = cmds.intField( minValue=0, maxValue=150, step=1 , width = elem_width/6, 
			changeCommand = lambda *args: self.gutCheck_update('field'))
		self.gutCheck_grade_slider = cmds.intSlider( min=-100, max=0, value=0, step=1, width = elem_width*5/6, changeCommand = lambda *args: self.gutCheck_update('slider'), dragCommand = lambda *args: self.gutCheck_update('slider'))
		cmds.setParent('..')

		cmds.button(label = 'Commit', command = self.gutCheckSet, width = elem_width)
		cmds.setParent('..')
		
		# cmds.showWindow(self.gutCheckWindowElement)

	def gutCheck_update(self, controlType):
		self.log('gut check update')
		if controlType == 'slider':
			value = cmds.intSlider(self.gutCheck_grade_slider, query = True, value = True)
			cmds.intField(self.gutCheck_grade_intField, edit = True, value = -value)
		elif controlType == 'field':
			value = cmds.intField(self.gutCheck_grade_intField, query = True, value = True)
			cmds.intSlider(self.gutCheck_grade_slider, edit = True, value = -value)

	def gutCheckSet(self, *args):
		self.log('gut check set')
		value = cmds.intField(self.gutCheck_grade_intField, query = True, value = True)
		for sub in self.subcategories:
			sub.gutCheck_update(value)
		# cmds.deleteUI(self.gutCheckWindowElement)
		# self.enable()
		self.gutCheckReset()

	def gutCheckReset(self, *args):
		self.log('gut check reset!')
		cmds.intField(self.gutCheck_grade_intField, edit = True, value = 0)
		self.gutCheck_update('field')
		cmds.frameLayout(self.gutCheckFrameLayout, edit = True, collapse = True)
		cmds.frameLayout(self.mainFrameLayout, edit = True, collapse = True)

	def gutCheckCancel(self, *args):
		self.log('gut check cancel')
		# cmds.deleteUI(self.gutCheckWindowElement)
		self.enable()

	def autoProGo(self):
		self.log('defaults: {}'.format(self.defaults))
		self.log('defaults.findall("auto"): {}'.format(self.defaults.findall('auto')[0]))
		self.log('!!! autoText: {}'.format(self.defaults.findall('auto')[0].text))
		if self.defaults.findall('auto')[0].text :
			for sub in self.subcategories:
				try:
					self.runAuto(self.defaults, sub)
				except RuntimeError as e:
					cmds.warning('Error running automation. Skipping section: {}\n{}'.format(sub.title, e))

			self.updatePGS()

	def runAuto(self, defaultsFromXML, single_subcat, auto = False):
		# this section handles all the automation linking on the subcategories
		subcatXMLElement = single_subcat.subcatXML
		if not auto:
			try:
				self.log("Lets try")
				self.log(defaultsFromXML.find('auto').text)
				self.log('subcatXMLElement:')
				sub_title1 = subcatXMLElement.get('title')
				if sub_title1 == None:
					sub_title1 = subcatXMLElement.find('title').text
				self.log('subcat title: %s' % sub_title1) 
				# self.log(subcatXMLElement.find('auto').text)
				self.log("did those last two print?")
				subcat_auto = None
				if subcatXMLElement.find('auto') != None:
					subcat_auto = subcatXMLElement.find('auto').text
				if subcat_auto == '' or subcat_auto == None:
					subcat_auto = False
				if (defaultsFromXML.find('auto').text == 'True') and subcat_auto:
					self.log('auto.text is %s' % subcatXMLElement.find('auto').text)
					auto = True
			except AttributeError as e:
				self.log('AttributeError for Auto test: \n{}'.format(e))
				# cmds.warning('AttributeError: {}'.format(sys.exc_info()[2].tb_lineno))
				cmds.warning('AttributeError: {}: Line {}'.format(e,sys.exc_info()[2].tb_lineno))
				pass

		if auto:
			self.log(subcatXMLElement.find('auto').text)
			autoScriptName = subcatXMLElement.find('auto').text
			self.log('auto is True!!!')
			import pabuito_auto as autoRun
			# reload(autoRun)
			# autoScripts = dir(autoRun)
			folder_name = defaultsFromXML.find('auto').get('folder')
			if folder_name != None:
				autoRun = getattr(autoRun, folder_name)
			autoScripts = dir(autoRun)
			self.log('Methods in auto run are \n %s' % autoScripts)
			defaultMethods = defaultsList = ['__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__']
			autoScriptModules = []
			for method in autoScripts:
				if method not in defaultMethods:
					autoScriptModules.append(method)
			self.log('autoScriptModules: %s' % autoScriptModules)
			self.log('autoScriptName: %s' % autoScriptName)

			# print('auoScriptModules:')
			# for mod in autoScriptModules:
			# 	print(mod)
				
			if autoScriptName in autoScriptModules:
				self.log('Found AutoScript!')
				returnDict = getattr(getattr(autoRun, autoScriptName), autoScriptName)(self.defaults)
				self.log(returnDict)
				sub_title = subcatXMLElement.get('title')
				if sub_title == None:
					sub_title = subcatXMLElement.find('title').text
				returnDict['section_title'] = sub_title
				self.log('section_title: %s' % returnDict['section_title'])
				single_subcat.this_is_the_grade(returnDict)
			else:
				self.log('Failed to find autoScriptName')
				cmds.warning('Failed to find autoScriptName: {}'.format(autoScriptName))

		else:
			self.log('FALSE FALSE FALSE')

	def update_maincategory(self, section, *args):
		self.log('updating %s' % section)
		if section is 'highnotes':
			self.current_highnote_comment_text = cmds.scrollField(self.highnote_comments, query = True, text = True)

	def update(self):
		self.current_highnote_comment_text = cmds.scrollField(self.highnote_comments, query = True, text = True)
		for subcat in self.subcategories:
			subcat.update()

	def check_grade_status(self):
		self.log('checking %s section grade status' % self.title)
		currentGrade = 0
		catWeightAndValue = []
		for subcat in self.subcategories:
			catWeightAndValue.append((subcat.weight, subcat.current_grade_value))
		for cat in catWeightAndValue:
			currentGrade += ((float(cat[0])/100)*float(cat[1]))
		return (self.title, self.weight, currentGrade)

	def what_is_the_grade(self):
		self.log('collect grades from subsections')
		return_list = []
		return_list.append(self.title)
		return_list.append(self.weight)
		return_list.append(self.current_highnote_comment_text)
		sectionGradeTotal = 0
		subGradeList = []
		for sub in self.subcategories:
			subGradeList.append(sub.what_is_the_grade())
			self.log('Grade weight and value: {} * {}'.format(sub.what_is_the_grade()['grade_value'], sub.what_is_the_grade()['section_weight']))
			sectionGradeTotal += (sub.what_is_the_grade()['grade_value'] * (float(sub.what_is_the_grade()['section_weight'])/100.0))
		return_list.append(sectionGradeTotal)
		return_list.append(subGradeList)
		return return_list

	def this_is_the_grade(self, gradeList):
		sectionGrades = gradeList
		i = 0
		for item in sectionGrades:
			self.log('index {} of sectionGrades: {}'.format(i, item))
			i+=1
		self.log('\n\nStill needs to set high notes\n\n')
		cmds.scrollField(self.highnote_comments, edit = True, text = sectionGrades[2])
		self.update_maincategory('highnotes')
		self.log('section[3]:\n{}'.format(sectionGrades[4]))
		for sub in self.subcategories:
			for index in sectionGrades[4]:
				if sub.title is index['section_title']:
					sub.this_is_the_grade(index)

	def are_you_complete(self):
		incomplete_titles = []
		for sub in self.subcategories:
			self.log("Testing sub for complete-ness: %s" % sub.title)
			if not sub.is_complete:
				self.log('adding {} to incomplete_titles'.format(sub.title))
				incomplete_titles.append(sub.title)
				# return False
		self.log('incomplete_titles: \n{}'.format(incomplete_titles))
		return incomplete_titles
		# return True
	
	def reset(self):
		self.log('resetting main section')
		cmds.scrollField(self.highnote_comments, edit = True, text = '')
		cmds.frameLayout(self.mainFrameLayout, edit = True, collapse = True)
		# self.disable()
		for sub in self.subcategories:
			sub.reset()
		self.update_maincategory('highnotes')
		self.log('Main section {} reset'.format(self.title))

	def log(self, message, prefix = '.:main_category_class::', hush = True):
		"""
		print stuff yo!
		"""
		if not hush:
			print "%s: %s" % (prefix, message)