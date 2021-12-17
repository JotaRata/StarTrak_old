import os
import os.path
from sys import version
from STCore import debug
from STCore.classes.items import Language

__langs = {}


def register_languages():
	dir = 'STCore/lang'

	def check_folder():
		return os.path.isdir(dir) and len(os.listdir(dir)) > 0

	# ----------------------------------
	def read_header(file: str):
		language = Language(file)
		error_msg = 'The file \"{0}\" could not be loaded: '.format(file)
		with open(file, 'r') as f:
			count = 0
			start_line = 64
			end_line = 64
			error = None
			while True:
				line = f.readline().strip()
				# Ignore comments
				if line[0] == '#':
					continue
				if count < start_line:
					if line[:6] == 'HEADER':
						if '{' in line[6:]:
							start_line = count
						else:
							error = 'invalid header'
							break
				else:
					eq_index = -1
					if line[0] == '\t' or line[0] == ' ':
						line = line.expandtabs().replace(' ', '').lower()
						try:
							eq_index = line.index('=')
						except:
							error = 'invalid syntax'
							break
						if line[:eq_index] == 'id':
							language.id = line[eq_index:]
						elif line[:eq_index] == 'name':
							language.name = line[eq_index:]
						elif line[:eq_index] == 'version':
							language.version = line[eq_index:]
						else:
							error = 'invalid key \"{0}\"'.format(line[:eq_index])
							break
					else:
						error = 'iconsistent indentation'
						break
					# End reading of rile
					if '}' in line:
						end_line = count
						lang.header_end = end_line
						break
					else:
						error = 'invalid syntax'
						break
				if count >= 64:
					error = 'max header size of 64'
				count += 1
			if error is None:
				return language
			else:
				debug.warn(__name__, error_msg+error+'@'+str(count))

	# ----------------------------------
	if not check_folder():
		debug.error(__name__, 'No languages have been found in folder ./lang/')
		return
	for file in os.listdir(dir):
		lang = read_header(file)
		if lang is not None:
			__langs[lang.id] = lang

	if len(__langs) == 0:
		debug.error(
			__name__, "'No valid language files have been found in folder ./lang/'")


def load_language(id: str):
	def read_file(file: str, line_offset: int):
		_dict = {}
		with open(file, "r") as f:
			lines = f.readlines()
			for index, line in enumerate(lines[line_offset:]):
				keyval = line.split('=')
				if len(keyval) == 2:
					key = keyval[0].lower()
					val = keyval[1]

					if ' ' in key:
						debug.warn(
							__name__, 'Invalid syntax: \"{0}\" @{1}:{2}'.format(line, file, index))
						continue
					_dict[key] = val
				else:
					debug.warn(
						__name__, 'Invalid expression: \"{0}\" @{1}:{2}'.format(line, file, index))
					continue
		return _dict

	if id not in __langs:
		debug.error(
			__name__, 'Language pack \"{0}\" doesn\'t exist', format(id))

	language: Language = __langs[id]
	keywords = read_file(language.filepath, language.header_end)
	if len(keywords) == 0:
		debug.error(
			__name__, 'Invalid language pack \"{0}\"', format(id))

	language.dictionary = keywords
	__langs[id] = language
