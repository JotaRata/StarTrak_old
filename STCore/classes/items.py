from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from genericpath import getmtime, getsize
from posixpath import basename, splitext
from sys import path, version
from time import gmtime, strptime, struct_time
from warnings import simplefilter
from astropy.io import fits

from astropy.io.fits import header
from numpy import ndarray
from tkinter import Variable

from STCore import debug

CURRENT_VERSION = 2
#----------------------------------
class TrackState(Enum):
	"ACTIVE", 
	"INACTIVE", 
	"LOST", 
	"RUNNING"
#--------------------------------------------------
@dataclass
class Item(ABC):
	name 	: str
	version = 2
	
	def printd(self):
		print(f'{self.name} Item info:')
		print(self.__dict__)
#--------------------------------------------------
@dataclass
class File(Item):
	path 	: str
	simple 		  = True
	relative_path = False
	date_kw		  = 'DATE-OBS'

	def __post_init__(self):
		self.size = self.size_from_file(self.path)
		self.load_header()
		if not self.simple:
			self.load_data()
		
		if self.date_kw in self.header:
			self.date = self.date_from_header()
		else:
			self.date = self.date_from_file()
			debug.warn(self.name, "The key {0} doesn't exist in header, using creation time instead".format(self.date_kw))
		self.active = True
		self.version = 2
	def load_header(self):
			try:
				self.header = fits.getheader(self.path)
			except:
				debug.warn(self.path, "Couldn't read header from file: {0} ".format(self.path))
				self.header = header.Header([])
	def load_data(self):
		try:
			self.data = fits.getdata(self.path)
			self.simple = False
		except:
			debug.error(self.path, "Couldn't read data from file: {0}. File corrupt or invalid".format(self.path), stop=False)
			self.active = False
	def exists(self):
		from os.path import  isfile
		return isfile(self.path)
	def date_from_file(self):
		return gmtime(getmtime(self.path))
	def size_from_file(self, filepath):
		return getsize(filepath) >> 20
	def date_from_header(self):
		return strptime(self.header[self.date_kw], "%Y-%m-%dT%H:%M:%S.%f")
#--------------------------------------------------
@dataclass
class Star(Item):
	name : str
	location : tuple
	guide 				= False
	sample : ndarray	= None
	size : int			= 16
	bounds : int		= 60
	bkg_samples : tuple = None
	bkg_size : int		= 4
#--------------------------------------------------
@dataclass
class Track(Item):	
	state : TrackState 
	star : Star
	locations : list	= None
	values : list		= None
	losses : int		= 0

#--------------------------------------------------
@dataclass
class Setting(object):
	value 	: Variable
	group 	: str
	name 	:	 str
	default : object

	def set(self, value):
		self.value.set(value = value)
	def get(self):
		return self.value.get()
#--------------------------------------------------
@dataclass
class Language(object):
	filepath	: str
	id 			= ""
	name 		= ""
	version 	= -1
	dictionary  = None
	header_end 	= 0

	def __getitem__(self, key: str) -> str:
		if key in self.dictionary:
			return self.dictionary[key]
		else:
			return key

	def printd(self):
		print(self.id, self.name, self.version, self.header_end, self.dictionary)

	def validate(self):
		path_complete = False
		id_complete = False
		name_complete = False
		version_complete = False
		header_complete = False
		if self.filepath is not None:
			if len(self.filepath) > 0:
				path_complete = True
		if len(self.id) >= 2:
			id_complete = True
		if len(self.name) >= 3:
			name_complete = True
		if self.version >= 0:
			version_complete = True
		if self.header_end > 0:
			header_complete = True
		return path_complete and id_complete and name_complete and version_complete and header_complete
